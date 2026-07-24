"""
Service: RoomService
Verantwortlich für die Verwaltung von Räumen.
Admin-Operationen (create/update/delete) prüfen Nutzerrechte.
"""

import uuid
from typing import List, Optional

from ..models.room import Room
from ..models.user import User
from ..repositories.room_repository import RoomRepository
from ..services.user_service import AuthError


class RoomService:
    """
    Verwaltet alle raumbezogenen Operationen.

    Verantwortlichkeiten:
        - Räume anlegen, lesen, aktualisieren, deaktivieren (CRUD)
        - Verfügbare Räume für einen Zeitraum ermitteln
          (in Zusammenarbeit mit BookingService)
        - Kapazitäts- und Standortfilterung
    """

    def __init__(self, room_repository: RoomRepository = None):
        self._repo = room_repository or RoomRepository()

    def get_all(self) -> List[Room]:
        """Gibt alle aktiven Räume zurück."""
        return self._repo.find_active()

    def get_by_id(self, room_id: str) -> Optional[Room]:
        """Gibt einen Raum anhand seiner ID zurück."""
        room = self._repo.find_by_id(room_id)
        if room and not room.is_active:
            return None
        return room

    def create(
        self,
        name: str,
        number: str,
        capacity: int,
        room_type: str = "seminarraum",
        location: str = "",
        equipment: list = None,
        description: str = "",
        image_url: str = "",
        requesting_user: User = None,
    ) -> Room:
        """
        Legt einen neuen Raum an. Erfordert Admin-Rechte.

        Args:
            name:             Raumbezeichnung
            number:           Raumnummer (muss eindeutig sein)
            capacity:         Kapazität (muss > 0 sein)
            location:         Standort
            equipment:        Ausstattungsliste
            description:      Beschreibung
            requesting_user:  Der anfragende Nutzer (muss Admin sein)

        Raises:
            AuthError:   Kein Admin
            ValueError:  Ungültige Eingaben oder Raumnummer bereits vergeben
        """
        if requesting_user and not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Räume anlegen.")
        if not name or not name.strip():
            raise ValueError("Raumname darf nicht leer sein.")
        if not number or not number.strip():
            raise ValueError("Raumnummer darf nicht leer sein.")
        if capacity <= 0:
            raise ValueError("Kapazität muss größer als 0 sein.")
        if self._repo.number_exists(number):
            raise ValueError(f"Raumnummer '{number}' ist bereits vergeben.")

        room = Room(
            id=str(uuid.uuid4()),
            name=name.strip(),
            number=number.strip(),
            capacity=capacity,
            room_type=self._normalize_room_type(room_type),
            location=location,
            equipment=equipment or [],
            description=description,
            image_url=image_url,
        )
        return self._repo.save(room)

    def update(
        self,
        room_id: str,
        requesting_user: User,
        name: str = None,
        capacity: int = None,
        room_type: str = None,
        location: str = None,
        equipment: list = None,
        description: str = None,
        image_url: str = None,
    ) -> Room:
        """Aktualisiert einen Raum. Erfordert Admin-Rechte."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Räume bearbeiten.")
        room = self._repo.find_by_id(room_id)
        if not room or not room.is_active:
            raise ValueError(f"Raum mit ID '{room_id}' nicht gefunden.")

        if name is not None:
            room.name = name.strip()
        if capacity is not None:
            if capacity <= 0:
                raise ValueError("Kapazität muss größer als 0 sein.")
            room.capacity = capacity
        if room_type is not None:
            room.room_type = self._normalize_room_type(room_type)
        if location is not None:
            room.location = location
        if equipment is not None:
            room.equipment = equipment
        if description is not None:
            room.description = description
        if image_url is not None:
            room.image_url = image_url

        self._repo.update(room)
        return room

    def deactivate(self, room_id: str, requesting_user: User) -> Room:
        """Deaktiviert einen Raum (Soft-Delete). Erfordert Admin-Rechte."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Räume deaktivieren.")
        room = self._repo.find_by_id(room_id)
        if not room or not room.is_active:
            raise ValueError(f"Raum mit ID '{room_id}' nicht gefunden.")
        room.is_active = False
        self._repo.update(room)
        return room

    def filter_by_capacity(self, min_capacity: int) -> List[Room]:
        return self._repo.find_by_capacity(min_capacity)

    def search(
        self,
        query: str = "",
        location: str = "",
        min_capacity: int = None,
        room_type: str = "",
        equipment: list = None,
    ) -> List[Room]:
        """Backend-Such- und Filterlogik für Räume."""
        rooms = self.get_all()
        if query:
            q = query.lower().strip()
            rooms = [
                r for r in rooms
                if q in r.name.lower()
                or q in r.number.lower()
                or q in r.location.lower()
                or q in r.description.lower()
            ]
        if location:
            loc = location.lower().strip()
            rooms = [r for r in rooms if loc in r.location.lower()]
        if min_capacity is not None:
            rooms = [r for r in rooms if r.capacity >= min_capacity]
        if room_type:
            normalized_type = self._normalize_room_type(room_type)
            rooms = [r for r in rooms if r.room_type == normalized_type]
        if equipment:
            wanted = [e.lower().strip() for e in equipment if e.strip()]
            rooms = [
                r for r in rooms
                if all(
                    any(item == existing.lower() for existing in r.equipment)
                    for item in wanted
                )
            ]
        return rooms

    def get_shared_desk_rooms(self) -> List[Room]:
        """Gibt nur Räume zurück, die für Arbeitsplatz-/Sitzplatzbuchungen gedacht sind."""
        return [room for room in self.get_all() if room.room_type == "shared_desk"]

    def _normalize_room_type(self, room_type: str) -> str:
        value = (room_type or "seminarraum").strip().lower()
        aliases = {
            "arbeitsplatz": "shared_desk",
            "shared desk": "shared_desk",
            "shared-desk": "shared_desk",
            "seminar": "seminarraum",
            "seminar_room": "seminarraum",
            "meeting": "meetingraum",
        }
        value = aliases.get(value, value)
        allowed = {"shared_desk", "seminarraum", "meetingraum", "studio"}
        if value not in allowed:
            raise ValueError("room_type muss shared_desk, seminarraum, meetingraum oder studio sein.")
        return value
