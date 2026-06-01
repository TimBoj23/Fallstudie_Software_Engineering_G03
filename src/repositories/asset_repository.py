"""Repository: Asset"""
import os
from ..models.asset import Asset, AssetType
from .base_repository import JsonRepository

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

class AssetRepository(JsonRepository[Asset]):
    def __init__(self):
        super().__init__(os.path.join(DATA_DIR, "assets.json"))

    def from_dict(self, data: dict) -> Asset:
        return Asset.from_dict(data)

    def to_dict(self, obj: Asset) -> dict:
        return obj.to_dict()

    def find_active(self) -> list:
        return [a for a in self.find_all() if a.is_active]

    def find_by_type(self, asset_type: AssetType) -> list:
        return [a for a in self.find_active() if a.asset_type == asset_type]
