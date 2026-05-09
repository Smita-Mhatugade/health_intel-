"""Hospital Recommendation Engine using Geoapify and OpenStreetMap Nominatim."""
import math
import time
import pandas as pd
import requests
from typing import List, Optional, Tuple, Dict, Any
from backend.schemas.schemas import HospitalInfo
from backend import config

# Simple in-memory cache
# Format: { cache_key: (expiry_timestamp, data) }
_CACHE: Dict[str, Tuple[float, Any]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour

def _get_cache(key: str) -> Optional[Any]:
    """Retrieve item from cache if it exists and is not expired."""
    if key in _CACHE:
        expiry, data = _CACHE[key]
        if time.time() < expiry:
            return data
        else:
            del _CACHE[key]
    return None

def _set_cache(key: str, data: Any):
    """Store item in cache with 1-hour TTL."""
    _CACHE[key] = (time.time() + CACHE_TTL_SECONDS, data)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km using Haversine formula."""
    R = 6371  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def reverse_geocode(lat: float, lon: float) -> dict:
    """
    Reverse geocode a location to verify city name using Geoapify.
    Falls back to Nominatim if Geoapify fails.
    """
    cache_key = f"revgeo_{round(lat, 4)}_{round(lon, 4)}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    result = {
        "city": "Unknown",
        "state": "Unknown",
        "country": "Unknown",
        "confidence": 0.0,
        "source": "none"
    }

    # 1. Try Geoapify
    if config.GEOAPIFY_API_KEY:
        try:
            url = "https://api.geoapify.com/v1/geocode/reverse"
            params = {
                "lat": lat,
                "lon": lon,
                "apiKey": config.GEOAPIFY_API_KEY
            }
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                if features:
                    props = features[0].get("properties", {})
                    result["city"] = props.get("city") or props.get("county", "Unknown")
                    result["state"] = props.get("state", "Unknown")
                    result["country"] = props.get("country", "Unknown")
                    # Rank provides confidence score
                    result["confidence"] = props.get("rank", {}).get("confidence", 1.0)
                    result["source"] = "geoapify"
                    _set_cache(cache_key, result)
                    return result
        except Exception as e:
            print(f"[HospitalRecommender] Geoapify Reverse Geocoding error: {e}")

    # 2. Fallback to Nominatim
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json"
        }
        headers = {
            "User-Agent": "HealthIntel/1.0"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            address = data.get("address", {})
            result["city"] = address.get("city") or address.get("town") or address.get("county", "Unknown")
            result["state"] = address.get("state", "Unknown")
            result["country"] = address.get("country", "Unknown")
            result["confidence"] = 0.8  # Default assumed confidence for fallback
            result["source"] = "nominatim"
            _set_cache(cache_key, result)
            return result
    except Exception as e:
        print(f"[HospitalRecommender] Nominatim Reverse Geocoding error: {e}")

    return result


def _query_geoapify(lat: float, lon: float, radius_km: float) -> Optional[List[HospitalInfo]]:
    """Query Geoapify API for hospitals near a location."""
    if not config.GEOAPIFY_API_KEY:
        print("[HospitalRecommender] GEOAPIFY_API_KEY_MISSING in configuration.")
        return None
        
    radius_m = int(radius_km * 1000)
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "healthcare.hospital",
        "filter": f"circle:{lon},{lat},{radius_m}",
        "bias": f"proximity:{lon},{lat}",
        "limit": 30,
        "apiKey": config.GEOAPIFY_API_KEY
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            features = data.get("features", [])
            hospitals = []
            
            for feature in features:
                props = feature.get("properties", {})
                h_lat = props.get("lat", 0)
                h_lon = props.get("lon", 0)
                
                if h_lat == 0 and h_lon == 0:
                    continue
                    
                distance_km = props.get("distance", 0) / 1000.0
                if distance_km == 0:
                    distance_km = haversine_distance(lat, lon, h_lat, h_lon)
                    
                address = props.get("address_line2", props.get("formatted", "Address not available"))
                name = props.get("name", "Unknown Hospital")
                if not name:
                    name = "Unknown Hospital"
                    
                hospitals.append(HospitalInfo(
                    name=name,
                    address=address,
                    city=props.get("city"),
                    latitude=h_lat,
                    longitude=h_lon,
                    distance_km=round(distance_km, 2),
                    specialties=["general"], # Geoapify doesn't reliably return hospital specialties
                    phone=props.get("contact", {}).get("phone")
                ))
            
            hospitals.sort(key=lambda h: h.distance_km)
            return hospitals
        elif resp.status_code == 429:
            print("[HospitalRecommender] API_RATE_LIMIT exceeded for Geoapify.")
        else:
            print(f"[HospitalRecommender] Geoapify API returned {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[HospitalRecommender] Geoapify API error: {e}")
    
    return None


def _query_nominatim(lat: float, lon: float, radius_km: float) -> Optional[List[HospitalInfo]]:
    """Query OpenStreetMap Nominatim API for hospitals near a location as fallback."""
    # Note: Nominatim search radius is approx based on viewbox
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": "hospital",
        "format": "json",
        "lat": lat,
        "lon": lon,
        "limit": 30
    }
    headers = {
        "User-Agent": "HealthIntel/1.0"
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            hospitals = []
            for item in data:
                h_lat = float(item.get("lat", 0))
                h_lon = float(item.get("lon", 0))
                
                if h_lat == 0 and h_lon == 0:
                    continue
                    
                distance_km = haversine_distance(lat, lon, h_lat, h_lon)
                if distance_km > radius_km:
                    continue
                    
                name = item.get("name", "Unknown Hospital")
                address = item.get("display_name", "Address not available")
                
                hospitals.append(HospitalInfo(
                    name=name,
                    address=address,
                    city=None,  # Not easily extractable from simple JSON response
                    latitude=h_lat,
                    longitude=h_lon,
                    distance_km=round(distance_km, 2),
                    specialties=["general"],
                    phone=None
                ))
            
            hospitals.sort(key=lambda h: h.distance_km)
            return hospitals
    except Exception as e:
        print(f"[HospitalRecommender] Nominatim API error: {e}")
    return None


def _query_local_database(user_lat: float, user_lon: float, radius_km: float,
                          specialties: List[str]) -> List[HospitalInfo]:
    """Fallback: query the local hospitals.csv database."""
    try:
        df = pd.read_csv(config.HOSPITALS_CSV_PATH)
    except Exception:
        return []

    hospitals = []
    for _, row in df.iterrows():
        h_lat = float(row["latitude"])
        h_lon = float(row["longitude"])
        distance = haversine_distance(user_lat, user_lon, h_lat, h_lon)

        if distance > radius_km:
            continue

        h_specialties = [s.strip() for s in str(row.get("specialties", "")).split(",")]

        # Check if hospital has any matching specialty
        has_match = not specialties or any(
            s in h_specialties for s in specialties
        )
        if not has_match:
            continue

        hospitals.append(HospitalInfo(
            name=str(row["name"]),
            address=str(row.get("address", "N/A")),
            city=str(row.get("city", "")),
            latitude=h_lat,
            longitude=h_lon,
            distance_km=round(distance, 2),
            specialties=h_specialties,
            phone=str(row.get("phone", "")) if pd.notna(row.get("phone")) else None,
            rating=float(row.get("rating", 0)) if pd.notna(row.get("rating")) else None,
        ))

    hospitals.sort(key=lambda h: h.distance_km)
    return hospitals


def recommend_hospitals(lat: float, lon: float, disease_category: str,
                        radius_km: float = 10.0) -> dict:
    """
    Get hospital recommendations using Geoapify API (if configured) or Nominatim API.
    Falls back to local CSV database if the APIs are unavailable.
    Results are cached for 1 hour to handle rate limits.
    """
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError("INVALID_COORDINATES: Latitude must be -90 to 90, Longitude -180 to 180.")

    # Check cache
    # Round to 3 decimal places (approx 110m) for caching purposes to increase hits for nearby coords
    cache_key = f"hosp_{round(lat, 3)}_{round(lon, 3)}_{radius_km}"
    cached_result = _get_cache(cache_key)
    if cached_result:
        cached_result["source"] += " (cached)"
        return cached_result

    # Load disease specialties
    disease_config = config.load_disease_config()
    specialties = disease_config.get(disease_category, {}).get("specialties", [])

    hospitals = None
    source = "local_database"
    
    # 1. Try Geoapify API
    if config.GEOAPIFY_API_KEY:
        hospitals = _query_geoapify(lat, lon, radius_km)
        if hospitals is not None:
            source = "geoapify"
            
    # 2. Try Nominatim fallback if Geoapify is not used or failed
    if hospitals is None:
        hospitals = _query_nominatim(lat, lon, radius_km)
        if hospitals is not None:
            source = "nominatim"

    # 3. Fallback to local database
    if hospitals is None:
        hospitals = _query_local_database(lat, lon, radius_km, specialties)
        source = "local_database"

    result = {
        "hospitals": hospitals,
        "search_radius_km": radius_km,
        "total_found": len(hospitals),
        "source": source,
    }
    
    # Store in cache
    _set_cache(cache_key, result)
    
    return result
