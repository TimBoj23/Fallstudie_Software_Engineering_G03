# Testdokumentation RePlan

## Automatisierte Tests

Die Backend-Tests liegen im Ordner `tests/` und werden mit `pytest` ausgeführt. Kleine Frontend-Logiktests liegen unter `frontend/src/tests/` und werden mit Vitest ausgeführt.

```bash
pytest
```

```bash
cd frontend
npm test
```

Aktueller Schwerpunkt:

| Bereich | Beispiele |
| --- | --- |
| Nutzer | Registrierung, Login, Profiländerung, eigener Passwortwechsel, anonymisierter Soft-Delete, E-Mail-Wiederverwendung |
| Räume | Anlegen, Aktualisieren, Deaktivieren, Kapazitätsfilter |
| Assets | Anlegen, Suchen, Filtern, Deaktivieren |
| Buchungen | Erfolgreiche Buchung, Konfliktprüfung, Bearbeitung, Verlängerung, Stornierung, Rechteprüfung |
| Sitzplätze | Direkte Sitzplatzbuchung, automatische Zuweisung, parallele Sitzplatzkonflikte |
| Randfälle | Startzeit nach Endzeit, gleiche Zeitpunkte, überschneidende Buchungen, stornierte Buchungen |
| Frontend | Kalenderfarben, Normalisierung von Einladungsadressen sowie getrennte Raum-/Shared-Office-Auswahl |
| Kalenderexport | UTC-Zeiten und korrekt maskierte iCalendar-Inhalte |
| Anwesenheit | Check-in, Check-out, verfrühter Check-in und Admin-Belegung |
| Neue Sprint-Features | Einladungscodes, Einladungskapazität, sichere Einladungsliste, Serienbearbeitung, In-App-Hinweise, Demo-Reset und Auslastungsstatistik |

## Manuelle Tests

| Ablauf | Erwartung |
| --- | --- |
| Registrierung und Login | Nutzer kann Konto erstellen und sich anmelden. |
| Raum buchen | Seminarraum ist im Zeitraum für andere blockiert. |
| Arbeitsplatz buchen | Nur Arbeitsplätze aus Shared Offices werden angeboten; Sitzplan und automatische Auswahl verwenden dieselbe Konfliktlogik. |
| Asset buchen | Asset ist im Zeitraum nicht doppelt buchbar. |
| Admin-Nutzerverwaltung | Admin sieht Nutzer mit Bildern und kann Rollen bearbeiten. |
| Passwort vergessen | Reset ist über E-Mail oder Token-MVP möglich. |
| Buchungsübersicht | Nutzer sehen sprechende Namen statt technischer IDs. |
| Seminareinladung | Externe Person kann nur mit gültigem Code, Passwort und – falls vorhanden – eingeladener E-Mail beitreten. |
| Buchung bearbeiten | Nur zukünftige aktive Buchungen werden gespeichert; Konflikte werden abgewiesen. |
| Buchung verlängern | Verlängerung gelingt nur, wenn der Folgezeitraum frei ist. |
| Serienverwaltung | Einzeltermin oder aktueller und alle folgenden Termine können geändert/storniert werden. |
| Demo-Reset | Passwort, Bestätigungstext und Adminrolle sind erforderlich; Ressourcen und Admins bleiben erhalten. |
| Aktuelle Raumbelegung | Admin sieht nur eingecheckte Personen in gerade laufenden Buchungen. |
| Dark Mode | Umschalter wechselt das Farbschema und behält die Auswahl nach Neuladen. |
| Admin-Ressourcen | Räume, Sitzplätze und Assets können bearbeitet und deaktiviert werden. |
| Kalenderexport | Exportierte `.ics`-Datei lässt sich in einer Kalenderanwendung öffnen. |
| Kontoeinstellungen | Name, E-Mail und Profilbild werden aktualisiert; Rollen bleiben unverändert. |
| Eigenes Passwort | Änderung gelingt nur mit richtigem aktuellem Passwort. |
| Konto löschen | Bestätigung und Passwort sind nötig; danach verliert die Sitzung den Zugriff und die E-Mail kann erneut registriert werden. |

## Testergebnis

Der aktuelle Stand wurde am 27.07.2026 mit **87 bestandenen Backend-Tests**, **7 bestandenen Frontend-Tests** und einem erfolgreichen Produktions-Build geprüft. Browserbasierte End-to-End-Tests bleiben ein sinnvoller nächster Ausbauschritt.
