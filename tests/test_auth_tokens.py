import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from src.utils.tokens import create_auth_token, create_checkin_token, decode_auth_token, decode_checkin_token


def test_auth_token_ist_signiert_und_dekodierbar():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})
    with app.app_context():
        token = create_auth_token("user-123")

        assert token != "user-123"
        assert decode_auth_token(token) == "user-123"
        assert decode_auth_token(f"{token}manipuliert") == ""


def test_checkin_token_bindet_buchung_und_nutzer():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})
    with app.app_context():
        token = create_checkin_token("booking-1", "user-1")
        assert decode_checkin_token(token) == {"booking_id": "booking-1", "user_id": "user-1"}
        assert decode_checkin_token(f"{token}kaputt") == {}
