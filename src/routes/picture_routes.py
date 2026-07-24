"""
Routes: Pictures API
POST /api/pictures - Bilddatei hochladen (Admin)
"""

import os
import uuid

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from ..utils.auth_middleware import admin_required

pictures_bp = Blueprint("pictures", __name__, url_prefix="/api/pictures")

ALLOWED_EXTENSIONS = {".avif", ".jpg", ".jpeg", ".png", ".webp"}


@pictures_bp.route("", methods=["POST"])
@admin_required
def upload_picture():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "Bitte eine Bilddatei auswählen."}), 400

    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Nur AVIF-, PNG-, JPG- und WebP-Dateien sind erlaubt."}), 400

    pictures_dir = os.path.join(current_app.root_path, "data", "pictures")
    os.makedirs(pictures_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    saved_name = f"{uuid.uuid4().hex}_{filename}"
    file.save(os.path.join(pictures_dir, saved_name))

    return jsonify({
        "filename": saved_name,
        "image_url": f"/pictures/{saved_name}",
    }), 201
