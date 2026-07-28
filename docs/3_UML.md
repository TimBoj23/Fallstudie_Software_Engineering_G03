# UML- und Architekturübersicht RePlan

**Stand:** 28.07.2026
**Bezug:** aktueller Fullstack-Prototyp auf Basis von Flask, React/Vite und SQLite

## 1. Systemkontext

```mermaid
flowchart LR
    User[Mitarbeitende] -->|Browser| Frontend[React/Vite-Frontend]
    Admin[Administrierende] -->|Browser| Frontend
    Guest[Eingeladene Person] -->|Code / Link + Passwort| Frontend
    Frontend -->|REST/JSON + Bearer-Token| API[Flask-API]
    API --> Services[Service-Schicht]
    Services --> Repositories[Repository-Schicht]
    Repositories --> SQLite[(SQLite)]
    Repositories -. einmalige Migration .-> JSON[(vorhandene JSON-Daten)]
    Seed[Seed-Skript] --> Repositories
    Git[(Git)] --> Images[Versionierte Bilder]
    Images --> Frontend
```

Ein externer E-Mail-Dienst gehört bewusst nicht zum Prototyp. Einladungslinks, Einladungscodes und Passwörter werden manuell weitergegeben; Benachrichtigungen bleiben innerhalb der Anwendung.

## 2. Schichtenmodell

| Schicht | Verzeichnis | Verantwortung |
| --- | --- | --- |
| Präsentation | `frontend/src/` | Navigation, Formulare, Zeit- und Sitzplanansichten, Dark Mode und API-Aufrufe |
| HTTP/API | `app.py`, `src/routes/` | Flask-Blueprints, Eingabeprüfung, Authentifizierung und HTTP-Statuscodes |
| Geschäftslogik | `src/services/` | Buchungsregeln, Konflikte, Einladungen, Serien, Anwesenheit, Nutzer- und Admin-Abläufe |
| Domäne | `src/models/` | Dataclasses und Enums für User, Room, Seat, Asset und Booking |
| Datenzugriff | `src/repositories/` | Einheitliche CRUD-Schnittstellen und Such-/Konfliktabfragen |
| Persistenz | `data/replan.sqlite`, JSON-Migration | Lokale Demo-Datenhaltung; Datenbankdatei wird nicht in Git versioniert |

## 3. Domänenmodell

```mermaid
classDiagram
    class User {
      +string id
      +string name
      +string email
      +UserRole role
      +string password_hash
      +string image_url
      +string reset_token
      +string reset_token_expires_at
      +bool is_active
      +string[] favorite_targets
    }

    class Room {
      +string id
      +string name
      +string number
      +int capacity
      +string room_type
      +string location
      +string[] equipment
      +string image_url
      +bool is_active
    }

    class Seat {
      +string id
      +string room_id
      +string label
      +int monitor_count
      +string image_url
      +bool is_active
    }

    class Asset {
      +string id
      +string name
      +AssetType asset_type
      +string location
      +string image_url
      +bool is_active
    }

    class Booking {
      +string id
      +string user_id
      +string target_id
      +BookingTargetType target_type
      +string title
      +string start_time
      +string end_time
      +BookingStatus status
      +string room_id
      +bool auto_assigned_seat
      +string invitation_code
      +string access_password_hash
      +string[] invitation_emails
      +string[] participant_emails
      +string checked_in_at
      +string checked_out_at
      +string series_id
      +int recurrence_index
    }

    User "1" --> "0..*" Booking : erstellt
    Room "1" --> "0..*" Seat : enthält
    Booking "0..*" --> "0..1" Room : Ziel oder Kontext
    Booking "0..*" --> "0..1" Seat : Ziel
    Booking "0..*" --> "0..1" Asset : Ziel
```

`Booking.target_type` bestimmt, ob `target_id` auf einen Raum, Sitzplatz oder ein Asset verweist. Bei Sitzplatzbuchungen speichert `room_id` zusätzlich den Shared-Office-Kontext.

## 4. Buchungs- und Anwesenheitsablauf

```mermaid
stateDiagram-v2
    [*] --> Entwurf
    Entwurf --> Aktiv: Zeitraum gültig und konfliktfrei
    Entwurf --> Abgelehnt: ungültig / Konflikt
    Aktiv --> Eingecheckt: Beginn erreicht + Check-in
    Eingecheckt --> Ausgecheckt: manueller Check-out
    Eingecheckt --> Ausgecheckt: Buchungsende erreicht
    Aktiv --> Abgelaufen: Buchungsende ohne Check-in
    Aktiv --> Storniert: berechtigte Stornierung
    Eingecheckt --> Storniert: Admin-/Nutzeraktion
    Storniert --> [*]
    Ausgecheckt --> [*]
    Abgelaufen --> [*]
```

Wichtig: Der persistierte Buchungsstatus unterscheidet `active` und `cancelled`. Eingecheckt/ausgecheckt wird über Zeitstempel modelliert. Die Oberfläche berechnet daraus den aktuellen Anwesenheits- und Verfügbarkeitszustand.

## 5. Sequenz: Buchung erstellen

```mermaid
sequenceDiagram
    actor U as Nutzer
    participant F as React-Frontend
    participant R as Flask-Route
    participant S as BookingService
    participant Repo as Repositories

    U->>F: Objekt und lokalen Zeitraum wählen
    F->>R: POST Buchung mit UTC-Zeitstempeln
    R->>S: validierte Nutzerdaten + Payload
    S->>Repo: Objekt/Nutzer laden
    S->>Repo: Konflikte im Halbintervall [Start, Ende) suchen
    alt Konflikt oder ungültige Eingabe
      S-->>R: fachlicher Fehler
      R-->>F: 400/409 + verständliche Meldung
    else frei
      S->>Repo: Buchung oder Serie speichern
      R-->>F: 201 + öffentliche Buchungsdaten
      F-->>U: Bestätigung und aktualisierte Übersicht
    end
```

## 6. Sicherheits- und Datenentscheidungen

- Passwörter und Buchungspasswörter werden ausschließlich als Hash gespeichert.
- API-Zugriffe verwenden signierte, zeitlich begrenzte Bearer-Tokens.
- Rollenprüfungen erfolgen im Backend; die Oberfläche allein entscheidet nicht über Berechtigungen.
- `SECRET_KEY` muss außerhalb der lokalen Demo als Umgebungsvariable gesetzt werden.
- Datum und Uhrzeit werden an der Browsergrenze eindeutig übertragen und backendseitig normalisiert; die Anzeige erfolgt in der konfigurierten lokalen Zeitzone.
- Bilder und Seed-Definitionen sind versioniert, `data/replan.sqlite` sowie Laufzeit- und Nutzerdaten nicht.

## 7. Architekturgrenzen

Die SQLite-Schicht speichert Repository-Datensätze generisch und ist damit für den lokalen Prototyp geeignet. Ein produktives System sollte daraus normalisierte SQL-Tabellen, echte Migrationen, einen externen Maildienst, serverseitig verwaltete Token-Sperrung und eine Deployment-Konfiguration entwickeln.
