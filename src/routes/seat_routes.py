"""
Routes: Seats API
GET    /api/seats             - Alle Sitzplätze (optional: ?room_id=&q=&start=&end=)
POST   /api/seats             - Sitzplatz anlegen (Admin)
GET    /api/seats/<id>        - Einzelnen Sitzplatz abrufen
PUT    /api/seats/<id>        - Sitzplatz bearbeiten (Admin)
DELETE /api/seats/<id>        - Sitzplatz deaktivieren (Admin)
GET    /api/rooms/<id>/seats  - Sitzplätze eines Raums
"""

from flask import Blueprint, request, jsonify, g

from ..services.booking_service import BookingService
from ..services.seat_service import SeatService
from ..services.audit_service import AuditService
from ..utils.auth_middleware import admin_required

seats_bp = Blueprint("seats", __name__, url_prefix="/api/seats")
room_seats_bp = Blueprint("room_seats", __name__, url_prefix="/api/rooms")
_seat_service = SeatService()
_audit_service = AuditService()
_booking_service = BookingService()


@seats_bp.route("", methods=["GET"])
def get_seats():
    """Gibt aktive Sitzplätze zurück, optional gefiltert nach Raum, Suche und Verfügbarkeit."""
    room_id = request.args.get("room_id")
    query = request.args.get("q", "")
    start = request.args.get("start")
    end = request.args.get("end")
    availability_mode = request.args.get("availability", "available")

    shared_desk_only = request.args.get("shared_desk_only", "").lower() == "true"
    if shared_desk_only:
        seats = _seat_service.search_in_shared_desk_rooms(query=query, room_id=room_id)
    else:
        seats = _seat_service.search(query=query, room_id=room_id)
    if start and end:
        try:
            if room_id:
                available_ids = set(_booking_service.get_available_seats(room_id, start, end))
            else:
                available_ids = set(_booking_service.get_available_seat_ids(start, end))
            if availability_mode != "all":
                seats = [s for s in seats if s.id in available_ids]
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    response_seats = []
    for seat in seats:
        data = seat.to_dict()
        if start and end:
            data["available"] = seat.id in available_ids
        response_seats.append(data)
    return jsonify({"seats": response_seats, "count": len(response_seats)}), 200


@room_seats_bp.route("/<room_id>/seats", methods=["GET"])
def get_room_seats(room_id):
    """Gibt alle aktiven Sitzplätze eines Raums zurück."""
    try:
        seats = _seat_service.get_by_room(room_id)
        return jsonify({"seats": [s.to_dict() for s in seats], "count": len(seats)}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@seats_bp.route("/<seat_id>", methods=["GET"])
def get_seat(seat_id):
    seat = _seat_service.get_by_id(seat_id)
    if not seat:
        return jsonify({"error": f"Sitzplatz '{seat_id}' nicht gefunden."}), 404
    return jsonify({"seat": seat.to_dict()}), 200


@seats_bp.route("", methods=["POST"])
@admin_required
def create_seat():
    data = request.get_json(silent=True) or {}
    try:
        seat = _seat_service.create(
            room_id=data.get("room_id", ""),
            label=data.get("label", ""),
            description=data.get("description", ""),
            image_url=data.get("image_url", ""),
            monitor_count=int(data.get("monitor_count", 1)),
            requesting_user=g.current_user,
        )
        _audit_service.record(g.current_user.id, "seat.created", "seat", seat.id, f"Arbeitsplatz {seat.label} wurde angelegt.")
        return jsonify({"seat": seat.to_dict()}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@seats_bp.route("/<seat_id>", methods=["PUT"])
@admin_required
def update_seat(seat_id):
    data = request.get_json(silent=True) or {}
    try:
        seat = _seat_service.update(
            seat_id=seat_id,
            requesting_user=g.current_user,
            label=data.get("label"),
            description=data.get("description"),
            image_url=data.get("image_url"),
            monitor_count=int(data["monitor_count"]) if "monitor_count" in data else None,
        )
        _audit_service.record(g.current_user.id, "seat.updated", "seat", seat.id, f"Arbeitsplatz {seat.label} wurde aktualisiert.")
        return jsonify({"seat": seat.to_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@seats_bp.route("/<seat_id>", methods=["DELETE"])
@admin_required
def deactivate_seat(seat_id):
    try:
        seat = _seat_service.deactivate(seat_id, g.current_user)
        _audit_service.record(g.current_user.id, "seat.deactivated", "seat", seat.id, f"Arbeitsplatz {seat.label} wurde deaktiviert.")
        return jsonify({"message": f"Sitzplatz '{seat.label}' wurde deaktiviert."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
