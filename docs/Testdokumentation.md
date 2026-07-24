# Testdokumentation RePlan

## Automatisierte Tests

Die Backend-Tests liegen im Ordner `tests/` und werden mit `pytest` ausgeführt.

```bash
pytest
```

Aktueller Schwerpunkt:

| Bereich | Beispiele |
| --- | --- |
| Nutzer | Registrierung, Login, Passwortvalidierung, doppelte E-Mail-Adressen |
| Räume | Anlegen, Aktualisieren, Deaktivieren, Kapazitätsfilter |
| Assets | Anlegen, Suchen, Filtern, Deaktivieren |
| Buchungen | Erfolgreiche Buchung, Konfliktprüfung, Stornierung, Rechteprüfung |
| Sitzplätze | Direkte Sitzplatzbuchung, automatische Zuweisung, parallele Sitzplatzkonflikte |
| Randfälle | Startzeit nach Endzeit, gleiche Zeitpunkte, überschneidende Buchungen, stornierte Buchungen |

## Manuelle Tests

| Ablauf | Erwartung |
| --- | --- |
| Registrierung und Login | Nutzer kann Konto erstellen und sich anmelden. |
| Raum buchen | Seminarraum ist im Zeitraum für andere blockiert. |
| Arbeitsplatz buchen | Nur Sitzplätze aus Shared-Desk-Räumen werden angeboten. |
| Asset buchen | Asset ist im Zeitraum nicht doppelt buchbar. |
| Admin-Nutzerverwaltung | Admin sieht Nutzer mit Bildern und kann Rollen bearbeiten. |
| Passwort vergessen | Reset ist über E-Mail oder Token-MVP möglich. |
| Buchungsübersicht | Nutzer sehen sprechende Namen statt technischer IDs. |

## Testergebnis

Der aktuelle Stand wurde mit `pytest` und `npm run build` geprüft. Frontend-End-to-End-Tests sind als sinnvoller nächster Schritt dokumentiert, aber nicht Bestandteil des aktuellen MVP.
