import json
import os

from fastapi import APIRouter

from ..models.user import UserResponse

router = APIRouter(prefix="/api", tags=["users"])

_MOCK_PATH = os.path.join(os.path.dirname(__file__), "../../data/mock_users.json")


@router.get("/users", response_model=list[UserResponse])
async def list_users() -> list[dict]:
    """Return all users with coordinates, pathologies, and medications."""
    with open(_MOCK_PATH, encoding="utf-8") as f:
        return json.load(f)
