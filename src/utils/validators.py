"""
Utils: Validators
Eingabevalidierungshelfer für Routes und Services.
"""
from datetime import datetime


def validate_iso_datetime(value: str, field_name: str = "Zeitangabe") -> str:
    """Validiert und normalisiert einen ISO-8601 Datetime-String."""
    if not value:
        raise ValueError(f"{field_name} darf nicht leer sein.")
    try:
        datetime.fromisoformat(value)
        return value
    except ValueError:
        raise ValueError(
            f"'{field_name}' muss im ISO-8601 Format sein (z. B. '2026-06-15T09:00:00')."
        )


def validate_required_string(value: str, field_name: str) -> str:
    """Validiert, dass ein String nicht leer ist."""
    if not value or not str(value).strip():
        raise ValueError(f"'{field_name}' darf nicht leer sein.")
    return str(value).strip()


def validate_positive_int(value, field_name: str) -> int:
    """Validiert, dass ein Wert eine positive ganze Zahl ist."""
    try:
        v = int(value)
        if v <= 0:
            raise ValueError()
        return v
    except (TypeError, ValueError):
        raise ValueError(f"'{field_name}' muss eine positive ganze Zahl sein.")
