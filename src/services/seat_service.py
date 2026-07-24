"""
Service: SeatService
Verantwortlich für die Verwaltung von Sitzplätzen innerhalb von Räumen.
"""

import uuid
from typing import List, Optional

from ..models.seat import Seat
from ..models.user import User
from ..repositories.room_repository import RoomRepository
from ..repositories.seat_repository import SeatRepository
from ..services.user_service import AuthError


class SeatService:
    """Verwaltet sitzplatzbezogene CRUD-Operationen."""

    def __init__(
        self,
        seat_repository: SeatRepository = None,
        room_repository: RoomRepository = None,
    ):
        self._repo = seat_repository or SeatRepository()
        self._room_repo = room_repository or RoomRepository()

    def get_all(self) -> List[Seat]:
        return self._repo.find_active()

    def get_by_id(self, seat_id: str) -> Optional[Seat]:
        seat = self._repo.find_by_id(seat_id)
        if seat and not seat.is_active:
            return None
        return seat

    def get_by_room(self, room_id: str) -> List[Seat]:
        self._validate_room_exists(room_id)
        return self._repo.find_by_room(room_id)

    def create(
        self,
        room_id: str,
        label: str,
        description: str = "",
        image_url: str = "",
        monitor_count: int = 1,
        requesting_user: User = None,
    ) -> Seat:
        """Legt einen neuen Sitzplatz an. Erfordert Admin-Rechte."""
        if requesting_user and not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Sitzplätze anlegen.")
        self._validate_room_exists(room_id)
        if not label or not label.strip():
            raise ValueError("Sitzplatzbezeichnung darf nicht leer sein.")
        if self._repo.label_exists(room_id, label):
            raise ValueError(f"Sitzplatz '{label}' existiert in diesem Raum bereits.")
        if monitor_count < 1:
            raise ValueError("Monitoranzahl muss mindestens 1 sein.")

        seat = Seat(
            id=str(uuid.uuid4()),
            room_id=room_id,
            label=label.strip(),
            description=description,
            image_url=image_url,
            monitor_count=monitor_count,
        )
        return self._repo.save(seat)

    def update(
        self,
        seat_id: str,
        requesting_user: User,
        label: str = None,
        description: str = None,
        image_url: str = None,
        monitor_count: int = None,
    ) -> Seat:
        """Aktualisiert einen Sitzplatz. Erfordert Admin-Rechte."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Sitzplätze bearbeiten.")
        seat = self._repo.find_by_id(seat_id)
        if not seat or not seat.is_active:
            raise ValueError(f"Sitzplatz mit ID '{seat_id}' nicht gefunden.")

        if label is not None:
            if not label.strip():
                raise ValueError("Sitzplatzbezeichnung darf nicht leer sein.")
            if self._repo.label_exists(seat.room_id, label, exclude_id=seat.id):
                raise ValueError(f"Sitzplatz '{label}' existiert in diesem Raum bereits.")
            seat.label = label.strip()
        if description is not None:
            seat.description = description
        if image_url is not None:
            seat.image_url = image_url
        if monitor_count is not None:
            if monitor_count < 1:
                raise ValueError("Monitoranzahl muss mindestens 1 sein.")
            seat.monitor_count = monitor_count

        self._repo.update(seat)
        return seat

    def deactivate(self, seat_id: str, requesting_user: User) -> Seat:
        """Deaktiviert einen Sitzplatz (Soft-Delete). Erfordert Admin-Rechte."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Sitzplätze deaktivieren.")
        seat = self._repo.find_by_id(seat_id)
        if not seat or not seat.is_active:
            raise ValueError(f"Sitzplatz mit ID '{seat_id}' nicht gefunden.")
        seat.is_active = False
        self._repo.update(seat)
        return seat

    def search(self, query: str = "", room_id: str = None) -> List[Seat]:
        seats = self._repo.find_active()
        if room_id:
            seats = [s for s in seats if s.room_id == room_id]
        if query:
            q = query.lower().strip()
            seats = [
                s for s in seats
                if q in s.label.lower() or q in s.description.lower()
            ]
        return seats

    def search_in_shared_desk_rooms(self, query: str = "", room_id: str = None) -> List[Seat]:
        """Sitzplatzsuche für Buchungen: nur Shared-Desk-Räume werden berücksichtigt."""
        shared_room_ids = {
            room.id for room in self._room_repo.find_active()
            if getattr(room, "room_type", "seminarraum") == "shared_desk"
        }
        seats = self.search(query=query, room_id=room_id)
        return [seat for seat in seats if seat.room_id in shared_room_ids]

    def _validate_room_exists(self, room_id: str) -> None:
        room = self._room_repo.find_by_id(room_id)
        if not room or not room.is_active:
            raise ValueError(f"Raum mit ID '{room_id}' nicht gefunden oder nicht verfügbar.")
