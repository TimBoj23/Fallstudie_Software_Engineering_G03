# KI-Nutzung im Projekt RePlan

**Stand:** 28.07.2026

Dieses Dokument ordnet die eingesetzte KI-Unterstützung transparent ein. Fachliche Entscheidungen, Priorisierung, Abnahme und Verantwortung lagen jederzeit beim Projektteam.

## Eigenständige Arbeit des Teams

| Bereich | Leistung des Teams |
| --- | --- |
| Fachliche Anforderungen | Definition der RePlan-Idee und der Abläufe für Räume, Shared Offices, Assets, Einladungen und Administration |
| Projektsteuerung | Rollen, Sprintziele, GitHub-Issues, Kanban-Status und Abnahmereihenfolge |
| UX-Bewertung | Entscheidung über Navigation, verständliche Bezeichnungen, Farben, Bilder und notwendige Rückmeldungen |
| Demo-Daten | Auswahl der Räume, Geräte, Arbeitsplätze, Admin-Konten und Bildmotive |
| Qualitätssicherung | Manuelle Abnahme, Reproduktion gemeldeter Fehler und Entscheidung über notwendige Korrekturen |
| Präsentation | Festlegung von Schwerpunkt, Demo-Ablauf, Verantwortlichkeiten und Endauswahl der Artefakte |

## Art der KI-Unterstützung

| Bereich | Unterstützung |
| --- | --- |
| Analyse und Refactoring | Untersuchung von Backend, Frontend, Datenhaltung und Dokumentstruktur sowie Vorschläge für kleine, überprüfbare Änderungen |
| Backend | Unterstützung bei Repository-, Buchungs-, Einladungs-, Check-in/-out-, Profil- und Admin-Logik |
| Frontend | Unterstützung bei API-Anbindung, Dark Mode, Navigation, Buchungsansichten, Sitzplan und responsivem Layout |
| Fehlersuche | Analyse von Zeitformaten, Zeitzonen, Check-in-Grenzen, Ressourcenfreigabe, SQLite-Daten und gleichzeitig laufenden Serverprozessen |
| Demo-Daten | Bereinigung lokaler Nutzer und Aktivitäten sowie idempotente Synchronisierung gemeinsamer Bilder und Ressourcen |
| Tests | Ergänzung und Ausführung automatisierter Backend- und Frontend-Tests sowie Produktions-Builds |
| Dokumentation | Abgleich und Aktualisierung von Konzept, UML, Sprint-, Test-, Abschluss- und Qualitätsdokumenten |

## Arbeitsweise und Kontrolle

- Änderungen wurden auf Anforderungen oder Rückmeldungen des Teams zurückgeführt.
- Vor Commits wurden relevante Tests und Builds ausgeführt.
- Sicherheits- und Umfangsentscheidungen wurden ausdrücklich dokumentiert, insbesondere der Verzicht auf echten E-Mail-Versand.
- Zugangsdaten und lokale Datenbanken wurden nicht als Dokumentationsinhalt oder Git-Artefakt behandelt.
- Vom Team gemeldete UI- und Zeitfehler wurden reproduziert und anhand des Codes überprüft.

## Verantwortlichkeit

KI war ein Entwicklungs- und Dokumentationswerkzeug, kein autonomes Teammitglied. Das Projektteam bleibt verantwortlich für fachliche Richtigkeit, Code-Review, Abnahme, Präsentation und den final veröffentlichten Stand.
