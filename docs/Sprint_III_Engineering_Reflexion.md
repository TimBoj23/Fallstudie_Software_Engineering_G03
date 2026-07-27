# Sprint III – Engineering-Reflexion und Lessons Learned

## Planung vs. Umsetzung

| Geplant | Umgesetzt | Einordnung |
| --- | --- | --- |
| Räume und Ressourcen buchbar machen | Räume, Sitzplätze und Assets sind getrennt buchbar | Umfang wurde erweitert, weil Sitzplätze fachlich wichtig wurden. |
| Einfache Datenhaltung | SQLite-backed Repository mit JSON-Migration | Für die Demo belastbarer als reine JSON-Dateien, aber noch kein vollständig relationales Schema. |
| Nutzer können buchen | Nutzer haben Registrierung, Login, Logout, eigene Buchungen und Passwort-Reset | Authentifizierung bleibt MVP-nah, ist aber für die Präsentation nutzbar. |
| Admin verwaltet Ressourcen | Admin kann Räume, Sitzplätze, Assets, Nutzer und Buchungen einsehen/bearbeiten | Admin-Oberfläche wurde deutlich wichtiger als am Anfang geplant. |
| Grundlegende Tests | Backend-Tests für Services und Randfälle sowie kleine Frontend-Logiktests | Browserbasierte End-to-End-Tests bleiben ein offener Ausbauschritt. |

## Architekturentscheidungen

- Das Backend bleibt die zentrale Quelle für Buchungslogik und Konfliktprüfung.
- Die API trennt Nutzerfunktionen und Adminfunktionen über Rollen.
- Sitzplätze wurden als eigene Entität modelliert, damit Arbeitsplätze separat buchbar sind.
- `room_type` trennt intern Shared-Office-Räume (`shared_desk`) von Seminarräumen und Studios; die Oberfläche verwendet den verständlicheren Begriff „Shared Office“.
- SQLite wird als Persistenzschicht genutzt, die Repository-Abstraktion erlaubt später ein relationales Schema mit eigenen Tabellen.

## Abweichungen und Gründe

- Das Frontend wurde zwischenzeitlich stärker eigenständig entwickelt als geplant. Dadurch musste später gezielt an die REST API angebunden werden.
- Die Datenhaltung wurde zunächst einfach gehalten. Für die Demo wurde SQLite ergänzt, ohne die gesamte Repository-Schicht neu zu schreiben.
- Einladungen werden bewusst ohne SMTP als kurzer Code und manuell teilbarer Link umgesetzt.
- Das Projektposter und Qualitätssheet wurden spät ergänzt, weil die Präsentationsanforderungen zum Ende konkreter wurden.

## Lessons Learned

- Schnittstellen zwischen Frontend und Backend müssen früh verbindlich beschrieben werden.
- Demo-Daten sind kein Nebenthema: realistische Daten machen fachliche Abläufe verständlicher.
- Eine Reservierung ist nicht automatisch eine Anwesenheit; Check-in und Belegung müssen fachlich getrennt werden.
- Farbschemata lassen sich wartbarer über zentrale Design-Tokens statt über komponentenweise Sonderregeln umsetzen.
- Technische IDs gehören nicht in Nutzeransichten.
- Teilbelegung braucht eine sichtbare Legende und konkrete freie Platzzahlen; Farbe allein reicht nicht.
- Änderungen an Buchungen müssen dieselbe Konfliktlogik wie Neuanlagen verwenden.
- Admin-Funktionen brauchen mehr Kontext als reine Listen, zum Beispiel Nutzerbilder, Rollen und Buchungsbesitzer.
- Kleine, testbare Backend-Services erleichtern spätere Änderungen erheblich.
- KI-Unterstützung kann Umsetzung und Dokumentation beschleunigen, ersetzt aber keine fachliche Bewertung durch das Team.
