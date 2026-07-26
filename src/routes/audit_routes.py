from flask import Blueprint, g, jsonify, request

from ..services.audit_service import AuditService
from ..services.user_service import AuthError
from ..utils.auth_middleware import admin_required

audit_bp = Blueprint("audit", __name__, url_prefix="/api/audit")
_audit_service = AuditService()


@audit_bp.route("", methods=["GET"])
@admin_required
def get_audit_events():
    try:
        events = _audit_service.list_events(
            g.current_user,
            limit=request.args.get("limit", 100),
            action=request.args.get("action", ""),
            entity_type=request.args.get("entity_type", ""),
        )
        return jsonify({"events": events, "count": len(events)}), 200
    except (AuthError, ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
