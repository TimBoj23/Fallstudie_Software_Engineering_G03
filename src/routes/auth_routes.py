"""
Routes: Auth API
POST /api/auth/register  – Registrierung
POST /api/auth/login     – Login (gibt User-ID zurück, JWT-ready)
POST /api/auth/logout    – Logout
POST /api/auth/forgot-password – Passwort zurücksetzen (MVP)
POST /api/auth/password-reset-request – Reset-Token anfordern
POST /api/auth/password-reset – Passwort per Reset-Token setzen
"""

from flask import Blueprint, request, jsonify
from ..services.user_service import UserService, AuthError
from ..models.user import UserRole
from ..utils.auth_middleware import login_required

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
            image_url=data.get("image_url", ""),
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


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    MVP-Passwort-zurücksetzen.

    Body:
        email        (str)
        new_password (str)
    """
    data = request.get_json(silent=True) or {}
    try:
        user = _user_service.reset_password_by_email(
            email=data.get("email", ""),
            new_password=data.get("new_password", ""),
        )
        return jsonify({
            "message": "Passwort wurde zurückgesetzt.",
            "user": user.to_public_dict(),
        }), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/password-reset-request", methods=["POST"])
def password_reset_request():
    """Fordert ein Reset-Token an. Im MVP wird das Token direkt zurückgegeben."""
    data = request.get_json(silent=True) or {}
    try:
        reset = _user_service.request_password_reset(email=data.get("email", ""))
        return jsonify({
            "message": "Reset-Token wurde erzeugt.",
            "reset": reset,
        }), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 404


@auth_bp.route("/password-reset", methods=["POST"])
def password_reset():
    """Setzt ein Passwort mit gültigem Reset-Token."""
    data = request.get_json(silent=True) or {}
    try:
        user = _user_service.reset_password_with_token(
            token=data.get("token", ""),
            new_password=data.get("new_password", ""),
        )
        return jsonify({
            "message": "Passwort wurde zurückgesetzt.",
            "user": user.to_public_dict(),
        }), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    Meldet den Nutzer ab.

    MVP-Hinweis: Der aktuelle Token ist die User-ID im Header. Dadurch gibt es
    serverseitig keine Session, die invalidiert werden muss.
    """
    return jsonify({"message": "Logout erfolgreich. Token clientseitig entfernen."}), 200
