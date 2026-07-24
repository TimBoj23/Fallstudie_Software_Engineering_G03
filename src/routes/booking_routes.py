"""
Routes: Bookings API
GET    /api/bookings            – Eigene Buchungen, optional gefiltert (Auth required)
GET    /api/bookings/all        – Alle Buchungen, optional gefiltert (Admin only)
POST   /api/bookings            – Neue Buchung erstellen
GET    /api/bookings/<id>       – Buchung abrufen
DELETE /api/bookings/<id>       – Buchung stornieren
GET    /api/bookings/availability – Verfügbarkeit prüfen
"""

from flask import Blueprint, request, jsonify, g
from ..models.booking import BookingTargetType
from ..repositories.asset_repository import AssetRepository
from ..repositories.room_repository import RoomRepository
from ..repositories.seat_repository import SeatRepository
from ..repositories.user_repository import UserRepository
from ..services.booking_service import BookingService, BookingConflictError, BookingNotFoundError
from ..services.user_service import AuthError
from ..utils.auth_middleware import login_required, admin_required

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")
_booking_service = BookingService()
_room_repo = RoomRepository()
_seat_repo = SeatRepository()
_asset_repo = AssetRepository()
_user_repo = UserRepository()


@bookings_bp.route("", methods=["GET"])
@login_required
def get_my_bookings():
    """Gibt alle eigenen Buchungen des eingeloggten Nutzers zurück."""
    try:
        bookings = _booking_service.search_bookings(
            requesting_user=g.current_user,
            user_id=g.current_user.id,
            status=request.args.get("status"),
            target_type=request.args.get("target_type"),
            target_id=request.args.get("target_id"),
            start=request.args.get("start"),
            end=request.args.get("end"),
            q=request.args.get("q", ""),
        )
        return jsonify({
            "bookings": [_booking_to_response(b) for b in bookings],
            "count": len(bookings),
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/all", methods=["GET"])
@admin_required
def get_all_bookings():
    """Gibt alle Buchungen zurück. Nur für Admins."""
    try:
        bookings = _booking_service.search_bookings(
            requesting_user=g.current_user,
            user_id=request.args.get("user_id"),
            status=request.args.get("status"),
            target_type=request.args.get("target_type"),
            target_id=request.args.get("target_id"),
            start=request.args.get("start"),
            end=request.args.get("end"),
            q=request.args.get("q", ""),
        )
        return jsonify({
            "bookings": [_booking_to_response(b) for b in bookings],
            "count": len(bookings),
        }), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("", methods=["POST"])
@login_required
def create_booking():
    """
    Erstellt eine neue Buchung.

    Body (JSON):
        target_id   (str): ID des Raums, Assets oder Sitzplatzes
        target_type (str): "room" | "asset" | "seat"
        seat_id     (str, optional): Sitzplatz innerhalb eines Raums
        start_time  (str): ISO-8601 Startzeit
        end_time    (str): ISO-8601 Endzeit
        title       (str, optional): Titel der Buchung
    """
    data = request.get_json(silent=True) or {}
    try:
        target_type = BookingTargetType(data.get("target_type", ""))
        booking = _booking_service.create_booking(
            user=g.current_user,
            target_id=data.get("target_id", ""),
            target_type=target_type,
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            title=data.get("title", "Buchung"),
            seat_id=data.get("seat_id"),
        )
        return jsonify({"booking": _booking_to_response(booking)}), 201
    except BookingConflictError as e:
        return jsonify({
            "error": str(e),
            "conflicts": [_booking_to_response(c) for c in e.conflicts],
        }), 409
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/<booking_id>", methods=["GET"])
@login_required
def get_booking(booking_id):
    booking = _booking_service.get_by_id(booking_id)
    if not booking:
        return jsonify({"error": "Buchung nicht gefunden."}), 404
    if booking.user_id != g.current_user.id and not g.current_user.is_admin():
        return jsonify({"error": "Zugriff verweigert."}), 403
    return jsonify({"booking": _booking_to_response(booking)}), 200


@bookings_bp.route("/<booking_id>", methods=["DELETE"])
@login_required
def cancel_booking(booking_id):
    """Storniert eine Buchung (eigene oder als Admin jede)."""
    try:
        booking = _booking_service.cancel_booking(booking_id, g.current_user)
        return jsonify({
            "message": "Buchung wurde erfolgreich storniert.",
            "booking": _booking_to_response(booking),
        }), 200
    except BookingNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AuthError as e:
        return jsonify({"error": str(e)}), 403


@bookings_bp.route("/availability", methods=["GET"])
def check_availability():
    """
    Prüft Verfügbarkeit eines Objekts für einen Zeitraum.

    Query-Parameter:
        target_id   (str): ID des Raums, Assets oder Sitzplatzes
        target_type (str): "room" | "asset" | "seat"
        start       (str): ISO-8601 Startzeit
        end         (str): ISO-8601 Endzeit
    """
    try:
        target_type = BookingTargetType(request.args.get("target_type", ""))
        is_available, conflicts = _booking_service.check_availability(
            target_id=request.args.get("target_id", ""),
            target_type=target_type,
            start_time=request.args.get("start", ""),
            end_time=request.args.get("end", ""),
        )
        return jsonify({
            "available": is_available,
            "conflicts": [_booking_to_response(c) for c in conflicts],
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


def _booking_to_response(booking):
    data = booking.to_dict()
    target = _resolve_booking_target(booking)
    if target:
        data.update(target)
    user = _user_repo.find_by_id(booking.user_id)
    if user:
        data.update({
            "user_name": user.name,
            "user_email": user.email,
            "user_image_url": user.image_url,
            "user_initials": _initials(user.name or user.email),
        })
    return data


def _resolve_booking_target(booking):
    if booking.target_type == BookingTargetType.ASSET:
        asset = _asset_repo.find_by_id(booking.target_id)
        if not asset:
            return None
        return {
            "target_name": asset.name,
            "target_meta": asset.location or asset.asset_type.value,
            "target_image_url": asset.image_url,
        }

    if booking.target_type == BookingTargetType.SEAT:
        seat = _seat_repo.find_by_id(booking.target_id)
        if not seat:
            return None
        room = _room_repo.find_by_id(seat.room_id)
        room_name = room.name if room else ""
        return {
            "target_name": f"Sitzplatz {seat.label}",
            "target_meta": room_name,
            "target_image_url": seat.image_url or (room.image_url if room else ""),
            "room_name": room_name,
        }

    room = _room_repo.find_by_id(booking.target_id)
    if not room:
        return None
    return {
        "target_name": room.name,
        "target_meta": room.location or room.number,
        "target_image_url": room.image_url,
    }


def _initials(value: str) -> str:
    parts = [part for part in value.replace("@", " ").replace(".", " ").split() if part]
    if not parts:
        return "?"
    return "".join(part[0] for part in parts[:2]).upper()
