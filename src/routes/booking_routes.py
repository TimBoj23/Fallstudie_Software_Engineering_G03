"""
Routes: Bookings API
GET    /api/bookings            – Eigene Buchungen, optional gefiltert (Auth required)
GET    /api/bookings/all        – Alle Buchungen, optional gefiltert (Admin only)
POST   /api/bookings            – Neue Buchung erstellen
GET    /api/bookings/<id>       – Buchung abrufen
DELETE /api/bookings/<id>       – Buchung stornieren
GET    /api/bookings/availability – Verfügbarkeit prüfen
GET    /api/bookings/schedule   – Zeitblock-Kalender für ein Objekt
"""

import os

from flask import Blueprint, request, jsonify, g
from ..models.booking import BookingTargetType
from ..repositories.asset_repository import AssetRepository
from ..repositories.room_repository import RoomRepository
from ..repositories.seat_repository import SeatRepository
from ..repositories.user_repository import UserRepository
from ..services.booking_service import BookingService, BookingConflictError, BookingNotFoundError
from ..services.notification_service import NotificationService
from ..services.audit_service import AuditService
from ..services.user_service import AuthError
from ..utils.auth_middleware import login_required, admin_required
from ..utils.tokens import create_checkin_token, decode_checkin_token

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")
_booking_service = BookingService()
_room_repo = RoomRepository()
_seat_repo = SeatRepository()
_asset_repo = AssetRepository()
_user_repo = UserRepository()
_notification_service = NotificationService()
_audit_service = AuditService()


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
        bookings = _booking_service.create_recurring_bookings(
            user=g.current_user,
            target_id=data.get("target_id", ""),
            target_type=target_type,
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            title=data.get("title", "Buchung"),
            seat_id=data.get("seat_id"),
            access_password=data.get("access_password", ""),
            invitation_emails=data.get("invitation_emails", []),
            recurrence_count=data.get("recurrence_count", 1),
            recurrence_interval=data.get("recurrence_interval", "weekly"),
        )
        booking = bookings[0]
        response_booking = _booking_to_response(booking)
        confirmation = _notification_service.booking_confirmation(
            g.current_user,
            booking,
            response_booking.get("target_name", ""),
        )
        invitations = _notification_service.booking_invitations(
            booking,
            response_booking.get("target_name", ""),
        )
        frontend_url = (
            os.environ.get("FRONTEND_URL")
            or request.headers.get("Origin")
            or "http://localhost:5173"
        ).rstrip("/")
        _audit_service.record(
            g.current_user.id,
            "booking.series_created" if len(bookings) > 1 else "booking.created",
            "booking",
            booking.series_id or booking.id,
            f"{len(bookings)} Buchung(en) wurden erstellt.",
        )
        return jsonify({
            "booking": response_booking,
            "bookings": [_booking_to_response(item) for item in bookings],
            "series_count": len(bookings),
            "confirmation": confirmation,
            "invitations": invitations,
            "invitation": {
                "code": booking.invitation_code,
                "share_url": f"{frontend_url}/?invite={booking.invitation_code}",
                "recipients": booking.invitation_emails,
                "delivery": "manual",
            } if booking.invitation_code else None,
        }), 201
    except BookingConflictError as e:
        suggestions = []
        try:
            target_type = BookingTargetType(data.get("target_type", ""))
            suggestions = _booking_service.suggest_alternatives(
                data.get("target_id", ""), target_type,
                data.get("start_time", ""), data.get("end_time", ""),
            )
        except (ValueError, TypeError):
            pass
        return jsonify({
            "error": str(e),
            "conflicts": [_booking_to_response(c) for c in e.conflicts],
            "suggestions": suggestions,
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
        scope = request.args.get("scope", "single")
        bookings = _booking_service.cancel_booking_scope(booking_id, g.current_user, scope)
        booking = bookings[0]
        _audit_service.record(
            g.current_user.id,
            "booking.series_cancelled" if len(bookings) > 1 else "booking.cancelled",
            "booking",
            booking.series_id or booking.id,
            f"{len(bookings)} Buchung(en) wurden storniert.",
        )
        return jsonify({
            "message": f"{len(bookings)} Buchung(en) wurden erfolgreich storniert.",
            "booking": _booking_to_response(booking),
            "bookings": [_booking_to_response(item) for item in bookings],
        }), 200
    except BookingNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/<booking_id>", methods=["PUT"])
@login_required
def update_booking(booking_id):
    """Bearbeitet einen Termin oder ihn und alle folgenden Serientermine."""
    data = request.get_json(silent=True) or {}
    try:
        target_type = BookingTargetType(data["target_type"]) if data.get("target_type") else None
        bookings = _booking_service.update_booking(
            booking_id=booking_id,
            requesting_user=g.current_user,
            title=data.get("title") if "title" in data else None,
            start_time=data.get("start_time") if "start_time" in data else None,
            end_time=data.get("end_time") if "end_time" in data else None,
            target_id=data.get("target_id") if "target_id" in data else None,
            target_type=target_type,
            scope=data.get("scope", "single"),
        )
        first = bookings[0]
        _audit_service.record(
            g.current_user.id,
            "booking.series_updated" if len(bookings) > 1 else "booking.updated",
            "booking",
            first.series_id or first.id,
            f"{len(bookings)} Buchung(en) wurden aktualisiert.",
        )
        return jsonify({
            "message": f"{len(bookings)} Buchung(en) wurden aktualisiert.",
            "booking": _booking_to_response(first),
            "bookings": [_booking_to_response(item) for item in bookings],
        }), 200
    except BookingNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except BookingConflictError as e:
        return jsonify({
            "error": str(e),
            "conflicts": [_booking_to_response(item) for item in e.conflicts],
        }), 409
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/<booking_id>/extend", methods=["POST"])
@login_required
def extend_booking(booking_id):
    data = request.get_json(silent=True) or {}
    try:
        booking = _booking_service.extend_booking(
            booking_id, g.current_user, data.get("minutes", 30)
        )
        _audit_service.record(
            g.current_user.id,
            "booking.extended",
            "booking",
            booking.id,
            f"Buchung wurde um {int(data.get('minutes', 30))} Minuten verlängert.",
        )
        return jsonify({
            "message": "Buchung wurde verlängert.",
            "booking": _booking_to_response(booking),
        }), 200
    except BookingNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except BookingConflictError as e:
        return jsonify({
            "error": str(e),
            "conflicts": [_booking_to_response(item) for item in e.conflicts],
        }), 409
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/<booking_id>/check-in", methods=["POST"])
@login_required
def check_in_booking(booking_id):
    """Checkt den Buchungsinhaber in eine aktuell laufende Buchung ein."""
    try:
        booking = _booking_service.check_in_booking(booking_id, g.current_user)
        _audit_service.record(g.current_user.id, "booking.checked_in", "booking", booking.id, "Check-in wurde durchgeführt.")
        return jsonify({
            "message": "Check-in erfolgreich.",
            "booking": _booking_to_response(booking),
        }), 200
    except BookingNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/<booking_id>/check-out", methods=["POST"])
@login_required
def check_out_booking(booking_id):
    """Checkt den Buchungsinhaber aus einer Belegung aus."""
    try:
        booking = _booking_service.check_out_booking(booking_id, g.current_user)
        _audit_service.record(g.current_user.id, "booking.checked_out", "booking", booking.id, "Check-out wurde durchgeführt.")
        return jsonify({
            "message": "Check-out erfolgreich.",
            "booking": _booking_to_response(booking),
        }), 200
    except BookingNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/<booking_id>/check-in-code", methods=["GET"])
@login_required
def get_check_in_code(booking_id):
    booking = _booking_service.get_by_id(booking_id)
    if not booking:
        return jsonify({"error": "Buchung nicht gefunden."}), 404
    if booking.user_id != g.current_user.id and not g.current_user.is_admin():
        return jsonify({"error": "Zugriff verweigert."}), 403
    token = create_checkin_token(booking.id, booking.user_id)
    frontend_url = (
        os.environ.get("FRONTEND_URL")
        or request.headers.get("Origin")
        or "http://localhost:5173"
    ).rstrip("/")
    return jsonify({
        "token": token,
        "check_in_url": f"{frontend_url}/?checkin={token}",
        "booking_id": booking.id,
    }), 200


@bookings_bp.route("/qr-check-in", methods=["POST"])
@login_required
def qr_check_in():
    data = request.get_json(silent=True) or {}
    payload = decode_checkin_token(data.get("token", ""))
    if not payload:
        return jsonify({"error": "Der QR-Code ist ungültig oder abgelaufen."}), 400
    if payload.get("user_id") != g.current_user.id and not g.current_user.is_admin():
        return jsonify({"error": "Dieser QR-Code gehört zu einem anderen Konto."}), 403
    try:
        booking = _booking_service.check_in_booking(payload.get("booking_id", ""), g.current_user)
        _audit_service.record(g.current_user.id, "booking.qr_checked_in", "booking", booking.id, "QR-Check-in wurde durchgeführt.")
        return jsonify({"message": "QR-Check-in erfolgreich.", "booking": _booking_to_response(booking)}), 200
    except BookingNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


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


@bookings_bp.route("/schedule", methods=["GET"])
def get_booking_schedule():
    """
    Liefert stündliche Zeitblöcke von 08:00 bis 22:00 Uhr für ein Buchungsobjekt.

    Query-Parameter:
        target_id   (str): ID des Raums, Assets oder Sitzplatzes
        target_type (str): "room" | "asset" | "seat"
        start_date  (str): YYYY-MM-DD
        days        (int): Anzahl Tage, Standard 7
    """
    try:
        target_type = BookingTargetType(request.args.get("target_type", ""))
        schedule = _booking_service.get_time_block_schedule(
            target_id=request.args.get("target_id", ""),
            target_type=target_type,
            start_date=request.args.get("start_date", ""),
            days=int(request.args.get("days", 7)),
        )
        return jsonify({
            "target_id": request.args.get("target_id", ""),
            "target_type": target_type.value,
            "schedule": schedule,
        }), 200
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/<booking_id>/verify-access", methods=["POST"])
def verify_booking_access(booking_id):
    """Prüft ein Zugangspasswort für eine geschützte Seminarraumbuchung."""
    data = request.get_json(silent=True) or {}
    allowed = _booking_service.verify_booking_access(
        booking_id=booking_id,
        access_password=data.get("access_password", ""),
    )
    return jsonify({"allowed": allowed}), 200


@bookings_bp.route("/<booking_id>/join", methods=["POST"])
def join_booking(booking_id):
    """Registriert eine externe Person für eine passwortgeschützte Raumbuchung."""
    data = request.get_json(silent=True) or {}
    try:
        booking = _booking_service.join_protected_booking(
            booking_id=booking_id,
            email=data.get("email", ""),
            access_password=data.get("access_password", ""),
        )
        target = _resolve_booking_target(booking) or {}
        return jsonify({
            "message": "Sie wurden erfolgreich in das Seminar eingebucht.",
            "booking": {
                "title": booking.title,
                "start_time": booking.start_time,
                "end_time": booking.end_time,
                "target_name": target.get("target_name", "Raum"),
            },
        }), 200
    except BookingNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/join", methods=["POST"])
def join_booking_by_code():
    """Registriert eine eingeladene Person über einen kurzen Einladungscode."""
    data = request.get_json(silent=True) or {}
    try:
        booking = _booking_service.join_by_invitation_code(
            invitation_code=data.get("invitation_code", ""),
            email=data.get("email", ""),
            access_password=data.get("access_password", ""),
        )
        target = _resolve_booking_target(booking) or {}
        return jsonify({
            "message": "Sie wurden erfolgreich in die Buchung aufgenommen.",
            "booking": {
                "title": booking.title,
                "start_time": booking.start_time,
                "end_time": booking.end_time,
                "target_name": target.get("target_name", "Raum"),
            },
        }), 200
    except BookingNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/notifications", methods=["GET"])
@login_required
def get_notifications():
    try:
        notifications = _booking_service.get_user_notifications(
            g.current_user, request.args.get("limit", 30)
        )
        return jsonify({
            "notifications": notifications,
            "count": len(notifications),
        }), 200
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@bookings_bp.route("/occupancy", methods=["GET"])
@admin_required
def get_room_occupancy():
    """Admin-Übersicht tatsächlich eingecheckter Personen je Raum."""
    try:
        entries = _booking_service.get_active_room_occupancy(g.current_user)
        response = []
        for entry in entries:
            user = _user_repo.find_by_id(entry["user_id"])
            if user:
                entry.update({
                    "user_name": user.name,
                    "user_email": user.email,
                    "user_image_url": user.image_url,
                    "user_initials": _initials(user.name or user.email),
                })
            response.append(entry)
        return jsonify({"occupancy": response, "count": len(response)}), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 403


@bookings_bp.route("/analytics", methods=["GET"])
@admin_required
def get_booking_analytics():
    try:
        return jsonify({"analytics": _booking_service.get_utilization_stats(
            g.current_user, request.args.get("days", 30)
        )}), 200
    except (AuthError, ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


def _booking_to_response(booking):
    data = booking.to_dict()
    data["has_access_password"] = bool(data.get("access_password_hash"))
    data.pop("access_password_hash", None)
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
