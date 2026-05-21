from fastapi import APIRouter, Query

from ..services.matching_engine import MatchingEngine

router = APIRouter(prefix="/api", tags=["matching"])

_engine = MatchingEngine()


@router.get("/matching")
async def get_matching(
    medication: str = Query(..., description="Medication name to match"),
    lat: float = Query(..., description="Requester latitude"),
    lon: float = Query(..., description="Requester longitude"),
    radius_km: float = Query(5.0, description="Search radius in kilometres"),
) -> dict:
    """Return nearby users sharing the given medication within the specified radius."""
    return await _engine.find_matches(medication, lat, lon, radius_km)
