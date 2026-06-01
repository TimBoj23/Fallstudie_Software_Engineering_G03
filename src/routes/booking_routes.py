"""
Routes: Bookings API
GET    /api/bookings            – Eigene Buchungen (Auth required)
GET    /api/bookings/all        – Alle Buchungen (Admin only)
POST   /api/bookings            – Neue Buchung erstellen
GET    /api/bookings/<id>       – Buchung abrufen
DELETE /api/bookings/<id>       – Buchung stornieren
GET    /api/bookings/availability – Verfügbarkeit prüfen
"""

from flask import Blueprint, request, jsonify, g
from ..services.booking_service import BookingService, BookingConflictError, BookingNotFoundError
from ..services.user_service import AuthError
from ..models.booking import BookingTargetType
from ..utils.auth_middleware import login_required, admin_required

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")
_booking_service = BookingService()


@bookings_bp.route("", methods=["GET"])
@login_required
def get_my_bookings():
    """Gibt alle eigenen Buchungen des eingeloggten Nutzers zurück."""
    bookings = _booking_service.get_user_bookings(g.current_user.id)
    return jsonify({
        "bookings": [b.to_dict() for b in bookings],
        "count": len(bookings),
    }), 200


@bookings_bp.route("/all", methods=["GET"])
@admin_required
def get_all_bookings():
    """Gibt alle Buchungen zurück. Nur für Admins."""
    try:
        bookings = _booking_service.get_all_bookings(g.current_user)
        return jsonify({
            "bookings": [b.to_dict() for b in bookings],
            "count": len(bookings),
        }), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 403


@bookings_bp.route("", methods=["POST"])
@login_required
def create_booking():
    """
    Erstellt eine neue Buchung.

    Body (JSON):
        target_id   (str): ID des Raums oder Assets
        target_type (str): "room" | "asset"
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
        )
        return jsonify({"booking": booking.to_dict()}), 201
    except BookingConflictError as e:
        return jsonify({
            "error": str(e),
            "conflicts": [c.to_dict() for c in e.conflicts],
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
    return jsonify({"booking": booking.to_dict()}), 200


@bookings_bp.route("/<booking_id>", methods=["DELETE"])
@login_required
def cancel_booking(booking_id):
    """Storniert eine Buchung (eigene oder als Admin jede)."""
    try:
        booking = _booking_service.cancel_booking(booking_id, g.current_user)
        return jsonify({
            "message": "Buchung wurde erfolgreich storniert.",
            "booking": booking.to_dict(),
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
        target_id   (str): ID des Raums oder Assets
        target_type (str): "room" | "asset"
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
            "conflicts": [c.to_dict() for c in conflicts],
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
