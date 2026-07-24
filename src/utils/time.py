"""Zeit-Helfer für konsistente UTC-Zeitstempel."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Gibt den aktuellen Zeitpunkt timezone-aware in UTC zurück."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Gibt den aktuellen UTC-Zeitpunkt als ISO-8601-String zurück."""
    return utc_now().isoformat()


def parse_iso_datetime(value: str) -> datetime:
    """Parst ISO-8601 und ergänzt bei naiven Werten UTC als Zeitzone."""
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
