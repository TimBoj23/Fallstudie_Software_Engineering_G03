# Abschlussdokumentation RePlan

**Stand:** 28.07.2026

## Ergebnis

RePlan ist als lokale Fullstack-Demo mit Flask-Backend und React/Vite-Frontend lauffähig. Die Anwendung trennt Räume, Shared Offices und Ausstattung verständlich, verhindert Überschneidungen zentral im Backend und bietet Nutzenden sowie Admins passende Arbeitsabläufe.

## Umgesetzter Funktionsumfang

- Registrierung, Login, Logout und signierte, zeitlich begrenzte Bearer-Tokens
- Passwort-Reset als lokaler Token-MVP; kein echter E-Mail-Versand
- Kontoeinstellungen für Name, E-Mail, Profilbild, Passwort und sichere Kontolöschung
- Wiederverwendung einer E-Mail-Adresse nach eigener Kontolöschung
- Buchung von ganzen Räumen, konkreten oder automatisch zugewiesenen Shared-Office-Plätzen und Assets
- Zentrale Konfliktprüfung gegen Doppelbuchungen und unzulässige parallele Sitzplatzbuchungen
- Grafische Zeit- und Verfügbarkeitsansichten sowie Shared-Office-Sitzplan
- Bearbeiten, Kopieren, Verlängern und Stornieren eigener zukünftiger Buchungen
- Wöchentliche Serien sowie getrennte Bearbeitung/Stornierung einzelner und folgender Termine
- Passwortgeschützte Einladungen mit kurzem Code, manuell teilbarem Link und optionaler E-Mail-Freigabeliste
- In-App-Benachrichtigungen mit Löschfunktion, bewusst ohne Versand an externe Postfächer
- Check-in per Oberfläche oder QR-Code, manueller Check-out und automatischer Check-out nach Buchungsende
- iCalendar-Export einzelner Buchungen
- kontobezogene Favoritenübersicht und Dark Mode mit gespeicherter Auswahl
- Admin-Verwaltung für Nutzer, Rollen, Räume, Sitzplätze, Assets und Buchungen
- Admin-Ansichten für aktuelle Belegung, geplante und tatsächliche Nutzung, No-Shows, Auslastungsstatistik und Audit-Protokoll
- Abgesicherter Demo-Reset für Buchungen, Statistik, Protokoll und Nicht-Admin-Konten
- SQLite-backed Repository mit einmaliger Migration vorhandener JSON-Daten
- Idempotentes Seed-Skript für gemeinsame Demo-Ressourcen, Bilder und vier Demo-Admins

## Architektur

```text
React/Vite-Frontend (localhost:5173)
              |
              | REST/JSON + Bearer-Token
              v
Flask-App / Blueprints (localhost:5002)
              |
       Services und Modelle
              |
       Repository-Abstraktion
              |
SQLite data/replan.sqlite + einmalige JSON-Migration
```

Die Datenbankdatei wird absichtlich nicht in Git versioniert. Gemeinsam versioniert werden Quellcode, Bilder und Seed-Definitionen; jedes Teammitglied synchronisiert seine lokale Demo-Datenbank mit `python scripts/seed_demo_data.py`.

## Zentrale Use Cases

| Use Case | Ergebnis |
| --- | --- |
| Raum buchen | Ganzer Raum wird für den gewählten Zeitraum reserviert und für Überschneidungen gesperrt. |
| Shared Office buchen | Konkreter oder automatisch ausgewählter freier Sitzplatz wird reserviert. |
| Asset buchen | Ausstattung wird unabhängig von Räumen reserviert. |
| Buchung verwalten | Eigene Buchung wird angezeigt, bearbeitet, verlängert, kopiert, exportiert oder storniert. |
| Einladung nutzen | Manuell eingeladene Person tritt mit Code/Link, Passwort und optionaler E-Mail-Freigabe bei. |
| Anwesenheit erfassen | Check-in/-out unterscheidet Reservierung und tatsächliche Belegung. |
| Konto verwalten | Profildaten und Passwort werden geändert oder das eigene Konto wird gelöscht. |
| Administration | Admin verwaltet Stammdaten, Rollen, Buchungen und prüft Belegung, Statistik und Protokoll. |

## Qualität

Der Branch `G03_Backend` wurde am 29.07.2026 mit **97 Backend-Tests**, **13 Frontend-Tests** und einem erfolgreichen Produktions-Build geprüft. Details stehen in der [Testdokumentation](./4_Testdokumentation.md).

## Bewusste Grenzen

- kein produktiver E-Mail-Versand oder SMTP-Dienst
- keine browserbasierten End-to-End-Tests
- keine produktive Deployment-Konfiguration
- keine Refresh-Tokens oder serverseitige Sperrliste für vorzeitig widerrufene Tokens
- SQLite speichert die Repository-Datensätze generisch; ein vollständig normalisiertes relationales Schema bleibt eine mögliche Weiterentwicklung

## Verweise

- [Konzeptionsplan](./2_Konzeptionsplan.md)
- [UML und Architektur](./3_UML.md)
- [Testdokumentation](./4_Testdokumentation.md)
- [Sprint-III-Reflexion](./Sprints/Sprint_III_Engineering_Reflexion.md)
- [Sprint-III-Umsetzungsplan](./Sprints/Sprint_III_Umsetzungsplan.md)
- [KI-Nutzung](./9_KI_Nutzung.md)
- [Qualitätsbericht](./Sprints/Qualitaetsbericht.html)
