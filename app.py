"""
RePlan – Flask App Entry Point

App-Factory-Pattern:
    create_app() erstellt und konfiguriert die Flask-Anwendung.
    Dieses Pattern ermöglicht einfaches Testing (Test-App mit eigener Konfiguration)
    und saubere Trennung von Konfiguration und Anwendungslogik.

Starten:
    python3 app.py
    oder: flask run

API läuft unter: http://localhost:5000
"""

import os
from flask import Flask, jsonify
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

    # ── CORS (für Frontend-Anbindung) ──────────────────────────────────────────
    # Erlaubt Requests vom Frontend (Entwicklung: localhost:3000 / 5173)
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",   # React
                "http://localhost:5173",   # Vite
                "http://localhost:4200",   # Angular
                "http://127.0.0.1:3000",
            ]
        }
    })

    # ── Blueprints registrieren ────────────────────────────────────────────────
    from src.routes.auth_routes import auth_bp
    from src.routes.room_routes import rooms_bp
    from src.routes.asset_routes import assets_bp
    from src.routes.booking_routes import bookings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(bookings_bp)

    # ── Health-Check Endpoint ──────────────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        """Einfacher Health-Check für Deployment-Monitoring."""
        return jsonify({
            "status": "ok",
            "service": "RePlan API",
            "version": "1.0.0-mvp",
        }), 200

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
                },
                "rooms": {
                    "GET  /api/rooms": "Alle Räume (optional: ?start=&end=)",
                    "GET  /api/rooms/<id>": "Einzelnen Raum abrufen",
                    "POST /api/rooms": "Raum anlegen [Admin]",
                    "PUT  /api/rooms/<id>": "Raum bearbeiten [Admin]",
                    "DELETE /api/rooms/<id>": "Raum deaktivieren [Admin]",
                },
                "assets": {
                    "GET  /api/assets": "Alle Assets (optional: ?start=&end=&type=)",
                    "GET  /api/assets/<id>": "Einzelnes Asset abrufen",
                    "POST /api/assets": "Asset anlegen [Admin]",
                    "PUT  /api/assets/<id>": "Asset bearbeiten [Admin]",
                    "DELETE /api/assets/<id>": "Asset deaktivieren [Admin]",
                },
                "bookings": {
                    "GET  /api/bookings": "Eigene Buchungen [Auth]",
                    "GET  /api/bookings/all": "Alle Buchungen [Admin]",
                    "POST /api/bookings": "Buchung erstellen [Auth]",
                    "GET  /api/bookings/<id>": "Buchung abrufen [Auth]",
                    "DELETE /api/bookings/<id>": "Buchung stornieren [Auth]",
                    "GET  /api/bookings/availability": "Verfügbarkeit prüfen",
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
    print("  Server: http://localhost:5000")
    print("  API:    http://localhost:5000/api")
    print("  Health: http://localhost:5000/api/health")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
