# Sprint III – Engineering-Reflexion und Lessons Learned

**Stand:** 28.07.2026

## Planung vs. Umsetzung

| Geplant | Tatsächlich umgesetzt | Einordnung |
| --- | --- | --- |
| Räume und Ressourcen buchen | Räume, Sitzplätze und Assets mit eigener Navigation, Suche, Filtern und Verfügbarkeit | Sitzplätze wurden als fachlich notwendige eigene Entität ergänzt. |
| Einfache SQL-Persistenz | SQLite-backed Repository mit einmaliger JSON-Migration | Belastbarer für die lokale Demo, aber noch kein normalisiertes relationales Schema. |
| Grundlegende Nutzerkonten | Registrierung, Login, Logout, Passwort-Reset, Profileinstellungen und Kontolöschung | Der Account-Lebenszyklus wurde deutlich vollständiger als ursprünglich geplant. |
| Admin verwaltet Ressourcen | Nutzer, Rollen, Räume, Sitzplätze, Assets, Buchungen, Belegung, Statistik, Audit und Reset | Die Admin-Oberfläche wurde zu einem eigenen Kernbereich. |
| Erweiterte Tests | 94 Backend- und 10 Frontend-Tests auf `G03_Backend` plus erfolgreicher Build | Browserbasierte E2E-Tests bleiben offen. |

## Wichtige Architekturentscheidungen

- Das Backend bleibt die einzige Quelle für Buchungs-, Konflikt- und Berechtigungsregeln.
- React stellt Zustände dar, sendet lokale Eingaben als eindeutige Zeitstempel und zeigt fachliche Fehlermeldungen an.
- `room_type=shared_desk` bleibt die interne Kompatibilitätsbezeichnung; die Oberfläche verwendet „Shared Office“.
- Sitzplätze sind eigene buchbare Objekte und verweisen auf ihren Shared-Office-Raum.
- Einladungen bestehen aus Code/Link, Passwort und optionaler E-Mail-Freigabeliste; echter Mailversand wurde ausdrücklich nicht umgesetzt.
- Reservierung und Anwesenheit bleiben getrennt: Check-in/-out und automatischer Check-out liefern die tatsächliche Belegung.
- Bilder und Seed-Definitionen werden über Git geteilt, die lokale SQLite-Datei dagegen nicht.

## Abweichungen und Gründe

- Das Frontend entstand zeitweise stärker unabhängig vom Backend. Die REST-API musste anschließend konsequent als gemeinsame Schnittstelle etabliert werden.
- Der Funktionsumfang wuchs um Dark Mode, Favoriten, Serien, Einladungen, iCalendar, QR-Check-in, Statistik und Kontoeinstellungen, weil diese Abläufe die Demo wesentlich verständlicher machen.
- Die Datenhaltung wurde ohne kompletten Austausch der Services von JSON auf SQLite umgestellt. Das sparte Risiko, lässt aber eine spätere relationale Normalisierung offen.
- Zeitfehler traten auf, weil Browserzeit, UTC und lokale Backendzeit unterschiedlich interpretiert wurden. Eindeutige ISO-8601-Werte und gemeinsame Zeit-Hilfsfunktionen wurden deshalb zum Architekturthema.
- Lokale Datenbanken führten zu unterschiedlichen Demo-Beständen im Team. Das idempotente Seed-Skript wurde zur verbindlichen Synchronisationsquelle.

## Lessons Learned

- Frontend und Backend brauchen früh einen verbindlichen API- und Zeitformatvertrag.
- Ein laufender zweiter Backend-Prozess kann einen Fix verdecken; nach Änderungen müssen Prozesse kontrolliert neu gestartet werden.
- Demo-Daten, Bilder und Seed-Prozess gehören zur reproduzierbaren Produktqualität.
- Technische IDs gehören nicht in Nutzeransichten; sprechende Namen und konkrete Zustände sind entscheidend.
- Farbe allein genügt nicht: Belegung braucht Text, Legende und freie Kapazität.
- Erstellen, Bearbeiten, Verlängern und Serienänderung müssen dieselbe Konfliktlogik verwenden.
- Ein manueller oder automatischer Check-out muss in allen Verfügbarkeitsansichten konsistent sichtbar werden.
- Soft-Delete erfordert eine klare Regel für eindeutige Felder; gelöschte E-Mail-Adressen werden deshalb wieder freigegeben.
- Kleine Service-Methoden und reproduzierbare Tests erleichtern späte Fehlerkorrekturen erheblich.
- KI kann Analyse, Umsetzung und Dokumentation beschleunigen, ersetzt aber weder fachliche Entscheidungen noch Team-Review und Abnahme.

## Abschlussbewertung

Sprint III hat aus der MVP-Struktur eine vorführbare Fullstack-Anwendung gemacht. Für eine produktive Fortführung wären vor allem Browser-E2E-Tests, ein normalisiertes Datenbankschema, Deployment, Monitoring und – nur bei geänderter Anforderung – ein externer Maildienst nötig.
