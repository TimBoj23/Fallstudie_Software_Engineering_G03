"""
Routes: Rooms API
GET    /api/rooms             – Alle Räume (optional: ?start=&end= für Verfügbarkeit)
POST   /api/rooms             – Raum anlegen (Admin)
GET    /api/rooms/<id>        – Einzelnen Raum abrufen
PUT    /api/rooms/<id>        – Raum bearbeiten (Admin)
DELETE /api/rooms/<id>        – Raum deaktivieren (Admin)
"""

from flask import Blueprint, request, jsonify, g
from ..services.room_service import RoomService
from ..services.booking_service import BookingService
from ..models.booking import BookingTargetType
from ..repositories.room_repository import RoomRepository
from ..utils.auth_middleware import login_required, admin_required

rooms_bp = Blueprint("rooms", __name__, url_prefix="/api/rooms")
_room_service = RoomService()
_booking_service = BookingService()


@rooms_bp.route("", methods=["GET"])
def get_rooms():
    """
    Gibt alle aktiven Räume zurück.
    Query-Parameter ?start=&end= filtern auf Verfügbarkeit.
    """
    start = request.args.get("start")
    end = request.args.get("end")

    rooms = _room_service.get_all()

    if start and end:
        try:
            available_ids = set(_booking_service.get_available_rooms(start, end))
            rooms = [r for r in rooms if r.id in available_ids]
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"rooms": [r.to_dict() for r in rooms], "count": len(rooms)}), 200


@rooms_bp.route("/<room_id>", methods=["GET"])
def get_room(room_id):
    room = _room_service.get_by_id(room_id)
    if not room:
        return jsonify({"error": f"Raum '{room_id}' nicht gefunden."}), 404
    return jsonify({"room": room.to_dict()}), 200


@rooms_bp.route("", methods=["POST"])
@admin_required
def create_room():
    """Legt einen neuen Raum an. Nur für Admins."""
    data = request.get_json(silent=True) or {}
    try:
        room = _room_service.create(
            name=data.get("name", ""),
            number=data.get("number", ""),
            capacity=data.get("capacity", 0),
            location=data.get("location", ""),
            equipment=data.get("equipment", []),
            description=data.get("description", ""),
            requesting_user=g.current_user,
        )
        return jsonify({"room": room.to_dict()}), 201
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 400


@rooms_bp.route("/<room_id>", methods=["PUT"])
@admin_required
def update_room(room_id):
    """Aktualisiert einen Raum. Nur für Admins."""
    data = request.get_json(silent=True) or {}
    try:
        room = _room_service.update(
            room_id=room_id,
            requesting_user=g.current_user,
            name=data.get("name"),
            capacity=data.get("capacity"),
            location=data.get("location"),
            equipment=data.get("equipment"),
            description=data.get("description"),
        )
        return jsonify({"room": room.to_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@rooms_bp.route("/<room_id>", methods=["DELETE"])
@admin_required
def deactivate_room(room_id):
    """Deaktiviert einen Raum (Soft-Delete). Nur für Admins."""
    try:
        room = _room_service.deactivate(room_id, g.current_user)
        return jsonify({"message": f"Raum '{room.name}' wurde deaktiviert."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
