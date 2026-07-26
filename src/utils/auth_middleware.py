"""
Utils: Auth Middleware
Authentifizierungs-Middleware für Flask-Routes.

Architekturentscheidung:
    Im MVP werden signierte und zeitlich begrenzte Bearer-Tokens verwendet.

    Für Produktion:
        - JWT mit kurzer Laufzeit (15 min) + Refresh-Token
        - Token-Blacklist via Redis
        - HTTPS erzwungen
"""

import functools
from flask import request, jsonify, g


def _get_user_from_request():
    """
    Extrahiert den Nutzer aus dem Request-Kontext.

    Das signierte Token wird aus dem Authorization-Header gelesen und verifiziert.
    """
    from ..repositories.user_repository import UserRepository
    from .tokens import decode_auth_token

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "", 1).strip() if auth_header.startswith("Bearer ") else ""
    user_id = decode_auth_token(token) if token else ""
    if not user_id:
        return None
    repo = UserRepository()
    return repo.find_by_id(user_id)


def login_required(f):
    """
    Decorator: Stellt sicher, dass der anfragende Nutzer eingeloggt ist.

    Usage:
        @app.route("/api/bookings")
        @login_required
        def get_bookings():
            user = g.current_user
            ...
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        user = _get_user_from_request()
        if not user:
            return jsonify({"error": "Authentifizierung erforderlich."}), 401
        if not user.is_active:
            return jsonify({"error": "Konto ist deaktiviert."}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """
    Decorator: Stellt sicher, dass der anfragende Nutzer Admin ist.

    Usage:
        @app.route("/api/rooms", methods=["POST"])
        @admin_required
        def create_room():
            ...
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        user = _get_user_from_request()
        if not user:
            return jsonify({"error": "Authentifizierung erforderlich."}), 401
        if not user.is_active:
            return jsonify({"error": "Konto ist deaktiviert."}), 403
        if not user.is_admin():
            return jsonify({"error": "Administrator-Rechte erforderlich."}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated
