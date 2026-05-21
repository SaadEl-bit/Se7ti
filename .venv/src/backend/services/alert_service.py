from typing import Any

from .stock_calculator import MedicationTracker  # type: ignore[import]


class AlertService:
    """Generates in-app low-stock alerts derived from the medication tracker."""

    def __init__(self) -> None:
        self._tracker = MedicationTracker()

    async def get_active_alerts(self, user_id: str) -> list[dict[str, Any]]:
        """Return low-stock alerts for the given user based on current stock levels."""
        data = await self._tracker.get_medication_status(user_id)
        return data.get("low_stock_alerts", [])

    async def create_alert(
        self, user_id: str, medication_id: str, message: str
    ) -> dict[str, Any]:
        """Create a manual alert entry (used by external triggers)."""
        return {"user_id": user_id, "medication_id": medication_id, "message": message}
