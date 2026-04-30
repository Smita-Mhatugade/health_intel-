"""Hospital Recommendation Engine using OpenStreetMap Overpass API."""
import math
import pandas as pd
import requests
from typing import List, Optional
from backend.schemas.schemas import HospitalInfo
from backend import config


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


def _query_overpass(lat: float, lon: float, radius_km: float) -> Optional[List[dict]]:
    """Query Overpass API for hospitals near a location."""
    radius_m = int(radius_km * 1000)
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      way["amenity"="hospital"](around:{radius_m},{lat},{lon});
      relation["amenity"="hospital"](around:{radius_m},{lat},{lon});
    );
    out center;
    """
    try:
        resp = requests.post(config.OVERPASS_API_URL, data={"data": query}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("elements", [])
    except Exception as e:
        print(f"[HospitalRecommender] Overpass API error: {e}")
    return None


def _parse_overpass_results(elements: List[dict], user_lat: float, user_lon: float,
                            specialties: List[str]) -> List[HospitalInfo]:
    """Parse Overpass API results into HospitalInfo objects."""
    hospitals = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name", "Unknown Hospital")

        # Get coordinates (center for ways/relations)
        if "center" in el:
            h_lat = el["center"]["lat"]
            h_lon = el["center"]["lon"]
        else:
            h_lat = el.get("lat", 0)
            h_lon = el.get("lon", 0)

        if h_lat == 0 and h_lon == 0:
            continue

        distance = haversine_distance(user_lat, user_lon, h_lat, h_lon)

        address_parts = []
        for key in ["addr:full", "addr:street", "addr:city", "addr:state"]:
            if key in tags:
                address_parts.append(tags[key])
        address = ", ".join(address_parts) if address_parts else tags.get("name", "Address not available")

        hospital_specialties = []
        spec_tag = tags.get("healthcare:speciality", "")
        if spec_tag:
            hospital_specialties = [s.strip() for s in spec_tag.split(";")]

        hospitals.append(HospitalInfo(
            name=name,
            address=address,
            city=tags.get("addr:city"),
            latitude=h_lat,
            longitude=h_lon,
            distance_km=round(distance, 2),
            specialties=hospital_specialties if hospital_specialties else ["general"],
            phone=tags.get("phone") or tags.get("contact:phone"),
        ))

    hospitals.sort(key=lambda h: h.distance_km)
    return hospitals


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


def _query_geoapify(lat: float, lon: float, radius_km: float) -> Optional[List[HospitalInfo]]:
    """Query Geoapify API for hospitals near a location."""
    if not config.GEOAPIFY_API_KEY:
        return None
        
    radius_m = int(radius_km * 1000)
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "healthcare.hospital",
        "filter": f"circle:{lon},{lat},{radius_m}",
        "bias": f"proximity:{lon},{lat}",
        "limit": 20,
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
    except Exception as e:
        print(f"[HospitalRecommender] Geoapify API error: {e}")
    
    return None


def recommend_hospitals(lat: float, lon: float, disease_category: str,
                        radius_km: float = 50.0) -> dict:
    """
    Get hospital recommendations using Geoapify API (if configured) or Overpass API.
    Falls back to local CSV database if the APIs are unavailable.
    """
    # Load disease specialties
    disease_config = config.load_disease_config()
    specialties = disease_config.get(disease_category, {}).get("specialties", [])

    hospitals = None
    source = "local_database"
    
    # Try Geoapify API first if key is present
    if config.GEOAPIFY_API_KEY:
        hospitals = _query_geoapify(lat, lon, radius_km)
        if hospitals is not None and len(hospitals) > 0:
            source = "geoapify_api"
            
    # Try Overpass API if Geoapify is not used or failed
    if not hospitals:
        elements = _query_overpass(lat, lon, radius_km)
        if elements is not None and len(elements) > 0:
            hospitals = _parse_overpass_results(elements, lat, lon, specialties)
            source = "overpass_api"

    # Fallback to local database
    if not hospitals:
        hospitals = _query_local_database(lat, lon, radius_km, specialties)
        source = "local_database"

    return {
        "hospitals": hospitals,
        "search_radius_km": radius_km,
        "total_found": len(hospitals),
        "source": source,
    }
