"""
Routes: Auth API
POST /api/auth/register  – Registrierung
POST /api/auth/login     – Login (gibt User-ID zurück, JWT-ready)
"""

from flask import Blueprint, request, jsonify
from ..services.user_service import UserService, AuthError
from ..models.user import UserRole

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
_user_service = UserService()


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registriert einen neuen Nutzer.

    Body (JSON):
        name     (str): Vollständiger Name
        email    (str): E-Mail-Adresse
        password (str): Passwort (min. 6 Zeichen)
        role     (str, optional): "user" | "admin" (Standard: "user")

    Returns:
        201: { user: {...} }
        400: { error: "..." }
    """
    data = request.get_json(silent=True) or {}
    try:
        role = UserRole(data.get("role", UserRole.USER.value))
        user = _user_service.register(
            name=data.get("name", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            role=role,
        )
        return jsonify({"user": user.to_public_dict()}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authentifiziert einen Nutzer.

    Body (JSON):
        email    (str): E-Mail-Adresse
        password (str): Passwort

    Returns:
        200: { user: {...}, token: "<user_id>" }
             (token = user_id als MVP-Ersatz für JWT)
        401: { error: "..." }
    """
    data = request.get_json(silent=True) or {}
    try:
        user = _user_service.login(
            email=data.get("email", ""),
            password=data.get("password", ""),
        )
        # MVP: user.id als "token" – für JWT-Upgrade hier ersetzen
        return jsonify({
            "user": user.to_public_dict(),
            "token": user.id,  # Wird bei JWT-Upgrade durch echtes Token ersetzt
        }), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 401
