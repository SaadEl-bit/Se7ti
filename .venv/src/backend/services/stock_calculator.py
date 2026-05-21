import json
import os
from datetime import date
from typing import Any

from ..models.medication import ConsumptionLog

_USERS_PATH = os.path.join(os.path.dirname(__file__), "../../data/mock_users.json")

_ALD_MEDICATIONS: list[str] = [
    "Metformine", "Glibenclamide", "Insuline",
    "Amlodipine", "Enalapril", "Losartan",
    "Salbutamol", "Budésonide",
    "Furosémide", "EPO", "Calcium",
    "Ténofovir", "Dolutégravir",
]


def _load_users() -> list[dict]:
    with open(_USERS_PATH, encoding="utf-8") as f:
        return json.load(f)


class MedicationTracker:
    """Tracks medication stock levels and purchase history for patients."""

    async def record_consumption(self, payload: ConsumptionLog) -> dict[str, Any]:
        """Record a medication dose consumption and return confirmation."""
        taken_at = payload.taken_at or date.today().isoformat()
        return {
            "user_id": payload.user_id,
            "medication_id": payload.medication_id,
            "quantity_consumed": payload.quantity,
            "taken_at": taken_at,
            "notes": payload.notes,
            "status": "recorded",
        }

    async def get_medication_status(self, user_id: str) -> dict[str, Any]:
        """Return tracked medications and low-stock alerts for a user."""
        users = _load_users()
        user = next((u for u in users if u["id"] == user_id), None)

        if not user:
            return {"user_id": user_id, "medications": [], "low_stock_alerts": []}

        medications: list[dict] = []
        low_stock_alerts: list[dict] = []
        threshold = 7

        for m in user.get("medicaments", []):
            qty = m.get("stock_restant", 0)
            med = {
                "id": m["id"],
                "name": m["nom"],
                "dosage": m.get("dosage"),
                "stock_quantity": qty,
                "stock_unit": m.get("unite", "comprimé"),
                "alert_threshold": threshold,
            }
            medications.append(med)
            if qty <= threshold:
                low_stock_alerts.append({
                    "medication_id": m["id"],
                    "medication_name": m["nom"],
                    "stock_quantity": qty,
                    "stock_unit": m.get("unite", "comprimé"),
                    "message": f"Stock bas : {qty} {m.get('unite', 'comprimé')}(s) restant(s) pour {m['nom']}",
                })

        return {
            "user_id": user_id,
            "medications": medications,
            "low_stock_alerts": low_stock_alerts,
        }

    def search_known_medications(self, query: str) -> list[str]:
        """Return ALD medication names matching the partial query (case-insensitive)."""
        q = query.lower().strip()
        if not q:
            return _ALD_MEDICATIONS[:]
        return [m for m in _ALD_MEDICATIONS if q in m.lower()]
