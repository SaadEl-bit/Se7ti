from fastapi import APIRouter, Query

from ..models.medication import ConsumptionLog  # type: ignore[import]
from ..services.stock_calculator import MedicationTracker  # type: ignore[import]

router = APIRouter(prefix="/api", tags=["medications"])

_tracker = MedicationTracker()


@router.post("/stock/consume")
async def log_consumption(payload: ConsumptionLog) -> dict:
    """Record a medication dose consumption event."""
    return await _tracker.record_consumption(payload)


@router.get("/stock/{user_id}")
async def get_medication_status(user_id: str) -> dict:
    """Return tracked medications and low-stock alerts for a user."""
    return await _tracker.get_medication_status(user_id)


@router.get("/medications/search")
async def search_medications(q: str = Query("", description="Partial medication name")) -> dict:
    """Return known ALD medication names matching a partial query."""
    results = _tracker.search_known_medications(q)
    return {"query": q, "results": results}
