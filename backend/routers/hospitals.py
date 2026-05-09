"""Hospital recommendation router with multi-ring support and Overpass API fallback."""
import time
import math
import requests
from typing import List, Tuple, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException
from backend.schemas.schemas import HospitalRequest, HospitalResponse, LocationResponse, HospitalInfo
from backend.services.hospital_recommender import reverse_geocode
from backend import config

router = APIRouter(prefix="/api", tags=["Hospitals"])

# Simple in-memory cache for API results
_CACHE: Dict[str, Tuple[float, Any]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour


def _get_cache(key: str) -> Optional[Any]:
    if key in _CACHE:
        expiry, data = _CACHE[key]
        if time.time() < expiry:
            return data
        else:
            del _CACHE[key]
    return None


def _set_cache(key: str, data: Any):
    _CACHE[key] = (time.time() + CACHE_TTL_SECONDS, data)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km using Haversine formula."""
    R = 6371  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def deduplicate_hospitals(hospitals: List[HospitalInfo]) -> List[HospitalInfo]:
    """Remove duplicates based on hospital name and rounded coordinates."""
    unique = []
    seen = set()
    for h in hospitals:
        # Key: name (lowercase) + lat/lon rounded to 3 decimals (~110 meters)
        key = f"{h.name.lower()}_{round(h.latitude, 3)}_{round(h.longitude, 3)}"
        if key not in seen:
            seen.add(key)
            unique.append(h)
    
    # Sort by distance
    return sorted(unique, key=lambda x: x.distance_km)


def search_geoapify_ring(lat: float, lon: float, radius_km: float, api_key: str) -> List[HospitalInfo]:
    """Single API call to Geoapify for a specific radius."""
    radius_m = int(radius_km * 1000)
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "healthcare.hospital",
        "filter": f"circle:{lon},{lat},{radius_m}",
        "bias": f"proximity:{lon},{lat}",
        "limit": 50,  # Maximize results per ring
        "apiKey": api_key
    }
    
    resp = requests.get(url, params=params, timeout=15)
    
    if resp.status_code == 429:
        raise Exception("rate_limit")
        
    if resp.status_code != 200:
        print(f"[Geoapify] Error {resp.status_code}: {resp.text}")
        return []
        
    hospitals = []
    data = resp.json()
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        h_lat = props.get("lat", 0)
        h_lon = props.get("lon", 0)
        
        if h_lat == 0 and h_lon == 0:
            continue
            
        dist = props.get("distance", 0) / 1000.0
        if dist == 0:
            dist = calculate_distance(lat, lon, h_lat, h_lon)
            
        name = props.get("name", "Unknown Hospital")
        if not name:
            name = "Unknown Hospital"
            
        address = props.get("address_line2", props.get("formatted", "Address not available"))
        
        hospitals.append(HospitalInfo(
            name=name,
            address=address,
            city=props.get("city"),
            latitude=h_lat,
            longitude=h_lon,
            distance_km=round(dist, 2),
            specialties=["general"],
            phone=props.get("contact", {}).get("phone")
        ))
        
    return hospitals


def search_geoapify_multiple(lat: float, lon: float, max_radius_km: float, api_key: str) -> Tuple[List[HospitalInfo], int, bool]:
    """Make multiple Geoapify calls in 10km increments."""
    all_hospitals = []
    calls_made = 0
    rate_limit_hit = False
    
    # Determine the step increments (10km chunks)
    steps = int(math.ceil(max_radius_km / 10.0))
    if steps == 0:
        steps = 1
        
    for i in range(1, steps + 1):
        ring_radius = float(i * 10)
        if ring_radius > max_radius_km:
            ring_radius = max_radius_km
            
        try:
            print(f"[Geoapify] Querying ring radius: {ring_radius}km")
            ring_results = search_geoapify_ring(lat, lon, ring_radius, api_key)
            all_hospitals.extend(ring_results)
            calls_made += 1
            
            # Delay to avoid hammering the API
            if i < steps:
                time.sleep(0.5)
        except Exception as e:
            if str(e) == "rate_limit":
                print("[Geoapify] Rate limit exceeded during multi-ring search.")
                rate_limit_hit = True
                break
            else:
                print(f"[Geoapify] Exception in multi-ring search: {e}")
                
    unique_hospitals = deduplicate_hospitals(all_hospitals)
    print(f"[Geoapify] Total unique hospitals found: {len(unique_hospitals)} across {calls_made} calls.")
    return unique_hospitals, calls_made, rate_limit_hit


def search_overpass(lat: float, lon: float, radius_km: float) -> List[HospitalInfo]:
    """Fallback to OpenStreetMap Overpass API (unlimited radius)."""
    print(f"[Overpass] Querying Overpass API for radius {radius_km}km")
    radius_m = int(radius_km * 1000)
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Overpass QL query searching for hospitals around the coordinate
    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      way["amenity"="hospital"](around:{radius_m},{lat},{lon});
      relation["amenity"="hospital"](around:{radius_m},{lat},{lon});
    );
    out center;
    """
    
    try:
        headers = {"User-Agent": "HealthIntel/1.0"}
        resp = requests.get(overpass_url, params={'data': query}, headers=headers, timeout=35)
        if resp.status_code != 200:
            print(f"[Overpass] Error {resp.status_code}: {resp.text}")
            return []
            
        data = resp.json()
        hospitals = []
        
        for element in data.get("elements", []):
            if element["type"] == "node":
                h_lat = element["lat"]
                h_lon = element["lon"]
            else: # way or relation
                center = element.get("center", {})
                h_lat = center.get("lat", 0)
                h_lon = center.get("lon", 0)
                
            if h_lat == 0 and h_lon == 0:
                continue
                
            dist = calculate_distance(lat, lon, h_lat, h_lon)
            if dist > radius_km:
                continue
                
            tags = element.get("tags", {})
            name = tags.get("name", "Unknown Hospital")
            if name == "Unknown Hospital" and "name:en" in tags:
                name = tags["name:en"]
                
            street = tags.get("addr:street", "")
            city = tags.get("addr:city", "")
            
            address_parts = [p for p in [street, city] if p]
            address = ", ".join(address_parts) if address_parts else "Address not available"
            
            hospitals.append(HospitalInfo(
                name=name,
                address=address,
                city=city or None,
                latitude=h_lat,
                longitude=h_lon,
                distance_km=round(dist, 2),
                specialties=["general"],
                phone=tags.get("phone") or tags.get("contact:phone")
            ))
            
        unique_hospitals = deduplicate_hospitals(hospitals)
        print(f"[Overpass] Found {len(unique_hospitals)} hospitals.")
        return unique_hospitals
        
    except Exception as e:
        print(f"[Overpass] Exception during query: {e}")
        return []


@router.post("/recommend-hospitals", response_model=HospitalResponse)
def recommend_hospitals(request: HospitalRequest):
    """
    1. Always search local CSV database first (now populated with 7900+ hospitals).
    2. Supplement with Geoapify/Overpass only if needed.
    """
    from backend.services.hospital_recommender import _query_local_database
    
    lat = request.latitude
    lon = request.longitude
    radius_km = request.radius_km
    disease_category = request.disease_category
    
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
        
    # Check Cache
    cache_key = f"hosp_multiring_{round(lat, 3)}_{round(lon, 3)}_{radius_km}"
    cached = _get_cache(cache_key)
    if cached:
        cached["source"] += " (cached)"
        return HospitalResponse(**cached)

    calls_made = 0
    source = "local_database"
    
    # Load disease specialties
    disease_config = config.load_disease_config()
    specialties = disease_config.get(disease_category, {}).get("specialties", [])
    
    # 1. ALWAYS query local CSV database first
    hospitals = _query_local_database(lat, lon, radius_km, specialties)
    
    api_key = config.GEOAPIFY_API_KEY
    
    # 2. Supplement if we have very few results (less than 5)
    if len(hospitals) < 5:
        if api_key and radius_km <= 60.0:
            api_hospitals, calls, rate_limit_hit = search_geoapify_multiple(lat, lon, radius_km, api_key)
            calls_made += calls
            hospitals.extend(api_hospitals)
            source = "local+geoapify"
            
            if rate_limit_hit and len(hospitals) < 5:
                overpass_hospitals = search_overpass(lat, lon, radius_km)
                hospitals.extend(overpass_hospitals)
                source = "local+geoapify+overpass"
                calls_made += 1
        else:
            overpass_hospitals = search_overpass(lat, lon, radius_km)
            hospitals.extend(overpass_hospitals)
            source = "local+overpass"
            calls_made += 1
            
    # Deduplicate after combining
    hospitals = deduplicate_hospitals(hospitals)

    result = {
        "hospitals": hospitals,
        "radius_used_km": radius_km,
        "total_found": len(hospitals),
        "source": source,
        "calls_made": calls_made,
        "location": {
            "latitude": lat,
            "longitude": lon
        }
    }
    
    # Cache the result
    _set_cache(cache_key, result)
    
    return HospitalResponse(**result)


@router.get("/reverse-geocode", response_model=LocationResponse)
async def get_reverse_geocode(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):
    """Reverse geocode a location to get city, state, and country."""
    result = reverse_geocode(lat, lon)
    return LocationResponse(**result)
