# Testdokumentation RePlan

**Geprüfter Branch:** `G03_Backend`
**Prüfstand:** 28.07.2026

## Automatisierte Prüfungen

Backend-Tests aus dem Projektstamm:

```bash
.venv/bin/python -m pytest -q
```

Frontend-Tests und Produktions-Build:

```bash
cd frontend
npm test -- --run
npm run build
```

| Bereich | Abgedeckte Beispiele |
| --- | --- |
| Nutzer und Authentifizierung | Registrierung, Login, Rollen, Bearer-Token, Profiländerung, Passwortwechsel, Passwort-Reset, Kontolöschung und E-Mail-Wiederverwendung |
| Räume und Assets | Anlegen, Bearbeiten, Deaktivieren, Suche, Filter und Bildpfade |
| Buchungen | Anlage, Konfliktprüfung, Bearbeitung, Kopie, Verlängerung, Stornierung und Rechteprüfung |
| Shared Offices | konkrete und automatische Sitzplatzwahl, parallele Sitzplatzkonflikte und Sitzplanlogik |
| Einladungen | Einladungscode, Passwort, E-Mail-Freigabeliste und Kapazitätsgrenzen – bewusst ohne echten E-Mail-Versand |
| Serien | wöchentliche Wiederholung sowie Änderung/Stornierung einzelner und folgender Termine |
| Anwesenheit | Check-in, Check-out, verfrühter Check-in, automatischer Check-out und Admin-Belegung |
| Zeitverarbeitung | UTC-Normalisierung, lokale Anzeige, Zeitbereichsvalidierung und iCalendar-Export |
| Administration | Nutzer- und Ressourcenverwaltung, Statistik, Audit-Protokoll und abgesicherter Demo-Reset |
| Frontend-Logik | Theme, Kalenderfarben, Datumsformat, Buchungs-UI sowie Raum-/Shared-Office-Trennung |

## Manuelle Abnahmeszenarien

| Ablauf | Erwartung |
| --- | --- |
| Erstinstallation | Backend und Frontend starten nach Anleitung; `/api/health` antwortet erfolgreich. |
| Seed-Synchronisierung | `scripts/seed_demo_data.py` ergänzt idempotent Räume, Sitzplätze, neun Assets, Bilder und vier Demo-Admins. |
| Raum buchen | Eine Ganzraumbuchung blockiert den Raum für überschneidende Buchungen. |
| Shared Office buchen | Nutzende wählen einen freien Arbeitsplatz grafisch oder lassen einen freien Platz automatisch zuweisen. |
| Asset buchen | Ausstattung kann im selben Zeitraum nicht doppelt gebucht werden. |
| Eigene Buchung bearbeiten | Nur zulässige zukünftige Änderungen werden gespeichert; die Konfliktprüfung läuft erneut. |
| Favoritenübersicht | Kontobezogene Favoriten werden zu Räumen, Arbeitsplätzen und Ausstattung aufgelöst. |
| Visuelle Verfügbarkeit | Freie und belegte Zeiträume werden mit Ressource, Zeitraum und Konflikten dargestellt. |
| Reale Nutzung | Geplante Meetingzeit wird anhand von Check-in und Check-out der tatsächlichen Nutzung gegenübergestellt. |
| Check-in/-out | Check-in ist ab lokalem Buchungsbeginn möglich; ein beendeter Termin wird automatisch ausgecheckt. |
| Einladung annehmen | Eine Person tritt über manuell geteilten Code/Link, Passwort und gegebenenfalls freigegebene E-Mail bei. |
| Kontoeinstellungen | Name, E-Mail, Bild und Passwort können geändert werden; nach Löschung ist die E-Mail wieder registrierbar. |
| Admin-Bereich | Admin sieht Nutzerbilder, Ressourcen, Buchungen, Belegung, Statistik und Audit-Ereignisse. |
| Demo-Reset | Adminrolle, Passwort und Bestätigungstext sind erforderlich; Demo-Ressourcen und Admins bleiben erhalten. |
| Dark Mode | Auswahl bleibt nach einem Neuladen erhalten. |
| Kalenderexport | `.ics`-Datei lässt sich in einer Kalenderanwendung öffnen. |

## Ergebnis

Am 28.07.2026 wurden auf `G03_Backend` folgende Prüfungen erfolgreich ausgeführt:

- **97 Backend-Tests bestanden**
- **13 Frontend-Tests bestanden**
- **React-Produktions-Build erfolgreich**

Damit sind **110 automatisierte Tests** im dokumentierten Branch grün. Browserbasierte End-to-End-Tests und ein vollständiger Fremdgerätetest bleiben sinnvolle letzte Abnahmeschritte.
