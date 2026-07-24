import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app


def test_schedule_liefert_stuendliche_bloecke_fuer_raum():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})
    client = app.test_client()

    response = client.get(
        "/api/bookings/schedule",
        query_string={
            "target_type": "room",
            "target_id": "6a188a9c-9ee3-4165-9fdd-1e903619b192",
            "start_date": "2026-08-03",
            "days": 2,
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["schedule"]) == 2
    assert len(data["schedule"][0]["slots"]) == 14
    assert data["schedule"][0]["slots"][0]["label"] == "08:00-09:00"
    assert data["schedule"][0]["slots"][-1]["label"] == "21:00-22:00"
