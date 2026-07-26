import os

from ..models.audit_event import AuditEvent
from .base_repository import JsonRepository

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


class AuditRepository(JsonRepository[AuditEvent]):
    def __init__(self):
        super().__init__(os.path.join(DATA_DIR, "audit_events.json"))

    def from_dict(self, data: dict) -> AuditEvent:
        return AuditEvent.from_dict(data)

    def to_dict(self, obj: AuditEvent) -> dict:
        return obj.to_dict()
