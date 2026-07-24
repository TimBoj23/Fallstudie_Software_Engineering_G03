from .auth_routes import auth_bp
from .room_routes import rooms_bp
from .seat_routes import seats_bp, room_seats_bp
from .asset_routes import assets_bp
from .booking_routes import bookings_bp
from .picture_routes import pictures_bp
from .user_routes import users_bp

__all__ = ["auth_bp", "rooms_bp", "seats_bp", "room_seats_bp", "assets_bp", "bookings_bp", "pictures_bp", "users_bp"]
