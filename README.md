# Fallstudie Software Engineering – Gruppe 03

In diesem Repository wird die Fallstudie für Gruppe 03 im Modul **Fallstudie Software Engineering** bearbeitet.

## Projekt

**Raum- und Ressourcenplanung für Unternehmen**

Ziel des Projekts ist die Entwicklung eines webbasierten Tools, das Unternehmen dabei unterstützt, Räume, Arbeitsplätze und Ressourcen effizient zu planen, zu buchen und zu verwalten.

Das System soll Mitarbeitenden ermöglichen, verfügbare Räume, Arbeitsplätze und Ressourcen schnell zu finden und für bestimmte Zeiträume zu buchen. Gleichzeitig soll ein Admin-Bereich bereitgestellt werden, in dem Räume, Ressourcen und Buchungen zentral verwaltet werden können.

Die ausführliche fachliche Planung, das Lastenheft, die Stakeholderanalyse, Use Cases, Anforderungen, Priorisierung, Risiken und Sprintplanung befinden sich im Dokument:

- [`Konzeptionsplan.md`](./Konzeptionsplan.md)

## Teilnehmer

- Tim-Oliver Strauß
- Florian Haentjes
- Denis Nickel
- Alexander Vetrenko

## Themenauswahl

- [ ] Lernplaner für Studierende
- [ ] Essensplaner für verschiedene Zielgruppen
- [x] Raum- und Ressourcenplanung für Unternehmen
- [ ] Aktivitäten und Habit-Tracker für Fitness- und Gesundheitsbewusste
- [ ] Gerätemanagement-Plattform für Unternehmen

## Kurzbeschreibung

In vielen Unternehmen werden Räume, Arbeitsplätze und Ressourcen über verschiedene Kanäle wie E-Mail, Kalender, Tabellen oder persönliche Absprachen verwaltet. Dadurch können Doppelbuchungen, unklare Zuständigkeiten oder unnötiger organisatorischer Aufwand entstehen.

Das geplante System soll diesen Prozess vereinfachen und eine zentrale Plattform bereitstellen, über die Buchungen transparent, nachvollziehbar und effizient durchgeführt werden können.

## Ziel des Systems

Das System soll folgende Ziele erfüllen:

- zentrale Verwaltung von Räumen, Arbeitsplätzen und Ressourcen
- einfache Buchung durch Mitarbeitende
- Vermeidung von Doppelbuchungen
- Übersicht über eigene Buchungen
- administrative Verwaltung von Räumen, Ressourcen und Buchungen
- nachvollziehbare und benutzerfreundliche Planung
- einfache Bedienbarkeit über eine Weboberfläche

## Beispiele für Räume und Ressourcen

### Räume

- Meetingräume
- Konferenzräume
- Arbeitsplätze
- Sitzplätze in Großraumbüros
- Projekträume
- Schulungsräume

Beispiel: `Raum 1001, Platz 23 [1001-23]`

### Ressourcen

- Beamer
- Whiteboards
- Laptops
- Monitore
- Adapter
- Moderationsmaterial
- Präsentationstechnik

## Repository und Arbeitsweise

- Wir nutzen hauptsächlich zur Bearbeitung den Branch `G03`.
- Es wird ein Pull Request erstellt, wenn eine Aufgabe fertig ist.
- Die Arbeitsteilung halten wir in `TASKS.md` fest.
- Anforderungen, Dokumentation, Setup-Hinweise und Tests werden im Repository gepflegt.
- Fertige oder geplante Aufgaben werden zusätzlich als GitHub Issues dokumentiert.
- Die Dokumentation wird kontinuierlich gepflegt und nicht erst am Projektende ergänzt.

## Rollenverteilung

| Rolle | Verantwortliche Person | Aufgaben |
|---|---|---|
| Projektmanager | Florian Haentjes | Koordination, Zeitplanung |
| Scrum Master | Tim-Oliver Strauß | Sprint Planning, Review & Retrospective |
| Requirements Engineer | Alexander Vetrenko | Anforderungen, User Stories, Stakeholderanalyse, Scoping Document |
| Backend-Entwicklung | gesamtes Team | Datenmodell, Geschäftslogik, Buchungslogik, Schnittstellen |
| Frontend-Entwicklung / UX | Denis Nickel | Benutzeroberfläche, Nutzerführung, Darstellung der Buchungen |
| Quality Assurance | Denis Nickel | Tests, Code Reviews, Fehlerprüfung, Dokumentation der Qualität |

> Hinweis: Die Rollen dienen als Hauptverantwortlichkeiten. Die Umsetzung erfolgt gemeinsam im Team.

## Geplante technische Umsetzung

Die genaue technische Umsetzung kann im Projektverlauf angepasst werden. Geplant ist eine webbasierte Anwendung mit:

- Python als Programmiersprache
- Weboberfläche im Browser
- Speicherung der Daten in einer einfachen Datenbank oder Datei
- Tests mit `pytest`
- Dokumentation im GitHub-Repository

## Projektstruktur

Eine mögliche Projektstruktur ist:

```text
.
├── README.md
├── Konzeptionsplan.md
├── TASKS.md
├── requirements.txt
├── app.py
├── src/
│   ├── models/
│   ├── services/
│   └── routes/
└── tests/
```

Die konkrete Struktur kann im Verlauf der Umsetzung angepasst werden.

## Ausführung des Programms

### Installation

Repository klonen oder herunterladen.

Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

### Start des Programms

Start des Programms durch:

```bash
python3 <STARTDATEI>.py
```

Beispiel, falls die Startdatei später `app.py` heißt:

```bash
python3 app.py
```

Das Programm startet anschließend im Browser unter:

```text
http://[IP_ADDRESS]
```

oder lokal unter:

```text
http://localhost:5000
```

> Hinweis: Die konkrete Startdatei wird nach der technischen Umsetzung angepasst.

## Testen

Die zu testenden Dateien werden im Ordner `tests/` abgelegt.

Tests ausführen:

```bash
pytest
```

Wichtige Testfälle:

- Raum kann erfolgreich gebucht werden.
- Ressource kann erfolgreich gebucht werden.
- Doppelbuchung wird verhindert.
- Nutzer kann eigene Buchungen einsehen.
- Nutzer kann eigene Buchung stornieren.
- Administrator kann Räume verwalten.
- Administrator kann Ressourcen verwalten.

## Wichtige Projektdokumente

- `README.md`: Repository-Übersicht, Arbeitsweise, Setup, Start und Tests
- `Konzeptionsplan.md`: fachliche Planung, Lastenheft, Anforderungen, Stakeholderanalyse, Use Cases, MVP, Risiken, Sprints und Abschlussdokumentation
- `TASKS.md`: konkrete Aufgabenverteilung im Team
- `requirements.txt`: technische Abhängigkeiten
- `tests/`: automatisierte Tests

