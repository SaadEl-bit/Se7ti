import json
import math
import os
from typing import Any

_USERS_PATH = os.path.join(os.path.dirname(__file__), "../../data/mock_users.json")


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class MatchingEngine:
    """Finds nearby users who share a given medication."""

    async def find_matches(
        self,
        medication: str,
        lat: float,
        lon: float,
        radius_km: float = 5.0,
    ) -> dict[str, Any]:
        """Return users within radius_km who have the specified medication."""
        with open(_USERS_PATH, encoding="utf-8") as f:
            users = json.load(f)

        matches = []
        for user in users:
            distance = _haversine(lat, lon, user["latitude"], user["longitude"])
            if distance > radius_km:
                continue
            user_meds = [m["nom"].lower() for m in user.get("medicaments", [])]
            if medication.lower() in user_meds:
                matches.append({**user, "distance_km": round(distance, 2)})

        return {"medication": medication, "matching_users": matches, "count": len(matches)}
