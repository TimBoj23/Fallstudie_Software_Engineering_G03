from datetime import datetime, timezone

import pytest

from src.utils.time import parse_iso_datetime


def test_naive_browser_time_is_interpreted_as_replan_local_time(monkeypatch):
    monkeypatch.setenv("REPLAN_TIMEZONE", "Europe/Berlin")

    parsed = parse_iso_datetime("2026-07-27T16:00:00")

    assert parsed == datetime(2026, 7, 27, 14, 0, tzinfo=timezone.utc)


def test_offset_aware_time_is_normalized_to_utc(monkeypatch):
    monkeypatch.setenv("REPLAN_TIMEZONE", "Europe/Berlin")

    parsed = parse_iso_datetime("2026-07-27T16:00:00+02:00")

    assert parsed == datetime(2026, 7, 27, 14, 0, tzinfo=timezone.utc)


def test_unknown_replan_timezone_is_rejected(monkeypatch):
    monkeypatch.setenv("REPLAN_TIMEZONE", "Nowhere/Invalid")

    with pytest.raises(ValueError, match="Unbekannte REPLAN_TIMEZONE"):
        parse_iso_datetime("2026-07-27T16:00:00")
