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
        location: str = "",
        equipment: list = None,
        description: str = "",
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
            location=location,
            equipment=equipment or [],
            description=description,
        )
        return self._repo.save(room)

    def update(
        self,
        room_id: str,
        requesting_user: User,
        name: str = None,
        capacity: int = None,
        location: str = None,
        equipment: list = None,
        description: str = None,
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
        if location is not None:
            room.location = location
        if equipment is not None:
            room.equipment = equipment
        if description is not None:
            room.description = description

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
