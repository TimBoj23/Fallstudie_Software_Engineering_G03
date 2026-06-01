"""Repository: Room"""
import os
from ..models.room import Room
from .base_repository import JsonRepository

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

class RoomRepository(JsonRepository[Room]):
    def __init__(self):
        super().__init__(os.path.join(DATA_DIR, "rooms.json"))

    def from_dict(self, data: dict) -> Room:
        return Room.from_dict(data)

    def to_dict(self, obj: Room) -> dict:
        return obj.to_dict()

    def find_active(self) -> list:
        return [r for r in self.find_all() if r.is_active]

    def find_by_capacity(self, min_capacity: int) -> list:
        return [r for r in self.find_active() if r.capacity >= min_capacity]

    def find_by_location(self, location: str) -> list:
        return [r for r in self.find_active()
                if location.lower() in r.location.lower()]

    def number_exists(self, number: str, exclude_id: str = None) -> bool:
        return any(
            r.number == number and r.id != exclude_id
            for r in self.find_active()
        )
