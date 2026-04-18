"""Hospital recommendation router."""
from fastapi import APIRouter
from backend.models.schemas import HospitalRequest, HospitalResponse
from backend.services.hospital_recommender import recommend_hospitals

router = APIRouter(prefix="/api", tags=["Hospitals"])


@router.post("/recommend-hospitals", response_model=HospitalResponse)
async def get_hospital_recommendations(request: HospitalRequest):
    """Get nearby hospital recommendations based on location and disease category."""
    result = recommend_hospitals(
        lat=request.latitude,
        lon=request.longitude,
        disease_category=request.disease_category,
        radius_km=request.radius_km,
    )
    return HospitalResponse(**result)
