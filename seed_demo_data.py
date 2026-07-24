"""
Seed-Daten für die RePlan-Demo.

Start:
    python3 seed_demo_data.py

Das Skript ist idempotent: vorhandene Räume, Assets und Sitzplätze werden nicht
doppelt angelegt.
"""

import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.asset import AssetType
from src.models.user import UserRole
from src.repositories.asset_repository import AssetRepository
from src.repositories.room_repository import RoomRepository
from src.repositories.seat_repository import SeatRepository
from src.services.asset_service import AssetService
from src.services.room_service import RoomService
from src.services.seat_service import SeatService
from src.services.user_service import UserService


ROOM_IMAGES = [
    "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1517502884422-41eaead166d4?auto=format&fit=crop&w=900&q=80",
]

ASSET_IMAGES = {
    AssetType.BEAMER: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80",
    AssetType.LAPTOP: "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80",
    AssetType.MONITOR: "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=900&q=80",
    AssetType.WHITEBOARD: "https://images.unsplash.com/photo-1581726707445-75cbe4efc586?auto=format&fit=crop&w=900&q=80",
}


def seat_image(monitors: int) -> str:
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 360'>"
        "<rect width='640' height='360' fill='#eef2ff'/>"
        "<rect x='120' y='235' width='400' height='48' rx='10' fill='#334155'/>"
        "<rect x='210' y='285' width='220' height='22' rx='8' fill='#475569'/>"
        + "".join(
            f"<rect x='{150 + i * 115}' y='95' width='95' height='68' rx='8' fill='#2563eb'/>"
            f"<rect x='{188 + i * 115}' y='163' width='18' height='52' fill='#1e293b'/>"
            for i in range(monitors)
        )
        + f"<text x='320' y='60' text-anchor='middle' font-family='Arial' font-size='28' fill='#1e293b'>{monitors} Monitor(e)</text>"
        "</svg>"
    )
    return "data:image/svg+xml;utf8," + quote(svg, safe="/:=;,'()")


def seed_rooms(room_service: RoomService):
    room_repo = RoomRepository()
    rooms = [
        ("Seminarraum Alpha", "SR-101", 24, "Gebäude A, EG", ["Beamer", "Whiteboard", "Videokonferenz"], "Großer Seminarraum für Workshops.", ROOM_IMAGES[0]),
        ("Seminarraum Beta", "SR-202", 16, "Gebäude A, 2. OG", ["Whiteboard", "Monitor"], "Heller Raum für kleinere Seminare.", ROOM_IMAGES[1]),
        ("Projektstudio Gamma", "PS-303", 10, "Gebäude B, 1. OG", ["Monitor", "Moderationskoffer"], "Flexibler Projektraum für Teamarbeit.", ROOM_IMAGES[2]),
        ("Meetingraum Delta", "MR-011", 8, "Gebäude C, EG", ["Whiteboard"], "Kompakter Raum für Abstimmungen.", ROOM_IMAGES[0]),
        ("Konferenzraum Epsilon", "KR-404", 32, "Gebäude B, 4. OG", ["Beamer", "Soundanlage", "Videokonferenz"], "Großer Konferenzraum mit Präsentationstechnik.", ROOM_IMAGES[1]),
    ]
    for name, number, capacity, location, equipment, description, image_url in rooms:
        if room_repo.number_exists(number):
            continue
        room_service.create(
            name=name,
            number=number,
            capacity=capacity,
            location=location,
            equipment=equipment,
            description=description,
            image_url=image_url,
        )


def seed_assets(asset_service: AssetService):
    asset_repo = AssetRepository()
    assets = [
        ("Beamer Epson EB-X51", AssetType.BEAMER, "Full-HD Beamer, HDMI/VGA", "Lager EG"),
        ("Laptop Dell XPS 15", AssetType.LAPTOP, "Windows 11, Intel i7", "IT-Raum 003"),
        ("Monitor LG UltraWide", AssetType.MONITOR, "34 Zoll UltraWide Monitor", "Shared Office A"),
        ("Whiteboard mobil", AssetType.WHITEBOARD, "Mobiles Whiteboard mit Rollen", "Seminarbereich"),
        ("Moderationskoffer", AssetType.MODERATION, "Karten, Marker und Magnete", "Lager EG"),
        ("USB-C Adapterset", AssetType.ADAPTER, "HDMI, LAN und USB Adapter", "IT-Raum 003"),
    ]
    existing_names = {asset.name for asset in asset_repo.find_all()}
    for name, asset_type, description, location in assets:
        if name in existing_names:
            continue
        asset_service.create(
            name=name,
            asset_type=asset_type,
            description=description,
            location=location,
            image_url=ASSET_IMAGES.get(asset_type, ASSET_IMAGES[AssetType.MONITOR]),
        )


def seed_seats(seat_service: SeatService):
    room_repo = RoomRepository()
    seat_repo = SeatRepository()
    for room in room_repo.find_active():
        for index, monitors in enumerate([1, 2, 3, 2], start=1):
            label = f"{room.number}-P{index}"
            if seat_repo.label_exists(room.id, label):
                continue
            seat_service.create(
                room_id=room.id,
                label=label,
                description=f"Arbeitsplatz mit {monitors} Monitor(en) in {room.name}.",
                monitor_count=monitors,
                image_url=seat_image(monitors),
            )


def seed_admin(user_service: UserService):
    try:
        user_service.register(
            name="Demo Admin",
            email="admin@replan.de",
            password="admin123",
            role=UserRole.ADMIN,
        )
    except ValueError:
        pass


def main():
    room_service = RoomService()
    asset_service = AssetService()
    seat_service = SeatService()
    user_service = UserService()

    seed_rooms(room_service)
    seed_assets(asset_service)
    seed_seats(seat_service)
    seed_admin(user_service)
    print("Demo-Daten wurden vorbereitet.")
    print("Admin: admin@replan.de / admin123")


if __name__ == "__main__":
    main()
