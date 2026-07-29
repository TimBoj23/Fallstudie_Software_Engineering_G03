# Kundendokumentation und Teamreflexion RePlan

**Projekt:** RePlan Workspace  
**Stand:** 29.07.2026  
**Bezug:** Konzeptionsplan / Lastenheft in [2_Konzeptionsplan.md](./2_Konzeptionsplan.md)

Dieses Handout fasst den aktuellen Stand der Anwendung aus zwei Perspektiven zusammen:

1. Kundensicht: Was kann die Anwendung, welche Anforderungen wurden umgesetzt und welche Architektur wurde gewählt?
2. Teamsicht: Welche Tätigkeiten, Entscheidungen und Problemlösungen haben die vier Entwickler übernommen?

---

## Teil 1: Kundenteil

### 1. Ziel der Anwendung

RePlan ist eine webbasierte Raum- und Ressourcenplanungs-App. Die Anwendung unterstützt Unternehmen dabei, Räume, Sitzplätze in Shared Offices und Ausstattung zentral zu verwalten, Verfügbarkeiten zu prüfen und Buchungen konfliktfrei durchzuführen.

Die zentrale Idee aus dem Lastenheft war:

- Räume und Ressourcen sollen auffindbar und buchbar sein.
- Doppelbuchungen sollen verhindert werden.
- Nutzer sollen eigene Buchungen verwalten können.
- Administratoren sollen Stammdaten und Buchungen zentral kontrollieren können.
- Die Anwendung soll über eine Weboberfläche bedienbar und nachvollziehbar dokumentiert sein.

### 2. Implementierter Funktionsumfang

#### Nutzerfunktionen

- Registrierung, Login und Logout
- Bearbeitung des eigenen Profils inklusive Name, E-Mail, Passwort und Profilbild
- Passwort-vergessen-/Passwort-zurücksetzen-Funktion als lokaler MVP
- Anzeige von Räumen, Shared Offices/Sitzplätzen und Ausstattung
- Suche und Filterung nach Objekttyp, Zeitraum und Verfügbarkeit
- Buchung ganzer Räume
- Buchung konkreter Sitzplätze in Shared Offices
- automatische Sitzplatzzuweisung, wenn kein konkreter Platz gewählt wird
- Buchung von Assets wie Beamer, Laptop oder Whiteboard
- Kalender- und Zeitblockansichten für buchbare Objekte
- Anzeige, Bearbeitung, Verlängerung, Kopie und Stornierung eigener Buchungen
- Historie der eigenen Buchungen nach Typ und Datum
- Einladungsfunktion per manuell teilbarem Code/Link
- Check-in und Check-out, zusätzlich QR-Code-gestützte Prüfung
- iCalendar-Export einzelner Buchungen
- Favoriten und Dark Mode
- In-App-Benachrichtigungen

#### Administratorfunktionen

- geschützter Adminbereich
- Verwaltung von Räumen, Sitzplätzen und Assets
- Verwaltung aller Buchungen
- Anzeige, welcher Nutzer eine Buchung erstellt hat
- Nutzerverwaltung inklusive Rollenänderung
- Anlegen neuer Nutzer
- zentrales Zurücksetzen von Passwörtern
- Anzeige von Nutzerfotos
- Belegungs-, Statistik- und Audit-Ansichten
- Demo-Reset für präsentationsfähige Ausgangsdaten

### 3. Gegenüberstellung Lastenheft und Umsetzung

| Anforderung aus dem Lastenheft | Umsetzung | Relevante Dateien |
| --- | --- | --- |
| Räume sollen verwaltet werden können. | Räume können im Backend modelliert, gespeichert, über API bereitgestellt und im Adminbereich verwaltet werden. | [src/models/room.py](../src/models/room.py), [src/services/room_service.py](../src/services/room_service.py), [src/routes/room_routes.py](../src/routes/room_routes.py), [frontend/src/pages/Admin.jsx](../frontend/src/pages/Admin.jsx) |
| Ressourcen wie Beamer, Laptops oder Whiteboards sollen erfassbar sein. | Assets sind als eigener Objekttyp umgesetzt und können angezeigt, gefiltert, gebucht und administriert werden. | [src/models/asset.py](../src/models/asset.py), [src/services/asset_service.py](../src/services/asset_service.py), [src/routes/asset_routes.py](../src/routes/asset_routes.py), [frontend/src/pages/Assets.jsx](../frontend/src/pages/Assets.jsx) |
| Nutzer sollen Räume und Ressourcen anzeigen können. | Frontend-Seiten zeigen Räume, Shared Offices und Ausstattung getrennt und nutzen API-Endpunkte. | [frontend/src/pages/Rooms.jsx](../frontend/src/pages/Rooms.jsx), [frontend/src/pages/Availability.jsx](../frontend/src/pages/Availability.jsx), [frontend/src/pages/Assets.jsx](../frontend/src/pages/Assets.jsx), [frontend/src/api/roomsApi.js](../frontend/src/api/roomsApi.js), [frontend/src/api/assetsApi.js](../frontend/src/api/assetsApi.js) |
| Verfügbarkeiten sollen für Zeiträume prüfbar sein. | Verfügbarkeit wird über Backend-Services geprüft und im Frontend mit Kalender-/Statusansichten dargestellt. | [src/services/booking_service.py](../src/services/booking_service.py), [frontend/src/components/ObjectCalendar.jsx](../frontend/src/components/ObjectCalendar.jsx), [frontend/src/utils/calendar.js](../frontend/src/utils/calendar.js) |
| Nutzer sollen Räume oder Ressourcen buchen können. | Buchungen werden über ein zentrales Buchungsformular erstellt und backendseitig validiert. | [frontend/src/pages/CreateBooking.jsx](../frontend/src/pages/CreateBooking.jsx), [frontend/src/api/bookingsApi.js](../frontend/src/api/bookingsApi.js), [src/routes/booking_routes.py](../src/routes/booking_routes.py), [src/services/booking_service.py](../src/services/booking_service.py) |
| Das System soll Buchungskonflikte erkennen. | Der BookingService prüft Überschneidungen und lehnt Konflikte ab. | [src/services/booking_service.py](../src/services/booking_service.py), [src/repositories/booking_repository.py](../src/repositories/booking_repository.py) |
| Das System soll Doppelbuchungen verhindern. | Räume, Assets und Sitzplätze werden gegen parallele Buchungen geprüft; zusätzlich darf ein Nutzer nicht mehrere Sitzplätze gleichzeitig buchen. | [src/services/booking_service.py](../src/services/booking_service.py), [src/models/booking.py](../src/models/booking.py) |
| Nutzer sollen eigene Buchungen sehen und stornieren können. | Eigene Buchungen werden inklusive Historie, Filter, Status und Stornierung angezeigt. | [frontend/src/pages/MyBookings.jsx](../frontend/src/pages/MyBookings.jsx), [frontend/src/components/BookingCard.jsx](../frontend/src/components/BookingCard.jsx), [src/routes/booking_routes.py](../src/routes/booking_routes.py) |
| Administratoren sollen Räume, Ressourcen und Buchungen verwalten können. | Der Adminbereich bündelt Verwaltung für Stammdaten, Nutzer und Buchungen. | [frontend/src/pages/Admin.jsx](../frontend/src/pages/Admin.jsx), [src/routes/user_routes.py](../src/routes/user_routes.py), [src/routes/room_routes.py](../src/routes/room_routes.py), [src/routes/asset_routes.py](../src/routes/asset_routes.py), [src/routes/seat_routes.py](../src/routes/seat_routes.py) |
| Rollen und Rechte sollen einfach unterstützt werden. | Nutzerrollen werden im Backend gespeichert, geprüft und im Frontend sichtbar gemacht. | [src/models/user.py](../src/models/user.py), [src/utils/auth_middleware.py](../src/utils/auth_middleware.py), [src/services/user_service.py](../src/services/user_service.py), [frontend/src/state/authStore.js](../frontend/src/state/authStore.js) |
| Die wichtigsten Abläufe sollen über eine Weboberfläche bedienbar sein. | React/Vite-Frontend bietet Navigation, Formulare, Karten, Kalender, Adminbereich und Buchungshistorie. | [frontend/src/App.jsx](../frontend/src/App.jsx), [frontend/src/components/AppShell.jsx](../frontend/src/components/AppShell.jsx), [frontend/src/components/ResourceCard.jsx](../frontend/src/components/ResourceCard.jsx) |
| Die Geschäftslogik soll testbar sein. | Backend- und Frontend-Tests prüfen Buchungslogik, Kalenderfunktionen, UI-Hilfslogik und Zeitumrechnung. | [docs/4_Testdokumentation.md](./4_Testdokumentation.md), [frontend/src/tests/calendar.test.js](../frontend/src/tests/calendar.test.js), [frontend/src/tests/bookingUi.test.js](../frontend/src/tests/bookingUi.test.js) |
| Architektur und Entscheidungen sollen dokumentiert werden. | Konzeptionsplan, UML-Übersicht, Testdokumentation, Abschlussdokumentation und Sprintdokumente beschreiben Planung und Umsetzung. | [docs/2_Konzeptionsplan.md](./2_Konzeptionsplan.md), [docs/3_UML.md](./3_UML.md), [docs/5_Abschlussdokumentation.md](./5_Abschlussdokumentation.md), [docs/Sprints/Sprint_III_Umsetzungsplan.md](./Sprints/Sprint_III_Umsetzungsplan.md) |
| Installation und Ausführung sollen beschrieben werden. | Die Anwendung ist als lokale Fullstack-Demo mit getrenntem Backend und Frontend lauffähig. | [README.md](../README.md), [requirements.txt](../requirements.txt), [frontend/package.json](../frontend/package.json), [src/main.py](../src/main.py) |

### 4. Sonderfunktionen über das ursprüngliche MVP hinaus

Einige Funktionen wurden über die Kernanforderungen hinaus umgesetzt, weil sie die Demo fachlich vollständiger und für Kunden besser nachvollziehbar machen:

- Sitzplätze als eigene buchbare Entität innerhalb eines Raumes
- automatische Sitzplatzzuweisung
- Regel gegen parallele Sitzplatzbuchungen eines Nutzers
- grafischer Shared-Office-Sitzplan
- Kalender- und Zeitblockansichten pro Objekt
- Benutzerfotos und Buchungsbesitzer in Adminansichten
- Passwortreset für Nutzer und Admins
- Einladungen mit Code, Link und Passwortschutz
- QR-Code-gestützter Check-in
- iCalendar-Export
- In-App-Benachrichtigungen
- Dark Mode
- Favoriten
- Audit-Protokoll
- Demo-Reset und Seed-Daten für präsentationsfähige Testdaten

### 5. Gewählte Architektur

RePlan wurde als lokale Fullstack-Anwendung umgesetzt:

```text
React/Vite-Frontend
        |
        | REST/JSON + Bearer-Token
        v
Flask-Backend mit Blueprints
        |
        v
Service-Schicht für Geschäftslogik
        |
        v
Repository-Schicht für Datenzugriff
        |
        v
SQLite-Datenbank mit einmaliger JSON-Migration
```

#### Begründung der Architekturentscheidung

Die gewählte Architektur trennt Oberfläche, API, Geschäftslogik und Datenhaltung klar voneinander. Dadurch bleibt die Buchungslogik zentral im Backend und ist nicht auf einzelne Frontend-Ansichten verteilt.

Für die Datenhaltung wurde SQLite gewählt, weil es für den Projektumfang passend ist:

- kein separater Datenbankserver notwendig
- lokal einfach ausführbar
- SQL-basierte Persistenz statt reiner JSON-Dateien
- gute Eignung für eine bewertbare Demo
- später erweiterbar in Richtung normalisierter relationaler Tabellen

Die vorhandenen JSON-Daten wurden nicht verworfen, sondern über eine Migrationslogik in die SQLite-basierte Repository-Schicht übernommen. Damit blieb der Übergang kontrollierbar und die bestehenden Services konnten weitgehend erhalten bleiben.

Relevante Architekturdateien:

- [docs/3_UML.md](./3_UML.md)
- [src/main.py](../src/main.py)
- [src/routes/](../src/routes/)
- [src/services/](../src/services/)
- [src/repositories/](../src/repositories/)
- [src/models/](../src/models/)
- [frontend/src/](../frontend/src/)

### 6. Bewusste Grenzen des Prototyps

RePlan ist eine lokale Projekt- und Demoanwendung. Einige produktive Aspekte wurden bewusst abgegrenzt:

- kein echter E-Mail-Versand über SMTP
- keine produktive Deployment-Konfiguration
- keine Single-Sign-On-Anbindung
- keine externe Kalender-Synchronisierung
- keine produktive Token-Sperrliste
- SQLite wird generisch über Repository-Datensätze genutzt; eine vollständig normalisierte Datenbank wäre ein nächster Ausbauschritt

---

## Teil 2: Selbstreflexion des Entwicklungsteams

### 1. Rollenverteilung

| Rolle | Verantwortliche Person | Aufgaben |
| --- | --- | --- |
| Projektmanagement | Florian Haentjes | Terminüberwachung, Pflege des Zeitplans, Koordination von Meetings, Nachverfolgung offener Aufgaben, Sicherstellung des Projektfortschritts |
| Scrum Master | Tim-Oliver Strauß | Sprint Planning, Review, Retrospective, Unterstützung des iterativen Vorgehens |
| Requirements Engineering / Dokumentation | Alexander Vetrenko | Sammlung und Strukturierung von Anforderungen, Use Cases, User Stories, Anforderungskatalog, Dokumentation fachlicher Entscheidungen |
| Software-Architektur / Systemdesign | gesamtes Team | Entwurf der Systemarchitektur, Modellierung von Komponenten und Datenstrukturen, Definition technischer Schnittstellen |
| Backend-Entwicklung | Alexander Vetrenko & Tim-Oliver Strauß | Umsetzung der Kernfunktionalitäten, Geschäftslogik, Buchungslogik, Schnittstellen |
| Frontend-Entwicklung / UX | Denis Nickel & Florian Haentjes | Benutzeroberfläche, Nutzerführung, Darstellung der Buchungen |
| Qualitätssicherung / Testing | Denis Nickel & Florian Haentjes | Testplanung, Testfälle, Funktionstests, Code Reviews, Fehlerprüfung |

### 2. Tim-Oliver Strauß: Backend, Scrum Master, Qualitätsmanagement

#### Durchgeführte Tätigkeiten

Tim-Oliver übernahm im Projekt eine koordinierende und technische Rolle. Als Scrum Master strukturierte er Sprint Planning, Reviews und Retrospektiven mit und achtete darauf, dass die Arbeitspakete in nachvollziehbare Schritte zerlegt wurden. Im Backend lag sein Schwerpunkt auf Buchungslogik, Validierungsregeln, API-Anbindung, Nutzerprozessen und Qualitätssicherung.

Wesentliche Tätigkeiten:

- Strukturierung der Sprintarbeit und Vorbereitung von Sprintunterlagen
- Mitarbeit an Backend-Services und Buchungsregeln
- Prüfung und Stabilisierung der API-Endpunkte
- Umsetzung bzw. Absicherung von Login, Logout und Passwortprozessen
- Erweiterung der Sitzplatzlogik inklusive automatischer Zuweisung
- Pflege der Qualitäts- und Abschlussdokumentation
- Prüfung von Build- und Testläufen vor Präsentationsständen

#### Entscheidungsfindung

Eine zentrale Entscheidung war, fachliche Regeln nicht im Frontend zu verstecken, sondern im Backend zu bündeln. Gerade bei Doppelbuchungen, Sitzplatzkonflikten und Rollenprüfungen wäre eine reine UI-Prüfung zu fehleranfällig gewesen. Die Entscheidung für eine Service-Schicht half dabei, Validierungen wiederverwendbar und testbar zu halten.

#### Problemlösungen

Ein wiederkehrendes Problem war die Zusammenführung eines teilweise autarken Frontends mit einem Backend, das die eigentliche Geschäftslogik liefern sollte. Die Lösung bestand darin, klare API-Endpunkte zu definieren, bestehende Frontend-Dummylogik schrittweise zu ersetzen und Fehler wie fehlende Ports, fehlende Dependencies oder fehlerhafte Datenmigrationen gezielt zu beheben.

### 3. Alexander Vetrenko: Backend, Requirements Engineering, Dokumentation

#### Durchgeführte Tätigkeiten

Alexander verantwortete die fachliche Strukturierung der Anforderungen und unterstützte die Backend-Entwicklung. Seine Rolle war wichtig, um aus allgemeinen Anforderungen konkrete Use Cases, User Stories und technische Arbeitspakete abzuleiten. Außerdem wirkte er an der Dokumentation fachlicher Entscheidungen mit.

Wesentliche Tätigkeiten:

- Sammlung und Strukturierung fachlicher Anforderungen
- Formulierung von Use Cases und User Stories
- Abgleich zwischen Lastenheft, Sprintzielen und Umsetzung
- Mitarbeit an Backend-Modellen und Services
- Unterstützung bei der Strukturierung von REST-Endpunkten
- Dokumentation von Architektur- und Umsetzungsentscheidungen

#### Entscheidungsfindung

Alexander achtete besonders darauf, dass Anforderungen nicht nur als Wunschliste existieren, sondern in überprüfbare Arbeitspakete überführt werden. Dadurch konnten Muss-, Soll- und Kann-Anforderungen priorisiert werden. Diese Priorisierung half dem Team, den Umfang trotz zusätzlicher Funktionen kontrollierbar zu halten.

#### Problemlösungen

Eine Herausforderung war die fachliche Trennung zwischen Räumen, Assets und Sitzplätzen. Anfangs konnten diese Objekte leicht vermischt werden, obwohl sie unterschiedliche Buchungsregeln besitzen. Durch die Modellierung als getrennte Entitäten mit gemeinsamen Buchungsmechanismen wurde die Anwendung verständlicher und erweiterbarer.

### 4. Florian Haentjes: Projektmanagement, Frontend, GitHub-Issues

#### Durchgeführte Tätigkeiten

Florian übernahm die Projektmanagementrolle und arbeitete am Frontend mit. Sein Fokus lag auf Terminüberwachung, Nachverfolgung offener Aufgaben, GitHub-Issues und einer nutzbaren Oberfläche. Damit verband er organisatorische Arbeit mit sichtbaren Ergebnissen in der Anwendung.

Wesentliche Tätigkeiten:

- Pflege und Nachverfolgung von Aufgaben über GitHub Issues
- Koordination offener Punkte für die Sprintplanung
- Mitarbeit an Frontend-Seiten und Nutzerführung
- Umsetzung von Übersichten für Räume, Assets, Sitzplätze und Buchungen
- Unterstützung bei Adminansichten und Darstellungslogik
- Abstimmung, welche Funktionen präsentationsreif gezeigt werden können

#### Entscheidungsfindung

Florian musste häufig zwischen Funktionsumfang und Verständlichkeit abwägen. Für die Präsentation war nicht nur entscheidend, dass eine Funktion technisch existiert, sondern dass sie in der Oberfläche nachvollziehbar ist. Deshalb wurden IDs aus Nutzersichten entfernt, Bilder ergänzt und Adminansichten stärker auf reale Nutzungssituationen ausgerichtet.

#### Problemlösungen

Ein wesentliches Problem war die anfänglich eigenständige Frontend-Struktur. Dadurch entstanden Inkonsistenzen zwischen Demo-Oberfläche und Backend-Logik. Die Lösung bestand darin, das Frontend schrittweise an die API anzubinden und Oberflächenzustände stärker aus echten Backenddaten abzuleiten.

### 5. Denis Nickel: Frontend, UX, Qualitätssicherung

#### Durchgeführte Tätigkeiten

Denis arbeitete schwerpunktmäßig an Frontend und UX sowie an Qualitätssicherung. Seine Aufgaben lagen in der Darstellung von Buchungen, Nutzerführung, visuellen Komponenten und manuellen Funktionstests. Besonders wichtig war, komplexe Backendprozesse für Nutzer verständlich sichtbar zu machen.

Wesentliche Tätigkeiten:

- Mitarbeit an Frontend-Komponenten und Seitenstruktur
- Gestaltung von Ressourcen- und Buchungskarten
- Unterstützung bei Kalender-, Status- und Filteransichten
- Funktionstests zentraler Nutzerabläufe
- Prüfung von UI-Verhalten bei Login, Buchung, Stornierung und Adminaktionen
- Rückmeldung zu Bedienbarkeit und Verständlichkeit

#### Entscheidungsfindung

Denis konzentrierte sich auf die Frage, welche Informationen Nutzer tatsächlich benötigen. Technische Details wie IDs sind für Admins teilweise hilfreich, für normale Nutzer aber störend. Daraus entstand die Entscheidung, Oberflächen stärker mit Namen, Bildern, Status und Zeitinformationen zu gestalten.

#### Problemlösungen

Eine Herausforderung war, unterschiedliche Objekttypen einheitlich darzustellen, ohne ihre Besonderheiten zu verlieren. Räume, Sitzplätze und Assets mussten ähnlich bedienbar sein, aber unterschiedliche Zusatzinformationen erhalten. Die Lösung bestand in wiederverwendbaren Komponenten wie ResourceCards, Buchungskarten und Kalenderansichten.

### 6. Gemeinsame Reflexion

#### Was gut funktioniert hat

- Die schrittweise Sprintstruktur half, den Projektumfang kontrollierbar zu halten.
- Die Trennung in Backend, Frontend, Dokumentation und Projektmanagement gab klare Verantwortlichkeiten.
- GitHub Issues und Dokumentation machten Fortschritt und offene Aufgaben nachvollziehbar.
- Die zentrale Backendlogik reduzierte widersprüchliche Buchungsregeln.
- Die finale Demo wurde durch realistischere Daten, Bilder und Adminfunktionen deutlich verständlicher.

#### Was schwierig war

- Frontend und Backend entwickelten sich zeitweise zu getrennt voneinander.
- Einige Anforderungen wurden erst im Verlauf präzise sichtbar, etwa Sitzplätze als eigene Entität oder Kalender-Zeitblöcke.
- Die Umstellung von JSON-Dateien auf SQLite musste vorsichtig erfolgen, damit vorhandene Daten und Schnittstellen nutzbar blieben.
- Der Präsentationsanspruch führte zu zusätzlichen Funktionen, die gegen Stabilität und Zeitrahmen abgewogen werden mussten.

#### Was wir daraus gelernt haben

- Schnittstellen sollten früher gemeinsam festgelegt werden.
- Demo-Daten sind kein Nebenthema, sondern entscheidend für eine überzeugende Präsentation.
- Rollen helfen, müssen aber regelmäßig mit tatsächlichen Aufgaben abgeglichen werden.
- Eine klare Service-Schicht erleichtert spätere Erweiterungen.
- Kleine, überprüfbare Arbeitspakete reduzieren Risiko besser als große Featureblöcke.

### 7. Fazit

Das Projekt entwickelte sich von einer geplanten Raum- und Ressourcenbuchung zu einer integrierten Fullstack-Demo mit rollenbasierter Verwaltung, SQL-Persistenz, Sitzplatzlogik, Kalenderdarstellung und erweiterten Nutzerfunktionen.

Aus Kundensicht ist RePlan als Prototyp geeignet, um die wichtigsten Abläufe einer internen Buchungsplattform zu demonstrieren. Aus Teamsicht zeigte das Projekt deutlich, wie wichtig frühe Schnittstellenklärung, klare Priorisierung und kontinuierliche Qualitätssicherung für eine lauffähige Software sind.
