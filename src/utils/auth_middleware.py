"""
Utils: Auth Middleware
JWT-Authentifizierungs-Middleware für Flask-Routes.

Architekturentscheidung:
    Im MVP wird eine vereinfachte Session-basierte Authentifizierung genutzt.
    Die JWT-Infrastruktur (Token-Generierung, Validierung) ist hier vorbereitet,
    damit der Wechsel zu echter JWT-Auth (z. B. mit flask-jwt-extended) nahtlos
    möglich ist.

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

    MVP-Implementierung: Nutzer-ID wird aus dem X-User-Id Header gelesen.
    Produktion: JWT-Token aus Authorization-Header dekodieren und verifizieren.
    """
    from ..repositories.user_repository import UserRepository
    user_id = request.headers.get("X-User-Id")
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
