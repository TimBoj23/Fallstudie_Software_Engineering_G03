"""Repository: Seat"""

import os
from typing import List

from ..models.seat import Seat
from .base_repository import JsonRepository

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


class SeatRepository(JsonRepository[Seat]):
    def __init__(self):
        super().__init__(os.path.join(DATA_DIR, "seats.json"))

    def from_dict(self, data: dict) -> Seat:
        return Seat.from_dict(data)

    def to_dict(self, obj: Seat) -> dict:
        return obj.to_dict()

    def find_active(self) -> List[Seat]:
        return [s for s in self.find_all() if s.is_active]

    def find_by_room(self, room_id: str, active_only: bool = True) -> List[Seat]:
        seats = [s for s in self.find_all() if s.room_id == room_id]
        if active_only:
            seats = [s for s in seats if s.is_active]
        return seats

    def label_exists(self, room_id: str, label: str, exclude_id: str = None) -> bool:
        normalized = label.strip().lower()
        return any(
            s.room_id == room_id
            and s.label.strip().lower() == normalized
            and s.id != exclude_id
            and s.is_active
            for s in self.find_all()
        )
