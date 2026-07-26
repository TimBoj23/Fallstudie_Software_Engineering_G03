"""Signierte, zeitlich begrenzte Authentifizierungs-Tokens."""

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


AUTH_TOKEN_SALT = "replan-auth-token-v1"
AUTH_TOKEN_MAX_AGE_SECONDS = 12 * 60 * 60
CHECKIN_TOKEN_SALT = "replan-checkin-token-v1"
CHECKIN_TOKEN_MAX_AGE_SECONDS = 14 * 24 * 60 * 60


def create_auth_token(user_id: str) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({"user_id": user_id}, salt=AUTH_TOKEN_SALT)


def decode_auth_token(token: str) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        payload = serializer.loads(
            token,
            salt=AUTH_TOKEN_SALT,
            max_age=AUTH_TOKEN_MAX_AGE_SECONDS,
        )
    except (BadSignature, SignatureExpired):
        return ""
    return str(payload.get("user_id", ""))


def create_checkin_token(booking_id: str, user_id: str) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(
        {"booking_id": booking_id, "user_id": user_id},
        salt=CHECKIN_TOKEN_SALT,
    )


def decode_checkin_token(token: str) -> dict:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return serializer.loads(
            token,
            salt=CHECKIN_TOKEN_SALT,
            max_age=CHECKIN_TOKEN_MAX_AGE_SECONDS,
        )
    except (BadSignature, SignatureExpired):
        return {}
