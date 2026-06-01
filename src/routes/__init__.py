from .auth_routes import auth_bp
from .room_routes import rooms_bp
from .asset_routes import assets_bp
from .booking_routes import bookings_bp

__all__ = ["auth_bp", "rooms_bp", "assets_bp", "bookings_bp"]
