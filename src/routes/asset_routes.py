"""
Routes: Assets API
GET    /api/assets          – Alle Assets (optional: ?start=&end=&type=)
POST   /api/assets          – Asset anlegen (Admin)
GET    /api/assets/<id>     – Einzelnes Asset
PUT    /api/assets/<id>     – Asset bearbeiten (Admin)
DELETE /api/assets/<id>     – Asset deaktivieren (Admin)
"""

from flask import Blueprint, request, jsonify, g
from ..services.asset_service import AssetService
from ..services.booking_service import BookingService
from ..models.asset import AssetType
from ..utils.auth_middleware import login_required, admin_required

assets_bp = Blueprint("assets", __name__, url_prefix="/api/assets")
_asset_service = AssetService()
_booking_service = BookingService()


@assets_bp.route("", methods=["GET"])
def get_assets():
    """Alle aktiven Assets, optional nach Zeitraum und Typ gefiltert."""
    start = request.args.get("start")
    end = request.args.get("end")
    asset_type_str = request.args.get("type")

    assets = _asset_service.get_all()

    if asset_type_str:
        try:
            atype = AssetType(asset_type_str)
            assets = [a for a in assets if a.asset_type == atype]
        except ValueError:
            return jsonify({"error": f"Unbekannter Asset-Typ: '{asset_type_str}'."}), 400

    if start and end:
        try:
            available_ids = set(_booking_service.get_available_assets(start, end))
            assets = [a for a in assets if a.id in available_ids]
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"assets": [a.to_dict() for a in assets], "count": len(assets)}), 200


@assets_bp.route("/<asset_id>", methods=["GET"])
def get_asset(asset_id):
    asset = _asset_service.get_by_id(asset_id)
    if not asset:
        return jsonify({"error": f"Asset '{asset_id}' nicht gefunden."}), 404
    return jsonify({"asset": asset.to_dict()}), 200


@assets_bp.route("", methods=["POST"])
@admin_required
def create_asset():
    data = request.get_json(silent=True) or {}
    try:
        atype = AssetType(data.get("asset_type", AssetType.OTHER.value))
        asset = _asset_service.create(
            name=data.get("name", ""),
            asset_type=atype,
            description=data.get("description", ""),
            location=data.get("location", ""),
            requesting_user=g.current_user,
        )
        return jsonify({"asset": asset.to_dict()}), 201
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 400


@assets_bp.route("/<asset_id>", methods=["PUT"])
@admin_required
def update_asset(asset_id):
    data = request.get_json(silent=True) or {}
    try:
        atype = AssetType(data["asset_type"]) if "asset_type" in data else None
        asset = _asset_service.update(
            asset_id=asset_id,
            requesting_user=g.current_user,
            name=data.get("name"),
            asset_type=atype,
            description=data.get("description"),
            location=data.get("location"),
        )
        return jsonify({"asset": asset.to_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@assets_bp.route("/<asset_id>", methods=["DELETE"])
@admin_required
def deactivate_asset(asset_id):
    try:
        asset = _asset_service.deactivate(asset_id, g.current_user)
        return jsonify({"message": f"Asset '{asset.name}' wurde deaktiviert."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
