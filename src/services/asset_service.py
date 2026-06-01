"""
Service: AssetService
Verantwortlich für die Verwaltung von Ressourcen/Assets.
"""

import uuid
from typing import List, Optional

from ..models.asset import Asset, AssetType
from ..models.user import User
from ..repositories.asset_repository import AssetRepository
from ..services.user_service import AuthError


class AssetService:
    """
    Verwaltet alle assetbezogenen Operationen (Ressourcen/Geräte).

    Verantwortlichkeiten:
        - Assets anlegen, lesen, aktualisieren, deaktivieren (CRUD)
        - Filterung nach Typ
    """

    def __init__(self, asset_repository: AssetRepository = None):
        self._repo = asset_repository or AssetRepository()

    def get_all(self) -> List[Asset]:
        return self._repo.find_active()

    def get_by_id(self, asset_id: str) -> Optional[Asset]:
        asset = self._repo.find_by_id(asset_id)
        if asset and not asset.is_active:
            return None
        return asset

    def get_by_type(self, asset_type: AssetType) -> List[Asset]:
        return self._repo.find_by_type(asset_type)

    def create(
        self,
        name: str,
        asset_type: AssetType,
        description: str = "",
        location: str = "",
        requesting_user: User = None,
    ) -> Asset:
        """Legt ein neues Asset an. Erfordert Admin-Rechte."""
        if requesting_user and not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Assets anlegen.")
        if not name or not name.strip():
            raise ValueError("Asset-Name darf nicht leer sein.")

        asset = Asset(
            id=str(uuid.uuid4()),
            name=name.strip(),
            asset_type=asset_type,
            description=description,
            location=location,
        )
        return self._repo.save(asset)

    def update(
        self,
        asset_id: str,
        requesting_user: User,
        name: str = None,
        asset_type: AssetType = None,
        description: str = None,
        location: str = None,
    ) -> Asset:
        """Aktualisiert ein Asset. Erfordert Admin-Rechte."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Assets bearbeiten.")
        asset = self._repo.find_by_id(asset_id)
        if not asset or not asset.is_active:
            raise ValueError(f"Asset mit ID '{asset_id}' nicht gefunden.")

        if name is not None:
            asset.name = name.strip()
        if asset_type is not None:
            asset.asset_type = asset_type
        if description is not None:
            asset.description = description
        if location is not None:
            asset.location = location

        self._repo.update(asset)
        return asset

    def deactivate(self, asset_id: str, requesting_user: User) -> Asset:
        """Deaktiviert ein Asset (Soft-Delete). Erfordert Admin-Rechte."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Assets deaktivieren.")
        asset = self._repo.find_by_id(asset_id)
        if not asset or not asset.is_active:
            raise ValueError(f"Asset mit ID '{asset_id}' nicht gefunden.")
        asset.is_active = False
        self._repo.update(asset)
        return asset
