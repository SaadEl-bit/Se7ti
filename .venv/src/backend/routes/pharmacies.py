import json
import os
from datetime import date

from fastapi import APIRouter, Query

from ..models.pharmacy import PharmacyResponse

router = APIRouter(prefix="/api", tags=["pharmacies"])

_MOCK_PATH = os.path.join(os.path.dirname(__file__), "../../data/mock_pharmacies.json")


def _load_pharmacies() -> list[dict]:
    with open(_MOCK_PATH, encoding="utf-8") as f:
        return json.load(f)


@router.get("/pharmacies", response_model=list[PharmacyResponse])
async def list_pharmacies(garde_only: bool = Query(False)) -> list[dict]:
    """Return pharmacies, optionally filtered to on-duty ones only."""
    pharmacies = _load_pharmacies()
    if garde_only:
        pharmacies = [p for p in pharmacies if p.get("is_garde")]
    return pharmacies


@router.get("/pharmacies/garde/now", response_model=list[PharmacyResponse])
async def pharmacies_on_duty_now() -> list[dict]:
    """Return pharmacies currently on duty (matching today's date)."""
    today = date.today().isoformat()
    return [
        p for p in _load_pharmacies()
        if p.get("is_garde") and p.get("garde_horaires", {}).get("date") == today
    ]
