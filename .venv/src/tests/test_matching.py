import pytest
import asyncio

from backend.services.matching_engine import MatchingEngine, _haversine


def test_haversine_same_point():
    assert _haversine(34.686, -1.911, 34.686, -1.911) == pytest.approx(0.0)


def test_haversine_known_distance():
    dist = _haversine(34.678, -1.905, 34.686, -1.911)
    assert 0.5 < dist < 2.0


def test_matching_finds_metformine_users():
    engine = MatchingEngine()
    result = asyncio.run(engine.find_matches("Metformine", 34.686, -1.911, radius_km=10))
    assert result["count"] >= 1
    assert any("Metformine" in [m["nom"] for m in u.get("medicaments", [])]
               for u in result["matching_users"])


def test_matching_excludes_distant_users():
    engine = MatchingEngine()
    result = asyncio.run(engine.find_matches("Metformine", 0.0, 0.0, radius_km=1))
    assert result["count"] == 0


def test_matching_case_insensitive():
    engine = MatchingEngine()
    result_lower = asyncio.run(engine.find_matches("metformine", 34.686, -1.911, radius_km=10))
    result_upper = asyncio.run(engine.find_matches("METFORMINE", 34.686, -1.911, radius_km=10))
    assert result_lower["count"] == result_upper["count"]
