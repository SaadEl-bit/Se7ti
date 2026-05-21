from fastapi import APIRouter

from ..services.alert_service import AlertService

router = APIRouter(prefix="/api", tags=["alerts"])

_alert_service = AlertService()


@router.get("/alerts/{user_id}")
async def get_alerts(user_id: str) -> dict:
    """Return all active stock-depletion alerts for a user."""
    alerts = await _alert_service.get_active_alerts(user_id)
    return {"user_id": user_id, "alerts": alerts}
