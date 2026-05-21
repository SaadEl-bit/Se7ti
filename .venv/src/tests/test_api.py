import pytest
import httpx
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_get_users_returns_list():
    response = client.get("/api/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0


def test_get_users_has_required_fields():
    response = client.get("/api/users")
    user = response.json()[0]
    assert "id" in user
    assert "pseudo" in user
    assert "latitude" in user
    assert "longitude" in user


def test_get_pharmacies_returns_list():
    response = client.get("/api/pharmacies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_pharmacies_garde_filter():
    response = client.get("/api/pharmacies?garde_only=true")
    assert response.status_code == 200
    pharmacies = response.json()
    assert all(p.get("is_garde") for p in pharmacies)


def test_get_pharmacies_on_duty_now():
    response = client.get("/api/pharmacies/garde/now")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_matching_endpoint():
    response = client.get("/api/matching?medication=Metformine&lat=34.686&lon=-1.911")
    assert response.status_code == 200
    data = response.json()
    assert "medication" in data
    assert "matching_users" in data
    assert "count" in data
