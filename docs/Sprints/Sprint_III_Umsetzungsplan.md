# Sprint III – Umsetzungsplan RePlan

**Branch:** `G03_Backend`
**Stand:** 28.07.2026
**Status:** fachlich umgesetzt; Abschlussprüfung und Zusammenführung laufen

## Ziel

RePlan wurde vom lokalen MVP zu einer stabilen Fullstack-Demo mit gemeinsamer REST-API, SQLite-Persistenz, verständlichen Buchungsabläufen, Admin-Funktionen und reproduzierbaren Demo-Daten ausgebaut. Trotz des Branch-Namens umfasst Sprint III Backend, Frontend, Tests und Dokumentation.

## Umgesetzte Arbeitspakete

### Persistenz und Demo-Daten

- [x] SQLite als primäre lokale Persistenz hinter der Repository-Schnittstelle eingeführt
- [x] einmalige Migration vorhandener JSON-Daten ermöglicht
- [x] Datenbankdatei aus Git ausgeschlossen
- [x] idempotentes Seed-Skript für Räume, Shared-Office-Plätze, neun Assets, Bilder und vier Demo-Admins erstellt
- [x] geschützten Demo-Reset für Buchungen, Statistik, Protokoll und Nicht-Admin-Konten ergänzt

### Buchbare Objekte und Verfügbarkeit

- [x] Räume, Shared Offices und Ausstattung in Navigation und Buchung getrennt
- [x] Ganzraumbuchungen für Überschneidungen vollständig gesperrt
- [x] konkrete und automatisch zugewiesene Shared-Office-Plätze umgesetzt
- [x] grafischen Sitzplan und Zeitraster ergänzt
- [x] Suche, Filter, kontobezogene Favoritenübersicht und sprechende Objektnamen ergänzt
- [x] Verfügbarkeit durch visuelle Frei-/Belegt-Anzeige, Zeitraum und Konfliktdetails erklärt

### Buchungsverwaltung

- [x] eigene Buchungen filtern, kopieren, bearbeiten, verlängern und stornieren
- [x] wöchentliche Serienbuchungen sowie Einzel-/Folgeterminänderungen
- [x] iCalendar-Export und QR-Code-Check-in
- [x] Check-in ab Buchungsbeginn, manueller Check-out und automatischer Check-out nach Ende
- [x] gemeinsame Konfliktprüfung für Anlage, Änderung, Verlängerung und Serien

### Einladungen und Benachrichtigungen

- [x] passwortgeschützte Einladungen mit kurzem Code und manuell teilbarem Link
- [x] optionale Liste erlaubter E-Mail-Adressen und Kapazitätsprüfung
- [x] eigener Ablauf „Einladung annehmen“
- [x] In-App-Benachrichtigungen mit Löschfunktion
- [x] Umfang klar abgegrenzt: **kein echter E-Mail-Versand**

### Nutzer und Administration

- [x] Registrierung, Login, Logout und signierte Bearer-Tokens
- [x] lokaler Passwort-Reset-Token
- [x] Profilbild, Name, E-Mail und Passwort in den Kontoeinstellungen änderbar
- [x] eigene Kontolöschung mit Passwortbestätigung und anschließender E-Mail-Wiederverwendung
- [x] Nutzer-, Rollen-, Raum-, Sitzplatz-, Asset- und Buchungsverwaltung
- [x] aktuelle Belegung, tatsächliche Nutzung, No-Shows, Auslastungsstatistik und Audit-Protokoll
- [x] vier benannte Demo-Admin-Konten mit Profilbildern synchronisiert

### UX, Qualität und Dokumentation

- [x] Dark Mode mit gespeicherter Auswahl
- [x] leere Zustände, verständliche Fehlermeldungen und responsive Buchungskarten verbessert
- [x] reale bzw. passende versionierte Bilder für Demo-Ressourcen eingebunden
- [x] Backend-, Frontend- und Build-Prüfungen dokumentiert
- [x] Konzeptionsplan, UML, Sprint-, Test-, Abschluss-, KI- und Qualitätsdokumente abgeglichen

## Technische Entscheidungen

- Geschäftslogik und Berechtigungen liegen im Backend; das Frontend bildet sie nicht separat nach.
- Zeitintervalle verwenden die Halbintervallregel `[Start, Ende)`, damit direkt aufeinanderfolgende Buchungen zulässig sind.
- Browserzeiten werden eindeutig übertragen und backendseitig normalisiert; die lokale Anzeige nutzt standardmäßig `Europe/Berlin`.
- SQLite passt zur lokalen Demonstration ohne zusätzlichen Datenbankserver. Die Repository-Abstraktion ermöglicht eine spätere Ablösung.
- Lokale Nutzerdaten und Buchungen werden nicht eingecheckt. Reproduzierbarkeit entsteht durch versionierte Bilder und das Seed-Skript.

## Nachweis auf diesem Branch

- 97 Backend-Tests bestanden
- 13 Frontend-Tests bestanden
- React-Produktions-Build erfolgreich

## Noch vor Abgabe

- [ ] aktuellen Branch mit den freigegebenen letzten Fixes kontrolliert zusammenführen
- [ ] vollständigen Setup- und Demo-Test auf einem zweiten Rechner durchführen
- [ ] Präsentation und Poster final abstimmen
- [ ] GitHub-Issues und Kanban-Status direkt im GitHub-Projekt abschließend prüfen

Eine separate Kanban-Markdown-Datei wird nicht mehr geführt; der verbindliche Aufgabenstatus liegt direkt in GitHub Issues und im Kanban-Board.
