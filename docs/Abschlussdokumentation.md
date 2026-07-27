# Abschlussdokumentation RePlan

## Aktueller Funktionsumfang

- Buchung von Seminarräumen, Shared-Office-Arbeitsplätzen und Assets
- Konfliktprüfung gegen Doppelbuchungen
- Nutzerregistrierung, Login, Logout und Passwort-Reset
- Signierte, zeitlich begrenzte Bearer-Tokens statt offen übertragener Nutzer-IDs
- Passwortgeschützte Raumreservierungen mit kurzem Einladungscode, manuell teilbarem Link und erlaubter E-Mail-Liste
- Bearbeiten und Verlängern eigener zukünftiger Buchungen mit erneuter Konfliktprüfung
- Bearbeiten oder Stornieren einzelner und zukünftiger Serientermine
- Grafischer Shared-Office-Sitzplan mit Teilbelegung und freier Platzzahl
- In-App-Benachrichtigungen ohne echten E-Mail-Versand
- Admin-Verwaltung für Nutzer, Räume, Sitzplätze, Assets und Buchungen
- Aktuelle, nach Raum gruppierte Belegungsübersicht im Admin-Bereich
- Echter Check-in/Check-out als Grundlage der Belegungsübersicht
- Filter- und Suchfunktionen für die wichtigsten Übersichten
- Bilder für Nutzer, Räume, Sitzplätze und Assets
- Dark Mode mit gespeicherter Nutzerauswahl
- Kalenderexport eigener Buchungen im iCalendar-Format
- Bearbeiten und Soft-Delete von Räumen, Sitzplätzen und Assets im Admin-Bereich
- SQLite-backed Persistenzschicht mit JSON-Migration
- Abgesicherter Demo-Reset für Buchungen, Statistik, Protokoll und Nicht-Admin-Konten

## Aktuelle Architektur

```text
frontend/ React + Vite
    |
    | REST API
    v
app.py / Flask Blueprints
    |
src/routes      HTTP-Endpunkte
src/services    Geschäftslogik
src/repositories Datenzugriff
src/models      Domänenmodelle
data/           Demo-Daten, Bilder, SQLite
tests/          Backend-Tests
```

## Aktualisierte Use Cases

| Use Case | Kurzbeschreibung |
| --- | --- |
| Raum buchen | Nutzer reserviert einen Seminarraum für einen Zeitraum. |
| Sitzplatz buchen | Nutzer bucht einen konkreten oder automatisch zugewiesenen Arbeitsplatz. |
| Asset buchen | Nutzer reserviert Ausstattung wie Laptop, Beamer oder Mikrofon. |
| Buchungen verwalten | Nutzer sieht, bearbeitet, verlängert oder storniert eigene Buchungen und Serien. |
| Admin verwaltet Nutzer | Admin legt Nutzer an, bearbeitet Rollen und setzt Passwörter zurück. |
| Admin prüft Buchungen | Admin sieht alle Buchungen inklusive Nutzerkontext. |
| Seminarteilnahme | Eingeladene Personen treten mit kurzem Einladungscode, erlaubter E-Mail und Passwort bei. |
| Shared Office buchen | Nutzer lässt einen freien Arbeitsplatz automatisch zuweisen oder wählt ihn im grafischen Sitzplan. |
| Raumbelegung prüfen | Admin sieht ausschließlich aktuell eingecheckte Buchungsinhaber. |

## Offene Punkte

- Echtes relationales SQL-Schema mit Tabellen für Nutzer, Räume, Sitzplätze, Assets und Buchungen
- Produktiver E-Mail-Versand über SMTP oder externen Maildienst
- Frontend-End-to-End-Tests
- Refresh-Tokens und serverseitige Sperrliste für vorzeitig widerrufene Auth-Tokens
- Deployment-Konfiguration außerhalb der lokalen Demo

## Verweise

- `docs/Konzeptionsplan.md`
- `docs/UML.md`
- `docs/Testdokumentation.md`
- `docs/Sprint_III_Engineering_Reflexion.md`
- `docs/KI_Nutzung.md`
- `docs/Qualitaetsbericht.html`
