"""
Routes: Users API
GET  /api/users                  - Nutzerübersicht (Admin)
POST /api/users                  - Nutzer anlegen (Admin)
GET/PUT/DELETE /api/users/me     - Eigenes Konto verwalten
POST /api/users/me/change-password - Eigenes Passwort ändern
PUT  /api/users/<id>             - Nutzer bearbeiten (Admin)
POST /api/users/<id>/reset-password - Passwort zurücksetzen (Admin)
"""

from flask import Blueprint, request, jsonify, g

from ..models.user import UserRole
from ..services.user_service import UserService, AuthError
from ..services.audit_service import AuditService
from ..utils.auth_middleware import admin_required, login_required

users_bp = Blueprint("users", __name__, url_prefix="/api/users")
_user_service = UserService()
_audit_service = AuditService()


@users_bp.route("", methods=["GET"])
@admin_required
def get_users():
    users = _user_service.search_users(
        query=request.args.get("q", ""),
        role=request.args.get("role", ""),
        status=request.args.get("status", "active"),
    )
    return jsonify({
        "users": [user.to_public_dict() for user in users],
        "count": len(users),
    }), 200


@users_bp.route("/me", methods=["GET"])
@login_required
def get_own_profile():
    """Liefert das eigene Profil ohne sensitive Felder."""
    return jsonify({"user": g.current_user.to_public_dict()}), 200


@users_bp.route("/me", methods=["PUT"])
@login_required
def update_own_profile():
    data = request.get_json(silent=True) or {}
    try:
        user = _user_service.update_own_profile(
            user_id=g.current_user.id,
            name=data.get("name") if "name" in data else None,
            email=data.get("email") if "email" in data else None,
            image_url=data.get("image_url") if "image_url" in data else None,
        )
        _audit_service.record(user.id, "profile.updated", "user", user.id, "Eigenes Profil wurde aktualisiert.")
        return jsonify({"message": "Profil wurde aktualisiert.", "user": user.to_public_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/me/change-password", methods=["POST"])
@login_required
def change_own_password():
    data = request.get_json(silent=True) or {}
    try:
        user = _user_service.change_own_password(
            user_id=g.current_user.id,
            current_password=data.get("current_password", ""),
            new_password=data.get("new_password", ""),
        )
        _audit_service.record(user.id, "password.changed", "user", user.id, "Eigenes Passwort wurde geändert.")
        return jsonify({"message": "Passwort wurde geändert."}), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 401
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/me", methods=["DELETE"])
@login_required
def delete_own_account():
    data = request.get_json(silent=True) or {}
    try:
        user = _user_service.deactivate_own_account(
            user_id=g.current_user.id,
            current_password=data.get("current_password", ""),
        )
        _audit_service.record(user.id, "account.deactivated", "user", user.id, "Eigenes Konto wurde deaktiviert.")
        return jsonify({"message": "Konto wurde gelöscht und der Zugriff deaktiviert."}), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 401
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/me/favorites", methods=["GET"])
@login_required
def get_favorites():
    favorites = _user_service.get_favorites(g.current_user.id)
    return jsonify({"favorites": favorites, "count": len(favorites)}), 200


@users_bp.route("/me/favorites", methods=["PUT"])
@login_required
def update_favorite():
    data = request.get_json(silent=True) or {}
    try:
        favorites = _user_service.set_favorite(
            user_id=g.current_user.id,
            target_type=data.get("target_type", ""),
            target_id=data.get("target_id", ""),
            enabled=bool(data.get("enabled", True)),
        )
        _audit_service.record(g.current_user.id, "favorite.updated", "user", g.current_user.id, "Favoriten wurden aktualisiert.")
        return jsonify({"favorites": favorites, "count": len(favorites)}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json(silent=True) or {}
    try:
        role = UserRole(data.get("role", UserRole.USER.value))
        user = _user_service.create_user(
            name=data.get("name", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            role=role,
            image_url=data.get("image_url", ""),
            requesting_user=g.current_user,
        )
        _audit_service.record(g.current_user.id, "user.created", "user", user.id, f"Nutzer {user.email} wurde angelegt.")
        return jsonify({"user": user.to_public_dict()}), 201
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/<user_id>/reset-password", methods=["POST"])
@admin_required
def reset_user_password(user_id):
    data = request.get_json(silent=True) or {}
    new_password = data.get("new_password") or _user_service.generate_temporary_password()
    try:
        user = _user_service.reset_password(
            user_id=user_id,
            new_password=new_password,
            requesting_user=g.current_user,
        )
        _audit_service.record(g.current_user.id, "user.password_reset", "user", user.id, f"Passwort für {user.email} wurde administrativ zurückgesetzt.")
        return jsonify({
            "message": "Passwort wurde zurückgesetzt.",
            "temporary_password": new_password,
            "user": user.to_public_dict(),
        }), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/<user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    try:
        role = UserRole(data["role"]) if "role" in data else None
        user = _user_service.update_user(
            user_id=user_id,
            requesting_user=g.current_user,
            name=data.get("name"),
            email=data.get("email"),
            role=role,
            image_url=data.get("image_url"),
            is_active=data.get("is_active") if "is_active" in data else None,
        )
        _audit_service.record(g.current_user.id, "user.updated", "user", user.id, f"Nutzer {user.email} wurde aktualisiert.")
        return jsonify({"user": user.to_public_dict()}), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
