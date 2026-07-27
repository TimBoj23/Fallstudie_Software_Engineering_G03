# Fallstudie Software Engineering – Gruppe 03

In diesem Repository wird die Fallstudie für Gruppe 03 im Modul **Fallstudie Software Engineering** bearbeitet.

## Projekt

**Raum- und Ressourcenplanung für Unternehmen**

Ziel des Projekts ist die Entwicklung eines webbasierten Tools, das Unternehmen dabei unterstützt, Räume, Arbeitsplätze und Ressourcen effizient zu planen, zu buchen und zu verwalten.

Das System soll Mitarbeitenden ermöglichen, verfügbare Räume, Arbeitsplätze und Ressourcen schnell zu finden und für bestimmte Zeiträume zu buchen. Gleichzeitig soll ein Admin-Bereich bereitgestellt werden, in dem Räume, Ressourcen und Buchungen zentral verwaltet werden können.

Die ausführliche fachliche Planung, das Lastenheft, die Stakeholderanalyse, Use Cases, Anforderungen, Priorisierung, Risiken, Sprintplanung und **Rollenverteilung** befinden sich im Dokument:

- [`Konzeptionsplan.md`](./docs/Konzeptionsplan.md)

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
- optionaler Dark Mode mit gespeicherter Auswahl
- Check-in und Check-out für tatsächliche Raumbelegung
- Kalenderexport einzelner Buchungen als `.ics`
- Favoriten für häufig genutzte Räume, Arbeitsplätze und Ausstattung
- wiederkehrende wöchentliche Buchungen und freie Alternativtermine
- QR-Code-Check-in für eigene Buchungen
- Admin-Auslastungsstatistik und Änderungsprotokoll
- Kontoeinstellungen für Profilbild, Name, E-Mail, Passwort und sichere Kontolöschung

## Beispiele für Räume und Ressourcen

### Räume

- Meetingräume
- Konferenzräume
- Arbeitsplätze
- Sitzplätze in Shared Offices
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
- Die Arbeitsteilung und Meilensteine halten wir in `docs/Projekt_Zeitplan.md` fest.
- Anforderungen, Dokumentation, Setup-Hinweise und Tests werden im Repository gepflegt.
- Fertige oder geplante Aufgaben werden zusätzlich als GitHub Issues dokumentiert.
- Die Dokumentation wird kontinuierlich gepflegt und nicht erst am Projektende ergänzt.

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
├── docs/
│   ├── Sprint_I_Architekturentscheidungen.md
│   ├── Sprint_II_Planung.md
│   ├── Sprint_III_Umsetzungsplan.md
│   └── Konzeptionsplan.md
├── requirements.txt
├── app.py
├── src/
│   ├── models/
│   ├── services/
│   └── routes/
├── frontend/
│   └── src/
├── scripts/
│   ├── demo.py
│   ├── reset_demo_activity.py
│   └── seed_demo_data.py
└── tests/
```

Die konkrete Struktur kann im Verlauf der Umsetzung angepasst werden.

## Aktive Admin-Konten

- `alex@replan.de`
- `florian@replan.de`
- `tim@replan.de`
- `denis@replan.de`

Der bereinigte Demo-Datenbestand enthält ausschließlich diese vier aktiven Admin-Konten. Bei einer selbst ausgeführten Kontolöschung wird die bisherige E-Mail-Adresse wieder für eine Registrierung freigegeben.

## Ausführung des Programms

## Setup-Guide: Backend und React-Frontend

Das Projekt besteht aus einem Flask-Backend und einem React-Frontend. Beide Teile müssen parallel laufen.

### 1. Backend einrichten

Im Hauptordner des Projekts:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Falls `pip` nicht zur richtigen Python-Version gehört:

```bash
python -m pip install -r requirements.txt
```

### 2. Backend starten

Im Hauptordner:

```bash
python app.py
```

Das Backend läuft anschließend unter:

```text
http://localhost:5002
```

API-Test:

```text
http://localhost:5002/api/health
```

### 3. Frontend einrichten

In einem zweiten Terminal:

```bash
cd frontend
npm ci
```

### 4. Frontend starten

Im Ordner `frontend`:

```bash
npm run dev
```

Das Frontend läuft anschließend unter:

```text
http://localhost:5173
```

### Spätere Starts (nach abgeschlossener Installation)

Terminal 1:

```bash
source .venv/bin/activate
python app.py
```

Terminal 2:

```bash
cd frontend
npm run dev
```

Danach im Browser öffnen:

```text
http://localhost:5173
```

Für den QR-Check-in mit einem Smartphone müssen Rechner und Smartphone im selben lokalen Netz sein. Das Frontend wird dann erreichbar gestartet:

```bash
cd frontend
npm run dev -- --host 0.0.0.0
```

Anschließend die im Terminal angezeigte Netzwerkadresse im Browser öffnen. Der erzeugte QR-Code übernimmt automatisch diese Adresse. Optional kann sie vor dem Backend-Start ausdrücklich gesetzt werden, zum Beispiel mit `FRONTEND_URL=http://192.168.1.20:5173`.

## Testen

Die zu testenden Dateien werden im Ordner `tests/` abgelegt.

Backend-Tests aus dem Hauptordner ausführen:

```bash
.venv/bin/python -m pytest
```

Wichtige Testfälle:

- Raum kann erfolgreich gebucht werden.
- Ressource kann erfolgreich gebucht werden.
- Doppelbuchung wird verhindert.
- Nutzer kann eigene Buchungen einsehen.
- Nutzer kann eigene Buchung stornieren.
- Administrator kann Räume verwalten.
- Administrator kann Ressourcen verwalten.

Frontend-Build prüfen:

```bash
cd frontend
npm run build
```

Frontend-Tests ausführen:

```bash
cd frontend
npm test
```

## Lokale Demo-Administratoren

Das idempotente Seed-Skript legt die Demo-Ressourcen und Admin-Konten an:

```bash
python scripts/seed_demo_data.py
```

Die ausgegebenen Passwörter sind ausschließlich für die lokale Demo vorgesehen und müssen außerhalb der Demo ersetzt werden. Alle Admin-Konten sind unter **Admin → Nutzer** sichtbar; dort kann nach Rolle `Admin` gefiltert werden.

## Konfiguration

Für lokale Demo-Zwecke kann das Backend ohne zusätzliche Umgebungsvariablen gestartet werden. Für jede Umgebung außerhalb der lokalen Demo muss ein eigener Flask Secret Key gesetzt werden:

```bash
export SECRET_KEY="bitte-einen-langen-zufaelligen-wert-setzen"
```

Optionale Speicher-Konfiguration:

```bash
export REPLAN_STORAGE=sqlite
export REPLAN_DB_PATH=data/replan.sqlite
```

Standardmäßig nutzt das Projekt SQLite über `data/replan.sqlite`. Die Repository-Schicht migriert vorhandene JSON-Daten beim ersten Zugriff in SQLite.

## Verwendete Frameworks und Bibliotheken

| Bereich | Technologie | Hinweis |
| --- | --- | --- |
| Backend | Python, Flask, Flask-CORS, ItsDangerous | Web-API, CORS und signierte Auth-Tokens |
| Persistenz | SQLite, JSON | SQLite-backed Repository mit JSON-Migration |
| Tests | pytest | Backend-Unit- und Service-Tests |
| Frontend | React, Vite | Weboberfläche |
| UI | lucide-react | Icons im Frontend |

Die genauen Versionen stehen in `requirements.txt` und `frontend/package.json`.

Hinweis zur Prüfung auf einem weiteren Rechner: Backend-Setup, Frontend-Setup, `pytest` und `npm run build` sind dokumentiert. Der finale Test auf einem fremden Gerät sollte vor der Abgabe mit dieser Anleitung durchgeführt und im Team bestätigt werden.

## KI-Nutzung

Die Nutzung von KI-Unterstützung ist transparent dokumentiert:

- [`docs/KI_Nutzung.md`](./docs/KI_Nutzung.md)

## Abschluss- und Qualitätsdokumente

- [`docs/Testdokumentation.md`](./docs/Testdokumentation.md)
- [`docs/Sprint_III_Engineering_Reflexion.md`](./docs/Sprint_III_Engineering_Reflexion.md)
- [`docs/Kanban_Aktualisierungen.md`](./docs/Kanban_Aktualisierungen.md)
- [`docs/Abschlussdokumentation.md`](./docs/Abschlussdokumentation.md)
- [`docs/Qualitaetsbericht.html`](./docs/Qualitaetsbericht.html)

## Wichtige Projektdokumente

- `README.md`: Repository-Übersicht, Arbeitsweise, Setup, Start und Tests
- `docs/Konzeptionsplan.md`: fachliche Planung, Lastenheft, Anforderungen, Stakeholderanalyse, Use Cases, MVP, Risiken, Sprints und Abschlussdokumentation
- `docs/Projekt_Zeitplan.md`: Meilensteine und grober Projektzeitplan
- `docs/Sprint_I_Architekturentscheidungen.md`, `docs/Sprint_II_Planung.md` und `docs/Sprint_III_Umsetzungsplan.md`: einheitliche Sprint-Serie
- `requirements.txt`: technische Abhängigkeiten
- `tests/`: automatisierte Tests
