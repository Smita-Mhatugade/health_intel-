"""Hospital Recommendation Engine using OpenStreetMap Overpass API."""
import math
import pandas as pd
import requests
from typing import List, Optional
from backend.models.schemas import HospitalInfo
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


def recommend_hospitals(lat: float, lon: float, disease_category: str,
                        radius_km: float = 50.0) -> dict:
    """
    Get hospital recommendations using OpenStreetMap Overpass API.
    Falls back to local CSV database if the API is unavailable.
    """
    # Load disease specialties
    disease_config = config.load_disease_config()
    specialties = disease_config.get(disease_category, {}).get("specialties", [])

    # Try Overpass API first
    elements = _query_overpass(lat, lon, radius_km)
    source = "overpass_api"

    if elements is not None and len(elements) > 0:
        hospitals = _parse_overpass_results(elements, lat, lon, specialties)
    else:
        # Fallback to local database
        source = "local_database"
        hospitals = _query_local_database(lat, lon, radius_km, specialties)

    return {
        "hospitals": hospitals,
        "search_radius_km": radius_km,
        "total_found": len(hospitals),
        "source": source,
    }
