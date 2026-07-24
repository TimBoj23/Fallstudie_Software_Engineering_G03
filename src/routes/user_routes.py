"""
Routes: Users API
GET  /api/users                  - Nutzerübersicht (Admin)
POST /api/users                  - Nutzer anlegen (Admin)
PUT  /api/users/<id>             - Nutzer bearbeiten (Admin)
POST /api/users/<id>/reset-password - Passwort zurücksetzen (Admin)
"""

from flask import Blueprint, request, jsonify, g

from ..models.user import UserRole
from ..services.user_service import UserService, AuthError
from ..utils.auth_middleware import admin_required

users_bp = Blueprint("users", __name__, url_prefix="/api/users")
_user_service = UserService()


@users_bp.route("", methods=["GET"])
@admin_required
def get_users():
    users = _user_service.get_all()
    return jsonify({
        "users": [user.to_public_dict() for user in users],
        "count": len(users),
    }), 200


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
            requesting_user=g.current_user,
        )
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
            is_active=data.get("is_active") if "is_active" in data else None,
        )
        return jsonify({"user": user.to_public_dict()}), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
