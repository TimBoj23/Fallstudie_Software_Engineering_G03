"""
RePlan – Flask App Entry Point

App-Factory-Pattern:
    create_app() erstellt und konfiguriert die Flask-Anwendung.
    Dieses Pattern ermöglicht einfaches Testing (Test-App mit eigener Konfiguration)
    und saubere Trennung von Konfiguration und Anwendungslogik.

Starten:
    python3 app.py
    oder: flask run

API läuft unter: http://localhost:5002
"""

import os
import re
import warnings
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS


def create_app(config: dict = None) -> Flask:
    """
    Flask App Factory.

    Args:
        config: Optionales Konfigurations-Dictionary (nützlich für Tests)

    Returns:
        Konfigurierte Flask-Anwendung
    """
    app = Flask(__name__)

    # ── Konfiguration ──────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "replan-dev-secret-change-in-prod")
    app.config["JSON_SORT_KEYS"] = False

    if config:
        app.config.update(config)

    if app.config["SECRET_KEY"] == "replan-dev-secret-change-in-prod":
        warnings.warn(
            "Using default SECRET_KEY. Set SECRET_KEY environment variable outside local demo use.",
            RuntimeWarning,
            stacklevel=2,
        )

    # ── CORS (für Frontend-Anbindung) ──────────────────────────────────────────
    # Erlaubt Requests vom Frontend (Entwicklung: localhost:3000 / 5173 / 5174)
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",   # React
                "http://localhost:5173",   # Vite
                "http://127.0.0.1:5173",
                "http://localhost:5174",   # Vite Ausweichport
                "http://127.0.0.1:5174",
                "http://localhost:4200",   # Angular
                "http://127.0.0.1:3000",
                re.compile(r"^http://(?:192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+):(?:3000|5173|5174)$"),
            ]
        }
    })

    # ── Blueprints registrieren ────────────────────────────────────────────────
    from src.routes.auth_routes import auth_bp
    from src.routes.room_routes import rooms_bp
    from src.routes.seat_routes import seats_bp, room_seats_bp
    from src.routes.asset_routes import assets_bp
    from src.routes.booking_routes import bookings_bp
    from src.routes.picture_routes import pictures_bp
    from src.routes.user_routes import users_bp
    from src.routes.audit_routes import audit_bp
    from src.routes.maintenance_routes import maintenance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(seats_bp)
    app.register_blueprint(room_seats_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(pictures_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(maintenance_bp)

    # ── Health-Check Endpoint ──────────────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        """Einfacher Health-Check für Deployment-Monitoring."""
        return jsonify({
            "status": "ok",
            "service": "RePlan API",
            "version": "1.0.0-mvp",
        }), 200

    @app.route("/pictures/<path:filename>", methods=["GET"])
    def pictures(filename):
        """Liefert lokal gespeicherte Demo- und Upload-Bilder aus."""
        pictures_dir = os.path.join(app.root_path, "data", "pictures")
        return send_from_directory(pictures_dir, filename)

    # ── API-Übersicht ──────────────────────────────────────────────────────────
    @app.route("/api", methods=["GET"])
    def api_index():
        """Gibt alle verfügbaren API-Endpunkte zurück."""
        return jsonify({
            "service": "RePlan – Raum- und Ressourcenplanungs-API",
            "version": "1.0.0-mvp",
            "endpoints": {
                "auth": {
                    "POST /api/auth/register": "Nutzer registrieren",
                    "POST /api/auth/login": "Nutzer anmelden",
                    "POST /api/auth/logout": "Nutzer abmelden",
                    "POST /api/auth/password-reset-request": "Reset-Token anfordern [MVP]",
                    "POST /api/auth/password-reset": "Passwort per Reset-Token setzen [MVP]",
                },
                "users": {
                    "GET  /api/users": "Nutzer suchen und filtern [Admin]",
                    "POST /api/users": "Nutzer anlegen [Admin]",
                    "PUT  /api/users/<id>": "Nutzer bearbeiten [Admin]",
                    "POST /api/users/<id>/reset-password": "Nutzerpasswort zurücksetzen [Admin]",
                    "GET/PUT /api/users/me/favorites": "Eigene Favoriten verwalten [Auth]",
                    "GET/PUT/DELETE /api/users/me": "Eigenes Profil abrufen, bearbeiten oder anonymisiert löschen [Auth]",
                    "POST /api/users/me/change-password": "Eigenes Passwort ändern [Auth]",
                },
                "pictures": {
                    "POST /api/pictures": "Bilddatei hochladen [Admin]",
                    "POST /api/pictures/profile": "Eigenes Profilbild hochladen [Auth]",
                    "GET  /pictures/<filename>": "Lokales Bild anzeigen",
                },
                "rooms": {
                    "GET  /api/rooms": "Alle Räume (optional: ?q=&location=&min_capacity=&room_type=&equipment=&start=&end=)",
                    "GET  /api/rooms/<id>": "Einzelnen Raum abrufen",
                    "GET  /api/rooms/<id>/seats": "Sitzplätze eines Raums abrufen",
                    "POST /api/rooms": "Raum anlegen [Admin]",
                    "PUT  /api/rooms/<id>": "Raum bearbeiten [Admin]",
                    "DELETE /api/rooms/<id>": "Raum deaktivieren [Admin]",
                },
                "seats": {
                    "GET  /api/seats": "Alle Sitzplätze (optional: ?room_id=&q=&start=&end=)",
                    "GET  /api/seats/<id>": "Einzelnen Sitzplatz abrufen",
                    "POST /api/seats": "Sitzplatz anlegen [Admin]",
                    "PUT  /api/seats/<id>": "Sitzplatz bearbeiten [Admin]",
                    "DELETE /api/seats/<id>": "Sitzplatz deaktivieren [Admin]",
                },
                "assets": {
                    "GET  /api/assets": "Alle Assets (optional: ?q=&start=&end=&type=)",
                    "GET  /api/assets/<id>": "Einzelnes Asset abrufen",
                    "POST /api/assets": "Asset anlegen [Admin]",
                    "PUT  /api/assets/<id>": "Asset bearbeiten [Admin]",
                    "DELETE /api/assets/<id>": "Asset deaktivieren [Admin]",
                },
                "bookings": {
                    "GET  /api/bookings": "Eigene Buchungen [Auth]",
                    "GET  /api/bookings/all": "Alle Buchungen [Admin]",
                    "GET  /api/bookings/occupancy": "Aktive Raumbelegung mit Nutzerkontext [Admin]",
                    "GET  /api/bookings/analytics": "Auslastungsstatistik [Admin]",
                    "POST /api/bookings": "Einzel- oder Serienbuchung erstellen [Auth]",
                    "GET  /api/bookings/<id>": "Buchung abrufen [Auth]",
                    "PUT  /api/bookings/<id>": "Einzelne oder zukünftige Serientermine bearbeiten [Auth]",
                    "POST /api/bookings/<id>/extend": "Buchung bei freiem Folgezeitraum verlängern [Auth]",
                    "POST /api/bookings/<id>/verify-access": "Passwort für geschützte Buchung prüfen",
                    "POST /api/bookings/<id>/join": "Externe Person per Buchungspasswort einbuchen",
                    "POST /api/bookings/join": "Externe Person per kurzem Einladungscode einbuchen",
                    "GET  /api/bookings/notifications": "Eigene In-App-Benachrichtigungen [Auth]",
                    "DELETE /api/bookings/<id>": "Buchung stornieren [Auth]",
                    "POST /api/bookings/<id>/check-in": "In laufende Buchung einchecken [Auth]",
                    "POST /api/bookings/<id>/check-out": "Aus laufender Buchung auschecken [Auth]",
                    "GET  /api/bookings/<id>/check-in-code": "Signierten QR-Check-in-Link erzeugen [Auth]",
                    "POST /api/bookings/qr-check-in": "Per QR-Token einchecken [Auth]",
                    "GET  /api/bookings/availability": "Verfügbarkeit prüfen",
                },
                "audit": {
                    "GET /api/audit": "Änderungsprotokoll anzeigen [Admin]",
                },
                "maintenance": {
                    "POST /api/admin/reset-demo": "Demoaktivität passwortgeschützt zurücksetzen [Admin]",
                },
            },
        }), 200

    # ── Globale Fehlerbehandlung ───────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpunkt nicht gefunden."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "HTTP-Methode nicht erlaubt."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Interner Serverfehler."}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    print("=" * 60)
    print("  RePlan API – Raum- und Ressourcenplanungssystem")
    print("=" * 60)
    print("  Server: http://localhost:5002")
    print("  API:    http://localhost:5002/api")
    print("  Health: http://localhost:5002/api/health")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5002)
