import asyncio

from backend.services.stock_calculator import MedicationTracker
from backend.models.medication import StockPurchase


def test_record_purchase_returns_status():
    tracker = MedicationTracker()
    payload = StockPurchase(
        user_id="b1000000-0000-0000-0000-000000000001",
        medication_id="c1000000-0000-0000-0000-000000000001",
        quantity=30,
        notes="Monthly refill",
    )
    result = asyncio.run(tracker.record_purchase(payload))
    assert result["status"] == "recorded"
    assert result["quantity_added"] == 30


def test_get_medication_status_known_user():
    tracker = MedicationTracker()
    result = asyncio.run(tracker.get_medication_status("b1000000-0000-0000-0000-000000000001"))
    assert result["user_id"] == "b1000000-0000-0000-0000-000000000001"
    assert "medications" in result
    assert "low_stock_alerts" in result
    assert len(result["medications"]) == 2


def test_get_medication_status_unknown_user():
    tracker = MedicationTracker()
    result = asyncio.run(tracker.get_medication_status("unknown-user-id"))
    assert result["medications"] == []
    assert result["low_stock_alerts"] == []


def test_low_stock_alert_triggered():
    tracker = MedicationTracker()
    result = asyncio.run(tracker.get_medication_status("b1000000-0000-0000-0000-000000000001"))
    alerts = result["low_stock_alerts"]
    alert_names = [a["medication_name"] for a in alerts]
    assert "Glibenclamide" in alert_names


def test_search_known_medications_partial():
    tracker = MedicationTracker()
    results = tracker.search_known_medications("met")
    assert any("Metformine" in r for r in results)


def test_search_known_medications_empty_query():
    tracker = MedicationTracker()
    results = tracker.search_known_medications("")
    assert len(results) > 0
