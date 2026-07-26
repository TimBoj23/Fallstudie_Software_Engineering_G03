"""
Seed-Daten für die RePlan-Demo.

Start:
    python3 scripts/seed_demo_data.py

Das Skript ist idempotent: vorhandene Räume, Assets und Sitzplätze werden nicht
doppelt angelegt.
"""

import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.asset import AssetType
from src.models.user import User, UserRole
from src.repositories.asset_repository import AssetRepository
from src.repositories.room_repository import RoomRepository
from src.repositories.seat_repository import SeatRepository
from src.services.asset_service import AssetService
from src.services.room_service import RoomService
from src.services.seat_service import SeatService
from src.services.user_service import UserService


ASSET_IMAGES = {
    AssetType.BEAMER: "/pictures/Beamer Epson EB-X51.jpeg",
    AssetType.LAPTOP: "/pictures/Laptop Dell XPS 15.jpeg",
    AssetType.MONITOR: "/pictures/Monitor_Dell_27.jpg",
    AssetType.WHITEBOARD: "/pictures/Mobiles_Whiteboard.jpeg",
    AssetType.ADAPTER: "/pictures/USB-C_Adapterkoffer.png",
    AssetType.MODERATION: "/pictures/Moderationskoffer.png",
}

SEED_ADMIN = User(
    id="seed-admin",
    name="Demo-Datenpflege",
    email="seed@replan.local",
    role=UserRole.ADMIN,
)


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
        ("Shared Office Alpha", "1001-A", 10, "shared_desk", "Gebäude A, EG", ["Beamer", "Whiteboard", "Videokonferenz"], "Shared-Desk-Bereich mit flexibel buchbaren Arbeitsplätzen für Teams und hybride Arbeit.", "/pictures/Meetingraum_Alpha.jpeg"),
        ("Shared Office Beta", "1002-B", 6, "shared_desk", "Gebäude A, 1. OG", ["Whiteboard", "Monitor"], "Ruhiger Shared-Desk-Bereich für konzentrierte Projektarbeit und kleine Teams.", "/pictures/Projektraum_Beta.jpg"),
        ("Seminarraum Gamma", "2001-G", 24, "seminarraum", "Gebäude B, 2. OG", ["Smartboard", "Mikrofonanlage", "Streaming-Kamera"], "Heller Seminarraum für Schulungen, Präsentationen und größere Teams.", "/pictures/Seminarraum_Gamma.jpg"),
        ("Seminarraum Delta", "2002-D", 18, "seminarraum", "Gebäude B, 2. OG", ["Beamer", "Flipchart", "Konferenzlautsprecher"], "Flexibler Seminarraum für Trainings und moderierte Gruppenarbeit.", "/pictures/Seminarraum_Delta.jpg"),
        ("Chroma Studio", "3001-C", 8, "studio", "Gebäude C, Studio", ["Greenscreen", "Studiolicht", "Kamera-Setup"], "Studiofläche für Videoaufnahmen, Produktdemos und Streamingformate.", "/pictures/Seminarraum_Chroma.webp"),
        ("Meetingraum Epsilon", "1003-E", 6, "meetingraum", "Gebäude A, 1. OG", ["Display", "Videokonferenz", "Whiteboard"], "Kleiner Meetingraum für vertrauliche Gespräche, Interviews und kurze Abstimmungen.", "/pictures/Meetingraum_Epsilon.jpg"),
    ]
    existing_by_number = {room.number: room for room in room_repo.find_all()}
    for name, number, capacity, room_type, location, equipment, description, image_url in rooms:
        existing = existing_by_number.get(number)
        if existing:
            room_service.update(
                room_id=existing.id,
                requesting_user=SEED_ADMIN,
                name=name,
                number=number,
                capacity=capacity,
                room_type=room_type,
                location=location,
                equipment=equipment,
                description=description,
                image_url=image_url,
            )
        else:
            room_service.create(
                name=name,
                number=number,
                capacity=capacity,
                room_type=room_type,
                location=location,
                equipment=equipment,
                description=description,
                image_url=image_url,
                requesting_user=SEED_ADMIN,
            )


def seed_assets(asset_service: AssetService):
    asset_repo = AssetRepository()
    assets = [
        ("Beamer Epson EB-X51", AssetType.BEAMER, "Full-HD Beamer mit HDMI/VGA für Seminarräume.", "Lager EG"),
        ("Laptop Dell XPS 15", AssetType.LAPTOP, "Windows 11, Intel i7, 32 GB RAM für Präsentationen und Workshops.", "IT-Raum 003"),
        ("Mobiles Whiteboard", AssetType.WHITEBOARD, "Beidseitig beschreibbares Whiteboard auf Rollen inklusive Markerablage.", "Seminarlager A"),
        ("Monitor Dell 27 Zoll", AssetType.MONITOR, "Mobiler QHD-Monitor mit HDMI und USB-C für temporäre Arbeitsplätze.", "IT-Raum 003"),
        ("USB-C Adapterkoffer", AssetType.ADAPTER, "Adapterset mit HDMI, DisplayPort, Ethernet und USB-A für Präsentationen.", "IT-Raum 003"),
        ("Moderationskoffer", AssetType.MODERATION, "Komplettset mit Karten, Markern, Klebepunkten, Magneten und Timer.", "Seminarlager A"),
    ]
    existing_by_name = {asset.name: asset for asset in asset_repo.find_all()}
    for name, asset_type, description, location in assets:
        image_url = ASSET_IMAGES.get(asset_type, ASSET_IMAGES[AssetType.MONITOR])
        existing = existing_by_name.get(name)
        if existing:
            asset_service.update(
                asset_id=existing.id,
                requesting_user=SEED_ADMIN,
                name=name,
                asset_type=asset_type,
                description=description,
                location=location,
                image_url=image_url,
            )
        else:
            asset_service.create(
                name=name,
                asset_type=asset_type,
                description=description,
                location=location,
                image_url=image_url,
                requesting_user=SEED_ADMIN,
            )


def seed_seats(seat_service: SeatService):
    room_repo = RoomRepository()
    seat_repo = SeatRepository()
    rooms = room_repo.find_active()
    shared_room_ids = {room.id for room in rooms if room.room_type == "shared_desk"}
    for seat in seat_repo.find_active():
        if seat.room_id not in shared_room_ids:
            seat_service.deactivate(seat.id, SEED_ADMIN)

    for room in rooms:
        if room.room_type != "shared_desk" or seat_repo.find_by_room(room.id):
            continue
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
                requesting_user=SEED_ADMIN,
            )


DEMO_ADMINS = [
    ("Alexander Vetrenko", "alex@replan.de", "AlexAdmin2026!", "/pictures/Alexander.webp"),
    ("Florian Haentjes", "florian@replan.de", "FlorianAdmin2026!", "/pictures/Florian.jpg"),
    ("Tim Strauss", "tim@replan.de", "TimAdmin2026!", "/pictures/Tim_Test.jpg"),
    ("Denis Nickel", "denis@replan.de", "DenisAdmin2026!", "/pictures/Denis.png"),
]


def seed_admins(user_service: UserService):
    initialized_credentials = []
    for name, email, password, image_url in DEMO_ADMINS:
        existing = user_service.get_by_email(email, include_inactive=True)
        if existing:
            needs_demo_password = not existing.is_active or existing.role != UserRole.ADMIN
            if needs_demo_password or existing.name != name or existing.image_url != image_url:
                user_service.update_user(
                    user_id=existing.id,
                    requesting_user=SEED_ADMIN,
                    name=name,
                    role=UserRole.ADMIN,
                    image_url=image_url,
                    is_active=True,
                )
            if needs_demo_password:
                user_service.reset_password(existing.id, password, SEED_ADMIN)
                initialized_credentials.append((email, password))
            continue
        user_service.register(
            name=name,
            email=email,
            password=password,
            role=UserRole.ADMIN,
            image_url=image_url,
        )
        initialized_credentials.append((email, password))
    return initialized_credentials


def seed_profile_images(user_service: UserService):
    """Aktualisiert bekannte Demo-Profile, ohne neu registrierte Nutzer anzutasten."""
    for user in user_service.get_all():
        if user.image_url == "/pictures/Alexander.avif":
            user_service.update_user(
                user_id=user.id,
                requesting_user=SEED_ADMIN,
                image_url="/pictures/Alexander.webp",
            )


def main():
    room_service = RoomService()
    asset_service = AssetService()
    seat_service = SeatService()
    user_service = UserService()

    seed_rooms(room_service)
    seed_assets(asset_service)
    seed_seats(seat_service)
    initialized_credentials = seed_admins(user_service)
    seed_profile_images(user_service)
    print("Demo-Daten wurden vorbereitet.")
    for name, email, _password, _image_url in DEMO_ADMINS:
        print(f"Admin: {name} – {email}")
    for email, password in initialized_credentials:
        print(f"Initialpasswort gesetzt: {email} / {password}")


if __name__ == "__main__":
    main()
