# Sprint I – Durchführungsprozess und Architekturentscheidungen

In der ersten Phase wurde das Backend für das Projekt **RePlan** konzipiert und umgesetzt. Dieser Leitfaden beschreibt den gewählten Architekturansatz, den Entwicklungsprozess sowie wichtige technische Entscheidungen, um das System testbar, skalierbar und erweiterbar zu gestalten.

> **Historische Einordnung (Stand 28.07.2026):** Dieses Dokument beschreibt bewusst den Stand von Sprint I. Die damalige JSON-Persistenz wurde in Sprint III durch ein SQLite-backed Repository mit einmaliger JSON-Migration ergänzt. Das aktuelle Gesamtbild steht in [`../3_UML.md`](../3_UML.md) und [`Sprint_III_Umsetzungsplan.md`](./Sprint_III_Umsetzungsplan.md).

## Architektur: Schichtenmodell (Layered Architecture)

Um das Projekt für eine große Nutzeranzahl ausrollbar zu machen und eine saubere Trennung der Verantwortlichkeiten zu gewährleisten, wurde ein striktes Schichtenmodell implementiert:

1.  **Model Layer (`src/models/`):**
    Enthielt zunächst reine Datenstrukturen für User, Room, Asset und Booking; später kam Seat als eigene Entität hinzu.
    *Besonderheit:* Das `Booking`-Modell enthält bereits den Algorithmus zur Feststellung von zeitlichen Überschneidungen (`overlaps_with`), wodurch Geschäftslogik sauber gekapselt bleibt.

2.  **Repository Layer (`src/repositories/`):**
    Übernahm in Sprint I den Datenzugriff über JSON-Dateien.
    *Entscheidung:* Ein generisches `JsonRepository[T]` wurde als Basisklasse implementiert, um Thread-Safety (über `threading.Lock`) zu garantieren.
    *Skalierung:* Dieser Layer kann später ohne Änderungen an der Geschäftslogik durch ein PostgreSQL- oder MongoDB-Repository ersetzt werden.

3.  **Service Layer (`src/services/`):**
    Hier liegt die Kernlogik.
    *Der `BookingService`* orchestriert die Erstellung von Buchungen und führt die zentrale Konfliktprüfung durch, bevor Daten persistiert werden. Dependency Injection wird verwendet, um Repositories für Testzwecke austauschbar zu machen.

4.  **Routes Layer (`src/routes/`):**
    Stellt REST-Endpunkte mittels Flask Blueprints bereit.
    *Frontend-Ready:* CORS ist in `app.py` konfiguriert, alle Endpunkte geben sauberes JSON zurück, und Fehler werden mit standardisierten HTTP-Statuscodes (400, 401, 403, 404, 409) kommuniziert.

## Kernlogik: Die Konfliktprüfung

Das Herzstück der Phase 1 ist die Verhinderung von Doppelbuchungen.
Der gewählte Konfliktalgorithmus basiert auf dem **Interval-Overlap-Prinzip**.

Zwei Zeiträume \([A_{start}, A_{end})\) und \([B_{start}, B_{end})\) überschneiden sich genau dann, wenn:
$$A_{start} < B_{end} \text{ UND } A_{end} > B_{start}$$

Diese Bedingung fängt alle 4 möglichen Konfliktfälle ab:
1.  B liegt vollständig in A.
2.  A liegt vollständig in B.
3.  B beginnt während A und endet nach A.
4.  B beginnt vor A und endet während A.

Dieses Prinzip wurde sowohl auf der Datenobjekt-Ebene (`Booking.overlaps_with`) als auch in der Repository-Datenbanksuche (`BookingRepository.find_conflicts`) implementiert.

## Persistenz im JSON-Format (Sprint-I-Stand)

Gemäß den Anforderungen wurde eine einfache Datei-Persistenz im Ordner `data/` realisiert (`users.json`, `rooms.json`, `assets.json`, `bookings.json`). Lese- und Schreibzugriffe sind zur Wahrung der Datenkonsistenz gelockt.

Im aktuellen Stand bleibt diese Schnittstelle erhalten, die primäre Persistenz ist jedoch SQLite. Vorhandene JSON-Daten werden beim ersten Zugriff migriert.

## Testing & Qualitätssicherung

Die Kernfunktionen, insbesondere der `BookingService`, wurden mit `pytest` testgetrieben entwickelt (`tests/test_booking_service.py`).
Die Tests deckten Positivfälle (erfolgreiche Buchung, Stornierung) sowie Negativfälle (alle vier Konfliktarten, Buchung in der Vergangenheit, Berechtigungsfehler) ab. Spätere Sprints ergänzten SQLite-, Nutzer-, Sitzplatz-, Einladungs-, Serien-, Check-in/-out- und Frontend-Tests.

## Terminal-Demo

Als Proof-of-Concept wurde eine interaktive Terminal-Demo (`scripts/demo.py`) implementiert.
Diese kann manuell bedient werden, bietet aber auch einen automatisierten Durchlauf (`--auto`), der alle Szenarien (Nutzer anlegen, Räume/Assets anzeigen, Buchen, Doppelbuchung verhindern, Stornieren) eindrucksvoll demonstriert.
