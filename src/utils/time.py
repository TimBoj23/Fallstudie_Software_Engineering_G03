"""Zeit-Helfer für konsistente UTC-Zeitstempel."""

import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DEFAULT_LOCAL_TIMEZONE = "Europe/Berlin"


def utc_now() -> datetime:
    """Gibt den aktuellen Zeitpunkt timezone-aware in UTC zurück."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Gibt den aktuellen UTC-Zeitpunkt als ISO-8601-String zurück."""
    return utc_now().isoformat()


def parse_iso_datetime(value: str) -> datetime:
    """Parst ISO-8601 und normalisiert den Zeitpunkt auf UTC.

    ``datetime-local``-Felder senden keine Zeitzone. Solche Legacy-Werte werden
    als lokale RePlan-Zeit interpretiert; neue Clients sollten einen Offset oder
    ``Z`` mitsenden. Die lokale Zone lässt sich über ``REPLAN_TIMEZONE`` ändern.
    """
    # Python 3.9 akzeptiert den ISO-8601-UTC-Suffix ``Z`` noch nicht direkt.
    # ``+00:00`` beschreibt denselben Zeitpunkt und funktioniert ab Python 3.7.
    normalized = f"{value[:-1]}+00:00" if isinstance(value, str) and value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        timezone_name = os.environ.get("REPLAN_TIMEZONE", DEFAULT_LOCAL_TIMEZONE)
        try:
            parsed = parsed.replace(tzinfo=ZoneInfo(timezone_name))
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unbekannte REPLAN_TIMEZONE: '{timezone_name}'.") from exc
    return parsed.astimezone(timezone.utc)
