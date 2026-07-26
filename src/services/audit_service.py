"""Zentrale, bewusst metadata-arme Audit-Protokollierung."""

import uuid

from ..models.audit_event import AuditEvent
from ..repositories.audit_repository import AuditRepository
from ..repositories.user_repository import UserRepository
from .user_service import AuthError


class AuditService:
    def __init__(self, repository=None, user_repository=None):
        self._repo = repository or AuditRepository()
        self._user_repo = user_repository or UserRepository()

    def record(self, actor_user_id: str, action: str, entity_type: str, entity_id: str, summary: str, metadata=None):
        return self._repo.save(AuditEvent(
            id=str(uuid.uuid4()),
            actor_user_id=actor_user_id or "system",
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            summary=summary,
            metadata=metadata or {},
        ))

    def list_events(self, requesting_user, limit=100, action="", entity_type=""):
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können das Änderungsprotokoll einsehen.")
        events = self._repo.find_all()
        if action:
            events = [event for event in events if event.action == action]
        if entity_type:
            events = [event for event in events if event.entity_type == entity_type]
        events.sort(key=lambda event: event.created_at, reverse=True)
        result = []
        for event in events[:max(1, min(int(limit or 100), 500))]:
            data = event.to_dict()
            actor = self._user_repo.find_by_id(event.actor_user_id)
            data["actor_name"] = actor.name if actor else "System"
            data["actor_email"] = actor.email if actor else ""
            result.append(data)
        return result
