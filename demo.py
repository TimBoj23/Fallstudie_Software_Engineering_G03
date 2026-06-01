"""
RePlan – Interaktive Terminal-Demo

Führt einen vollständigen Demo-Durchlauf durch:
    - Nutzer registrieren / einloggen
    - Räume und Assets anzeigen
    - Raum buchen
    - Asset buchen
    - Doppelbuchung testen (wird verhindert)
    - Eigene Buchungen anzeigen
    - Buchung stornieren

Starten:
    python3 demo.py
"""

import os
import sys
import uuid
from datetime import datetime, timedelta

# Projekt-Root zum sys.path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.user import UserRole
from src.models.booking import BookingTargetType
from src.models.asset import AssetType
from src.services.user_service import UserService, AuthError
from src.services.room_service import RoomService
from src.services.asset_service import AssetService
from src.services.booking_service import BookingService, BookingConflictError

# ── Farben für Terminal-Output ─────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
DIM    = "\033[2m"

def c(color, text): return f"{color}{text}{RESET}"
def ok(text):  print(f"  {c(GREEN, '✓')} {text}")
def err(text): print(f"  {c(RED, '✗')} {text}")
def info(text): print(f"  {c(BLUE, 'ℹ')} {text}")
def warn(text): print(f"  {c(YELLOW, '⚠')} {text}")


# ── Services (Demo nutzt temporäre Daten) ─────────────────────────────────────
user_svc    = UserService()
room_svc    = RoomService()
asset_svc   = AssetService()
booking_svc = BookingService()

# Demo-State
current_user = None
demo_room_id = None
demo_asset_id = None


# ─────────────────────────────────────────────────────────────────────────────
# Hilfsfunktionen
# ─────────────────────────────────────────────────────────────────────────────

def header(title: str):
    width = 60
    print()
    print(c(BOLD + CYAN, "═" * width))
    print(c(BOLD + CYAN, f"  {title}"))
    print(c(BOLD + CYAN, "═" * width))


def pause():
    input(c(DIM, "\n  [Enter] drücken um fortzufahren..."))


def future_time(hours_from_now: int = 1, duration_hours: int = 2):
    """Gibt einen zukünftigen Zeitraum als ISO-8601 Strings zurück."""
    start = datetime.utcnow() + timedelta(hours=hours_from_now)
    end   = start + timedelta(hours=duration_hours)
    return start.strftime("%Y-%m-%dT%H:%M:%S"), end.strftime("%Y-%m-%dT%H:%M:%S")


def print_menu(title: str, options: list):
    print()
    print(c(BOLD, f"  {title}"))
    print(c(DIM, "  " + "─" * 40))
    for i, (key, label) in enumerate(options, 1):
        print(f"  {c(YELLOW, key)}  {label}")
    print(c(DIM, "  " + "─" * 40))


def get_choice(prompt: str = "Auswahl") -> str:
    return input(f"\n  {c(BOLD, prompt)}: ").strip()


# ─────────────────────────────────────────────────────────────────────────────
# Demo-Szenarien
# ─────────────────────────────────────────────────────────────────────────────

def demo_setup_seed_data():
    """Legt Demo-Räume und Assets an, falls noch keine vorhanden."""
    global demo_room_id, demo_asset_id

    header("SCHRITT 0: Demo-Daten vorbereiten")
    info("Prüfe vorhandene Räume und Assets...")

    # Räume prüfen/anlegen
    rooms = room_svc.get_all()
    if not rooms:
        info("Keine Räume vorhanden – lege Demo-Räume an...")
        try:
            r1 = room_svc.create(
                name="Meetingraum Alpha",
                number="1001-A",
                capacity=10,
                location="Gebäude A, EG",
                equipment=["Beamer", "Whiteboard", "Videokonferenz"],
                description="Großer Meetingraum für Teamgespräche",
            )
            ok(f"Raum angelegt: {r1.name} [{r1.number}]")

            r2 = room_svc.create(
                name="Projektraum Beta",
                number="1002-B",
                capacity=6,
                location="Gebäude A, 1. OG",
                equipment=["Whiteboard", "Monitor"],
                description="Kompakter Projektraum",
            )
            ok(f"Raum angelegt: {r2.name} [{r2.number}]")
            demo_room_id = r1.id
        except Exception as ex:
            warn(f"Raum konnte nicht angelegt werden: {ex}")
    else:
        demo_room_id = rooms[0].id
        ok(f"{len(rooms)} Räume vorhanden. Nutze: {rooms[0].name}")

    # Assets prüfen/anlegen
    assets = asset_svc.get_all()
    if not assets:
        info("Keine Assets vorhanden – lege Demo-Assets an...")
        try:
            a1 = asset_svc.create(
                name="Beamer Epson EB-X51",
                asset_type=AssetType.BEAMER,
                description="Full-HD Beamer, HDMI/VGA",
                location="Lager EG",
            )
            ok(f"Asset angelegt: {a1.name}")

            a2 = asset_svc.create(
                name="Laptop Dell XPS 15",
                asset_type=AssetType.LAPTOP,
                description="Windows 11, Intel i7",
                location="IT-Raum 003",
            )
            ok(f"Asset angelegt: {a2.name}")
            demo_asset_id = a1.id
        except Exception as ex:
            warn(f"Asset konnte nicht angelegt werden: {ex}")
    else:
        demo_asset_id = assets[0].id
        ok(f"{len(assets)} Assets vorhanden. Nutze: {assets[0].name}")


def demo_user_registration():
    """Szenario 1: Nutzer registrieren."""
    global current_user
    header("SZENARIO 1: Nutzer-Registrierung")

    demo_email = f"demo_{uuid.uuid4().hex[:6]}@replan.de"
    demo_password = "demo123"
    demo_name = "Max Mustermann (Demo)"

    info(f"Registriere Nutzer: {demo_email}")
    try:
        user = user_svc.register(
            name=demo_name,
            email=demo_email,
            password=demo_password,
        )
        current_user = user
        ok(f"Registrierung erfolgreich!")
        ok(f"Name:  {user.name}")
        ok(f"Email: {user.email}")
        ok(f"Rolle: {user.role.value}")
        ok(f"ID:    {user.id}")
    except ValueError as e:
        err(f"Registrierung fehlgeschlagen: {e}")


def demo_user_login():
    """Szenario 2: Login testen."""
    global current_user
    if not current_user:
        warn("Kein Nutzer registriert. Überspringe Login.")
        return

    header("SZENARIO 2: Login")
    demo_email = current_user.email
    demo_password = "demo123"

    info(f"Login mit: {demo_email}")
    try:
        user = user_svc.login(email=demo_email, password=demo_password)
        ok(f"Login erfolgreich! Willkommen, {user.name}!")
    except AuthError as e:
        err(f"Login fehlgeschlagen: {e}")

    info("Teste falsches Passwort...")
    try:
        user_svc.login(email=demo_email, password="falschesPasswort!")
        err("Login hätte fehlschlagen sollen!")
    except AuthError as e:
        ok(f"Falsches Passwort korrekt abgelehnt: {e}")


def demo_list_rooms():
    """Szenario 3: Räume anzeigen."""
    header("SZENARIO 3: Verfügbare Räume anzeigen")
    rooms = room_svc.get_all()
    if not rooms:
        warn("Keine Räume vorhanden.")
        return
    info(f"{len(rooms)} Räume gefunden:")
    for r in rooms:
        equip = ", ".join(r.equipment) if r.equipment else "–"
        print(f"\n    {c(BOLD, r.name)} [{r.number}]")
        print(f"      Kapazität: {r.capacity} Personen")
        print(f"      Standort:  {r.location or '–'}")
        print(f"      Ausstattg: {equip}")


def demo_list_assets():
    """Szenario 4: Assets anzeigen."""
    header("SZENARIO 4: Verfügbare Assets anzeigen")
    assets = asset_svc.get_all()
    if not assets:
        warn("Keine Assets vorhanden.")
        return
    info(f"{len(assets)} Assets gefunden:")
    for a in assets:
        print(f"\n    {c(BOLD, a.name)} [{a.asset_type.value}]")
        print(f"      Standort: {a.location or '–'}")
        print(f"      Beschrg.: {a.description or '–'}")


def demo_book_room():
    """Szenario 5: Raum buchen."""
    global demo_room_id
    if not current_user or not demo_room_id:
        warn("Nutzer oder Raum nicht verfügbar. Überspringe.")
        return

    header("SZENARIO 5: Raum buchen")
    start, end = future_time(hours_from_now=2, duration_hours=2)
    room = room_svc.get_by_id(demo_room_id)
    info(f"Buche: {room.name} [{room.number}]")
    info(f"Zeitraum: {start} → {end}")

    try:
        booking = booking_svc.create_booking(
            user=current_user,
            target_id=demo_room_id,
            target_type=BookingTargetType.ROOM,
            start_time=start,
            end_time=end,
            title="Demo-Teammeeting",
        )
        ok(f"Buchung erfolgreich erstellt!")
        ok(f"Buchungs-ID: {booking.id}")
        ok(f"Titel:       {booking.title}")
        ok(f"Status:      {booking.status.value}")
        return booking
    except BookingConflictError as e:
        err(f"Buchungskonflikt: {e}")
    except ValueError as e:
        err(f"Fehler: {e}")
    return None


def demo_book_asset():
    """Szenario 6: Asset buchen."""
    global demo_asset_id
    if not current_user or not demo_asset_id:
        warn("Nutzer oder Asset nicht verfügbar. Überspringe.")
        return

    header("SZENARIO 6: Asset buchen")
    start, end = future_time(hours_from_now=2, duration_hours=2)
    asset = asset_svc.get_by_id(demo_asset_id)
    info(f"Buche: {asset.name} [{asset.asset_type.value}]")
    info(f"Zeitraum: {start} → {end}")

    try:
        booking = booking_svc.create_booking(
            user=current_user,
            target_id=demo_asset_id,
            target_type=BookingTargetType.ASSET,
            start_time=start,
            end_time=end,
            title="Demo-Präsentation",
        )
        ok(f"Asset-Buchung erfolgreich!")
        ok(f"Buchungs-ID: {booking.id}")
        return booking
    except BookingConflictError as e:
        err(f"Buchungskonflikt: {e}")
    except ValueError as e:
        err(f"Fehler: {e}")
    return None


def demo_double_booking():
    """Szenario 7: Doppelbuchung verhindern (KERNLOGIK)."""
    global demo_room_id
    if not current_user or not demo_room_id:
        warn("Voraussetzungen nicht erfüllt. Überspringe.")
        return

    header("SZENARIO 7: Doppelbuchung verhindern (Kernlogik)")
    start, end = future_time(hours_from_now=2, duration_hours=2)
    room = room_svc.get_by_id(demo_room_id)
    info(f"Versuche denselben Raum nochmals zu buchen: {room.name}")
    info(f"Zeitraum: {start} → {end} (identisch mit vorheriger Buchung)")

    try:
        booking_svc.create_booking(
            user=current_user,
            target_id=demo_room_id,
            target_type=BookingTargetType.ROOM,
            start_time=start,
            end_time=end,
            title="Konflikt-Test",
        )
        err("FEHLER: Doppelbuchung hätte verhindert werden sollen!")
    except BookingConflictError as e:
        ok(f"Doppelbuchung korrekt verhindert!")
        ok(f"Fehlermeldung: {str(e)[:80]}...")


def demo_view_bookings():
    """Szenario 8: Eigene Buchungen anzeigen."""
    if not current_user:
        warn("Kein Nutzer eingeloggt. Überspringe.")
        return

    header("SZENARIO 8: Eigene Buchungen anzeigen")
    bookings = booking_svc.get_user_active_bookings(current_user.id)
    info(f"{len(bookings)} aktive Buchungen für {current_user.name}:")

    for b in bookings:
        target_label = "Raum" if b.target_type.value == "room" else "Asset"
        print(f"\n    {c(BOLD, b.title)} [{target_label}]")
        print(f"      Von:    {b.start_time}")
        print(f"      Bis:    {b.end_time}")
        print(f"      Status: {c(GREEN, b.status.value)}")
        print(f"      ID:     {b.id}")


def demo_cancel_booking():
    """Szenario 9: Buchung stornieren."""
    if not current_user:
        warn("Kein Nutzer eingeloggt. Überspringe.")
        return

    bookings = booking_svc.get_user_active_bookings(current_user.id)
    if not bookings:
        warn("Keine aktiven Buchungen zum Stornieren vorhanden.")
        return

    header("SZENARIO 9: Buchung stornieren")
    booking = bookings[0]
    info(f"Storniere Buchung: '{booking.title}' (ID: {booking.id})")

    try:
        cancelled = booking_svc.cancel_booking(booking.id, current_user)
        ok(f"Buchung erfolgreich storniert!")
        ok(f"Neuer Status: {cancelled.status.value}")
    except Exception as e:
        err(f"Stornierung fehlgeschlagen: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Hauptmenü
# ─────────────────────────────────────────────────────────────────────────────

def interactive_menu():
    """Interaktives Hauptmenü der Terminal-Demo."""
    while True:
        header("RePlan – Terminal Demo")
        if current_user:
            info(f"Eingeloggt als: {c(BOLD, current_user.name)} ({current_user.role.value})")
        else:
            warn("Kein Nutzer eingeloggt.")

        print_menu("Was möchtest du tun?", [
            ("1", "Nutzer registrieren & einloggen"),
            ("2", "Verfügbare Räume anzeigen"),
            ("3", "Verfügbare Assets anzeigen"),
            ("4", "Raum buchen"),
            ("5", "Asset buchen"),
            ("6", "Doppelbuchung testen (Kernlogik)"),
            ("7", "Eigene Buchungen anzeigen"),
            ("8", "Buchung stornieren"),
            ("9", "Kompletten Demo-Durchlauf starten"),
            ("0", c(RED, "Beenden")),
        ])

        choice = get_choice("Auswahl (0-9)")

        if choice == "0":
            print(c(BOLD + GREEN, "\n  Auf Wiedersehen!\n"))
            break
        elif choice == "1":
            demo_user_registration()
            demo_user_login()
        elif choice == "2":
            demo_list_rooms()
        elif choice == "3":
            demo_list_assets()
        elif choice == "4":
            demo_book_room()
        elif choice == "5":
            demo_book_asset()
        elif choice == "6":
            demo_double_booking()
        elif choice == "7":
            demo_view_bookings()
        elif choice == "8":
            demo_cancel_booking()
        elif choice == "9":
            run_full_demo()
        else:
            warn("Ungültige Eingabe. Bitte 0–9 wählen.")

        pause()


def run_full_demo():
    """Führt alle Demo-Szenarien automatisch durch."""
    header("VOLLSTÄNDIGER DEMO-DURCHLAUF")
    info("Alle 9 Szenarien werden nacheinander ausgeführt...")

    demo_setup_seed_data()
    demo_user_registration()
    demo_user_login()
    demo_list_rooms()
    demo_list_assets()
    demo_book_room()
    demo_book_asset()
    demo_double_booking()
    demo_view_bookings()
    demo_cancel_booking()

    header("DEMO ABGESCHLOSSEN")
    ok("Alle Kernfunktionen erfolgreich demonstriert:")
    ok("✓ Nutzer-Registrierung und Login")
    ok("✓ Raum- und Asset-Anzeige")
    ok("✓ Raum-Buchung")
    ok("✓ Asset-Buchung")
    ok("✓ Doppelbuchungs-Prävention (Kernlogik)")
    ok("✓ Eigene Buchungen anzeigen")
    ok("✓ Buchung stornieren")


# ─────────────────────────────────────────────────────────────────────────────
# Einstiegspunkt
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print(c(BOLD + CYAN, "┌─────────────────────────────────────────────────────┐"))
    print(c(BOLD + CYAN, "│   RePlan – Raum- und Ressourcenplanungssystem       │"))
    print(c(BOLD + CYAN, "│   Interaktive Terminal-Demo  v1.0                   │"))
    print(c(BOLD + CYAN, "└─────────────────────────────────────────────────────┘"))

    # Demo-Daten immer vorbereiten
    demo_setup_seed_data()

    import sys
    # --auto Flag für nicht-interaktiven Volldruchlauf (z.B. CI)
    if "--auto" in sys.argv:
        run_full_demo()
    else:
        interactive_menu()
