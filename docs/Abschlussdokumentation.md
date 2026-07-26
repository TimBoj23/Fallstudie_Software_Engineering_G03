# Abschlussdokumentation RePlan

## Aktueller Funktionsumfang

- Buchung von Seminarräumen, Shared-Desk-Sitzplätzen und Assets
- Konfliktprüfung gegen Doppelbuchungen
- Nutzerregistrierung, Login, Logout und Passwort-Reset
- Signierte, zeitlich begrenzte Bearer-Tokens statt offen übertragener Nutzer-IDs
- Passwortgeschützte Seminarbuchungen mit Einladungen und externem Beitritt
- Admin-Verwaltung für Nutzer, Räume, Sitzplätze, Assets und Buchungen
- Aktuelle, nach Raum gruppierte Belegungsübersicht im Admin-Bereich
- Echter Check-in/Check-out als Grundlage der Belegungsübersicht
- Filter- und Suchfunktionen für die wichtigsten Übersichten
- Bilder für Nutzer, Räume, Sitzplätze und Assets
- Dark Mode mit gespeicherter Nutzerauswahl
- Kalenderexport eigener Buchungen im iCalendar-Format
- Bearbeiten und Soft-Delete von Räumen, Sitzplätzen und Assets im Admin-Bereich
- SQLite-backed Persistenzschicht mit JSON-Migration

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
| Buchungen verwalten | Nutzer sieht eigene Buchungen und kann diese stornieren. |
| Admin verwaltet Nutzer | Admin legt Nutzer an, bearbeitet Rollen und setzt Passwörter zurück. |
| Admin prüft Buchungen | Admin sieht alle Buchungen inklusive Nutzerkontext. |
| Seminarteilnahme | Externe Personen treten mit Buchungscode, E-Mail und Passwort bei. |
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
- `docs/Engineering_Reflexion.md`
- `docs/KI_Nutzung.md`
- `docs/Qualitaetssheet.html`
