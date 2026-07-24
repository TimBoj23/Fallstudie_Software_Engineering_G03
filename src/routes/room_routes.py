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
    Query-Parameter ?q=&location=&min_capacity=&equipment=&start=&end= filtern die Liste.
    """
    start = request.args.get("start")
    end = request.args.get("end")
    availability_mode = request.args.get("availability", "available")
    min_capacity = request.args.get("min_capacity")
    equipment = request.args.getlist("equipment")
    if not equipment and request.args.get("equipment"):
        equipment = request.args.get("equipment").split(",")

    try:
        rooms = _room_service.search(
            query=request.args.get("q", ""),
            location=request.args.get("location", ""),
            min_capacity=int(min_capacity) if min_capacity else None,
            equipment=equipment,
        )
    except ValueError:
        return jsonify({"error": "min_capacity muss eine Zahl sein."}), 400

    if start and end:
        try:
            available_ids = set(_booking_service.get_available_rooms(start, end))
            if availability_mode != "all":
                rooms = [r for r in rooms if r.id in available_ids]
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    response_rooms = []
    for room in rooms:
        data = room.to_dict()
        if start and end:
            data["available"] = room.id in available_ids
        response_rooms.append(data)
    return jsonify({"rooms": response_rooms, "count": len(response_rooms)}), 200


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
            image_url=data.get("image_url", ""),
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
            image_url=data.get("image_url"),
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
