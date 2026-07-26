"""Unveränderlicher Eintrag des administrativen Änderungsprotokolls."""

from dataclasses import dataclass, field
from typing import Dict

from ..utils.time import utc_now_iso


@dataclass
class AuditEvent:
    id: str
    actor_user_id: str
    action: str
    entity_type: str
    entity_id: str
    summary: str
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "actor_user_id": self.actor_user_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "summary": self.summary,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditEvent":
        return cls(
            id=data["id"],
            actor_user_id=data.get("actor_user_id", ""),
            action=data.get("action", ""),
            entity_type=data.get("entity_type", ""),
            entity_id=data.get("entity_id", ""),
            summary=data.get("summary", ""),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", utc_now_iso()),
        )
