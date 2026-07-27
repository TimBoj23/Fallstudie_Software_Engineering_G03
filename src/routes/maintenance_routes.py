"""Admin-Endpunkte für bewusst bestätigte Demo-Wartung."""

from flask import Blueprint, g, jsonify, request

from ..services.maintenance_service import MaintenanceService
from ..services.user_service import AuthError
from ..utils.auth_middleware import admin_required


maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/api/admin")
_maintenance_service = MaintenanceService()


@maintenance_bp.route("/reset-demo", methods=["POST"])
@admin_required
def reset_demo_activity():
    data = request.get_json(silent=True) or {}
    try:
        result = _maintenance_service.reset_demo_activity(
            requesting_user=g.current_user,
            current_password=data.get("current_password", ""),
            confirmation=data.get("confirmation", ""),
        )
        return jsonify({
            "message": "Demoaktivität wurde zurückgesetzt. Räume und Ausstattung bleiben erhalten.",
            "result": result,
        }), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 401
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
