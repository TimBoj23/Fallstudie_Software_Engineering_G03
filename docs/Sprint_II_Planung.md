# Sprint II – Planung

## Ziel des Sprint Plannings

In diesem Sprint Planning wird festgelegt, welche Aufgaben in der kommenden Woche bis zum naechsten Review bearbeitet werden. Der Fokus liegt darauf, das bestehende Backend, das React-Frontend und die Praesentationsfaehigkeit des Systems zu stabilisieren.

Das Projekt besteht aktuell aus:

- Flask-Backend mit REST-API
- JSON-Dateien als einfache Persistenz
- React/Vite-Frontend als separate Anwendung
- Backend-Logik fuer Raeume, Assets, Sitzplaetze, Buchungen, Login/Logout sowie Suche und Filter

Wichtig fuer die Praesentation: Frontend und Backend sind getrennte Anwendungen, aber fachlich verbunden. Das Frontend ruft die REST-Endpunkte des Backends auf. Die Geschaeftslogik liegt im Backend.

---

## Rollen und Redeanteile

Da drei Personen jeweils etwa 10 Minuten sprechen sollen, wird das Sprint Planning in drei klare Themenbloecke aufgeteilt.

| Person | Schwerpunkt | Redezeit |
| --- | --- | ---: |
| Person 1 | Begruessung, Projektziel, Rollen, Backlog und Anforderungen | ca. 10 Minuten |
| Person 2 | Technische Umsetzung, Backend, Schnittstellen, Sitzplatzlogik | ca. 10 Minuten |
| Person 3 | Frontend-Anbindung, Priorisierung, Risiken, nächste Schritte | ca. 10 Minuten |

Die Namen koennen vor der Praesentation eingesetzt werden:

- Person 1: ____________________
- Person 2: ____________________
- Person 3: ____________________

---

# Ablauf des Sprint Plannings

## 1. Begruessung und Zeitplanung (1 Minute)

**Sprecher: Person 1**

Kurztext:

> Willkommen zu unserem Sprint Planning fuer das Projekt RePlan. Ziel des Meetings ist es, die Aufgaben fuer die kommende Woche zu planen, Prioritaeten festzulegen und Hindernisse fruehzeitig zu identifizieren. Wir orientieren uns an einer Zeitbox von etwa 30 Minuten. Da wir zu dritt praesentieren, uebernimmt jede Person einen fachlichen Schwerpunkt.

Inhalte:

- Begruessung
- Hinweis auf Zeitbegrenzung
- Zweck des Meetings nennen
- Uebergang zum Backlog und zu den Anforderungen

---

## 2. Inhalte fuer die naechste Woche zusammentragen (10 Minuten)

**Sprecher: Person 1**

### Aktueller Projektstand

Das Projekt RePlan soll Unternehmen dabei unterstützen, Räume, Sitzplätze und Ressourcen zentral zu verwalten und zu buchen. Der bisherige Schwerpunkt lag auf der Backend-Logik und der Vermeidung von Doppelbuchungen.

Umgesetzter Stand:

- Nutzer können registriert und eingeloggt werden
- Logout-Endpunkt ist vorhanden
- Räume können gebucht werden
- Assets können gebucht werden
- Sitzplätze sind in einem Raum vorhanden
- Sitzplätze können separat gebucht werden
- Wenn kein Sitzplatz ausgewählt wird, weist das Backend automatisch einen freien Sitzplatz zu
- Doppelbuchungen werden durch die zentrale Konfliktprüfung verhindert
- Such- und Filterlogik ist im Backend vorhanden
- React-Frontend ist als separate Anwendung vorhanden und an die API angebunden

### Anforderungen im Backlog sauber formulieren

Für die nächste Woche sollen die Anforderungen als klare User Stories formuliert werden.

Beispiele:

- Als Nutzer möchte ich mich registrieren und anmelden können, damit ich Buchungen erstellen kann.
- Als Nutzer möchte ich Räume suchen und filtern können, damit ich schneller passende Räume finde.
- Als Nutzer möchte ich einen Sitzplatz in einem Raum auswählen können, damit ich gezielt einen Arbeitsplatz buchen kann.
- Als Nutzer möchte ich auch ohne Sitzplatzauswahl buchen können, damit mir automatisch ein freier Sitzplatz zugewiesen wird.
- Als Nutzer möchte ich meine Buchungen sehen und stornieren können.
- Als Administrator möchte ich Räume, Sitzplätze und Assets verwalten können.

### Infrastruktur-Aufgaben als Anforderungen erfassen

Auch technische Aufgaben werden im Backlog erfasst, damit sie nicht nebenbei verloren gehen.

Infrastruktur-Aufgaben:

- einheitliche Startanleitung für Backend und Frontend pflegen
- CORS-Konfiguration für lokale Frontend-Ports absichern
- Frontend-API-Basis einheitlich auf `http://localhost:5002/api` setzen

### Verbesserungsaufgaben aus der Retrospektive

Aus der bisherigen Zusammenarbeit ergeben sich konkrete Verbesserungen:

- Aufgaben früher im Backlog erfassen
- technische Entscheidungen dokumentieren
- keine parallelen Frontend-Prototypen ohne Absprache weiterentwickeln
- vor dem Merge prüfen, ob Frontend und Backend wirklich miteinander kommunizieren


### Task-Aufteilung nach Rollen

Der bisherige Task "Sitzplätze buchbar machen, Logout und Such-/Filterlogik implementieren" wird in Rollen aufgeteilt:

- Backend: Sitzplatzmodell, Repository, Service, Routen, Buchungskonflikte, Logout, Filterlogik. -> Alex/Tim
- Frontend: Seiten für Räume, Sitzplätze, Buchungen, Login/Logout und Buchungserstellung an API anbinden -> Florian/Denis
- QA/Dokumentation: Tests ausführen, Demo-Ablauf dokumentieren, GitHub Issues und Milestones pflegen -> Florian

### Delta zum letzten Sprint

Statt alles erneut zu erklären, wird nur der Fortschritt seit dem letzten Sprint betont:

- Vorher: Buchungen waren hauptsächlich auf Räume und Assets ausgelegt
- Jetzt: Sitzplätze sind eigene Entitäten und können separat gebucht werden
- Vorher: Frontend war nicht vorhanden
- Jetzt: React-Frontend nutzt API-Module und kommuniziert mit dem Flask-Backend
- Vorher: Logout und Suche/Filter waren offen
- Jetzt: Backend-Endpunkte und Filterlogik sind vorhanden
- Vorher: Zeitpunkt der Buchung war nicht klar auswählbar
- Jetzt: Zeitpunkt der Buchung ist klar definiert, Beginn und Ende

Übergang:

> Damit ist klar, welche Inhalte fachlich relevant sind. Im nächsten Schritt priorisieren wir, was davon für die kommende Woche am wichtigsten ist.

---

## 3. Priorisierung der kommenden Woche (10 Minuten)

**Sprecher: Person 2**

### Priorität 1: Backend soll die richtigen Daten liefern

Aufgaben:

- Backend starten und API erreichbar machen
- Frontend starten und mit Backend verbinden
- Login und Registrierung testen
- Räume, Sitzplätze und Assets anzeigen
- Buchung erstellen
- automatische Sitzplatzzuweisung zeigen
- Doppelbuchung verhindern
- Logout zeigen

Akzeptanzkriterien:

- `python3 app.py` startet das Backend ohne Fehler
- `npm run dev` startet das Frontend ohne Fehler
- `http://localhost:5002/api/health` liefert Status `ok`
- `http://localhost:5174` zeigt das Frontend
- Registrierung und Buchung funktionieren über das Frontend

### Priorität 2: Backend-Logik absichern

Aufgaben:

- Konflikte zwischen Raum- und Sitzplatzbuchungen testen
- Suche/Filter für Räume, Assets, Sitzplätze und Buchungen prüfen

Akzeptanzkriterien:

- Backend-Tests laufen mit `pytest -q`
- Doppelbuchungen werden mit HTTP `409` abgelehnt
- ungültige Eingaben liefern passende Fehlercodes

### Priorität 3: Frontend-Nutzerfluss stabilisieren

Aufgaben:

- Fehlermeldungen im Frontend verständlich anzeigen
- Buchungsformular mit Raum/Sitzplatz/Asset prüfen
- Logout prüfen
- API-Port in der Dokumentation korrekt halten

Akzeptanzkriterien:

- kein `Failed to fetch` bei korrektem Backend-Start
- Frontend nutzt `http://localhost:5002/api`
- CORS erlaubt Vite-Port `5174`

### Priorität 4: Dokumentation und GitHub Issues

Aufgaben:

- README aktualisieren
- Sprint Planning dokumentieren
- Review-Demo-Ablauf notieren
- GitHub Issues erstellen
- Milestone fuer kommenden Sprint anlegen

### Abhängigkeiten

| Aufgabe | Abhängigkeit | Auswirkung |
| --- | --- | --- |
| Frontend-Registrierung | Backend muss laufen | sonst `Failed to fetch` |
| Buchung erstellen | Login erforderlich | ohne Token keine Buchung |
| Sitzplatzbuchung | Sitzplätze müssen existieren | sonst nur klassische Raumbuchung |
| Demo | Testdaten müssen vorbereitet sein | sonst unklare Präsentation |
| GitHub Issues | Prioritäten müssen feststehen | sonst unklare Aufgabenverteilung |

### GitHub Milestone

Vorschlag für Milestone:

```text
Sprint II - Integration und Präsentationsfähigkeit
```

Fälligkeit:

```text
20.07.2026
```

---

## 4. Abschluss und Zusammenfassung (3 Minuten)

**Sprecher: Person 3**

### Nächste Schritte

1. Backend und Frontend lokal starten und Verbindung prüfen
2. Demo-Daten für Räume, Sitzplätze und Assets vorbereiten
3. Registrierung, Login, Buchung, Doppelbuchung und Logout testen
4. Milestone `Sprint II - Integration` anlegen
5. README und Sprint-Dokumentation aktuell halten


### Abschlussformulierung

> Zusammenfassend liegt der Schwerpunkt des Sprints auf Integration und Stabilisierung. Das Backend bildet weiterhin die fachliche Logik ab, während das React-Frontend als Oberfläche über REST-Endpunkte darauf zugreift. Bis zum nächsten Review konzentrieren wir uns darauf, den gesamten Ablauf von Registrierung über Buchung bis Logout stabil demonstrieren zu können.

---

# Kurzskript für die drei Sprecher

## Person 1 - Projektstand, Rollen, Backlog

Redeziel:

- erklären, was RePlan leisten soll
- aktuellen Stand zusammenfassen
- Backlog und Rollen erklären

Kernaussagen:

- RePlan ist ein Raum- und Ressourcenplanungssystem
- Backend ist für Logik und Daten verantwortlich
- Frontend ist die Benutzeroberfläche
- Sitzplätze wurden als eigene Entität ergänzt
- Aufgaben werden in Backend, Frontend und QA/Dokumentation aufgeteilt

## Person 2 - Technik, Priorisierung, Abhängigkeiten

Redeziel:

- technische Struktur erklären
- wichtigste Sprint-Aufgaben priorisieren
- Abhängigkeiten benennen

Kernaussagen:

- Flask stellt REST-Endpunkte bereit
- React ruft diese Endpunkte über API-Module auf
- Buchungslogik liegt zentral im Backend
- Priorität ist die lauffähige Integration
- Tests und Demo-Ablauf sichern die Präsentation ab

## Person 3 - Risiken, Abschluss

Redeziel:

- Risiken offen benennen
- nächste Schritte bestätigen

Kernaussagen:

- größtes Risiko sind Port-/CORS-Probleme und unklare Testdaten
- `5174` sind für Vite relevant
- Backend läuft auf `5002`
- vor der Präsentation wird der komplette Nutzerfluss getestet
- Kommunikation und GitHub Issues halten die Arbeit transparent

---

# Praesentations-Checkliste

Vor dem Sprint Review prüfen:

- [ ] Branch `G03` ist aktuell
- [ ] Backend startet mit `python3 app.py`
- [ ] API erreichbar unter `http://localhost:5002/api/health`
- [ ] Frontend startet mit `npm run dev`
- [ ] Frontend erreichbar unter `http://localhost:5173` oder `http://localhost:5174`
- [ ] Registrierung funktioniert
- [ ] Login funktioniert
- [ ] Räume werden geladen
- [ ] Sitzplätze werden geladen
- [ ] Assets werden geladen
- [ ] Buchung kann erstellt werden
- [ ] automatische Sitzplatzzuweisung funktioniert
- [ ] Doppelbuchung wird verhindert
- [ ] Logout funktioniert
- [ ] `pytest -q` läuft erfolgreich
