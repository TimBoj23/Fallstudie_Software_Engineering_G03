import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app


def test_seats_endpoint_zeigt_standardmaessig_alle_sitzplaetze():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})
    client = app.test_client()

    response = client.get("/api/seats?availability=all")

    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] >= 1
    assert len(data["seats"]) == data["count"]
