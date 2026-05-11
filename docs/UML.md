# UML – Klassendiagramm

## Raum- und Ressourcenplanungssystem (RePlan)

Das folgende Klassendiagramm modelliert die zentralen Entitäten und deren Beziehungen der webbasierten Raum- und Ressourcenplanungsanwendung.

Das Gesamtdiagramm ist aus Gründen der Übersichtlichkeit in **vier thematische Teildiagramme** aufgeteilt:

1. [Domänenmodell & Enumerationen](#1-domänenmodell--enumerationen)
2. [Buchungslogik](#2-buchungslogik)
3. [Raum- und Ressourcenverwaltung](#3-raum--und-ressourcenverwaltung)
4. [Nutzerverwaltung](#4-nutzerverwaltung)

---

## 1. Domänenmodell & Enumerationen

Zeigt alle Kernentitäten mit ihren Attributen sowie die verwendeten Enumerationen und deren Beziehungen untereinander.

```mermaid
classDiagram

    %% ─────────────────────────────────────────────
    %% Enum-ähnliche Typen (als Klassen dargestellt)
    %% ─────────────────────────────────────────────

    class Rolle {
        <<enumeration>>
        MITARBEITER
        ADMIN
    }

    class BuchungsStatus {
        <<enumeration>>
        AKTIV
        STORNIERT
        ABGESCHLOSSEN
    }

    class RaumTyp {
        <<enumeration>>
        MEETINGRAUM
        KONFERENZRAUM
        ARBEITSPLATZ
        SCHULUNGSRAUM
        PROJEKTRAUM
    }

    class RessourcenTyp {
        <<enumeration>>
        BEAMER
        WHITEBOARD
        LAPTOP
        MONITOR
        ADAPTER
        MODERATIONSMATERIAL
        PRAESENTATIONSTECHNIK
    }

    %% ─────────────────────────────────────────────
    %% Kernentitäten (Models)
    %% ─────────────────────────────────────────────

    class Nutzer {
        -int nutzer_id
        -str name
        -str email
        -str passwort_hash
        -Rolle rolle
        +get_nutzer_id() int
        +get_name() str
        +set_name(name: str) void
        +get_email() str
        +set_email(email: str) void
        +get_passwort_hash() str
        +set_passwort_hash(hash: str) void
        +get_rolle() Rolle
        +set_rolle(rolle: Rolle) void
        +liste_buchungen() list
        +ist_admin() bool
    }

    class Raum {
        -int raum_id
        -str raumname
        -str raumnummer
        -int kapazitaet
        -str standort
        -RaumTyp typ
        -str beschreibung
        -list ausstattung
        +get_raum_id() int
        +get_raumname() str
        +set_raumname(name: str) void
        +get_raumnummer() str
        +set_raumnummer(nr: str) void
        +get_kapazitaet() int
        +set_kapazitaet(kap: int) void
        +get_standort() str
        +set_standort(standort: str) void
        +get_typ() RaumTyp
        +set_typ(typ: RaumTyp) void
        +get_beschreibung() str
        +set_beschreibung(text: str) void
        +get_ausstattung() list
        +set_ausstattung(liste: list) void
        +ist_verfuegbar(start: datetime, ende: datetime) bool
        +get_buchungen() list
    }

    class Ressource {
        -int ressourcen_id
        -str name
        -RessourcenTyp typ
        -str beschreibung
        -str standort
        +get_ressourcen_id() int
        +get_name() str
        +set_name(name: str) void
        +get_typ() RessourcenTyp
        +set_typ(typ: RessourcenTyp) void
        +get_beschreibung() str
        +set_beschreibung(text: str) void
        +get_standort() str
        +set_standort(standort: str) void
        +ist_verfuegbar(start: datetime, ende: datetime) bool
        +get_buchungen() list
    }

    class Buchung {
        -int buchungs_id
        -int nutzer_id
        -datetime start_zeit
        -datetime end_zeit
        -BuchungsStatus status
        -datetime erstellt_am
        -str notiz
        +get_buchungs_id() int
        +get_nutzer_id() int
        +get_start_zeit() datetime
        +set_start_zeit(t: datetime) void
        +get_end_zeit() datetime
        +set_end_zeit(t: datetime) void
        +get_status() BuchungsStatus
        +set_status(s: BuchungsStatus) void
        +get_erstellt_am() datetime
        +get_notiz() str
        +set_notiz(text: str) void
        +stornieren() bool
        +ist_aktiv() bool
        +hat_zeitkonflikt(andere: Buchung) bool
    }

    class RaumBuchung {
        -int raum_id
        +get_raum_id() int
        +set_raum_id(id: int) void
    }

    class RessourcenBuchung {
        -int ressourcen_id
        +get_ressourcen_id() int
        +set_ressourcen_id(id: int) void
    }

    %% ─────────────────────────────────────────────
    %% Beziehungen: Vererbung
    %% ─────────────────────────────────────────────

    Buchung <|-- RaumBuchung : extends
    Buchung <|-- RessourcenBuchung : extends

    %% ─────────────────────────────────────────────
    %% Beziehungen: Assoziationen (Fachdomäne)
    %% ─────────────────────────────────────────────

    Nutzer "1" --> "0..*" Buchung : erstellt
    Nutzer "1" --> "1" Rolle : hat

    RaumBuchung "0..*" --> "1" Raum : reserviert
    RessourcenBuchung "0..*" --> "1" Ressource : reserviert

    Buchung "1" --> "1" BuchungsStatus : hat
    Raum "1" --> "1" RaumTyp : hat
    Ressource "1" --> "1" RessourcenTyp : hat
```

---

## 2. Buchungslogik

Zeigt `BuchungsService` und `BuchungsRepository` sowie deren Abhängigkeiten zu den Buchungs-Entitäten.

```mermaid
classDiagram

    class Buchung {
        -int buchungs_id
        -int nutzer_id
        -datetime start_zeit
        -datetime end_zeit
        -BuchungsStatus status
        -datetime erstellt_am
        -str notiz
        +get_buchungs_id() int
        +get_nutzer_id() int
        +get_status() BuchungsStatus
        +stornieren() bool
        +ist_aktiv() bool
        +hat_zeitkonflikt(andere: Buchung) bool
    }

    class RaumBuchung {
        -int raum_id
        +get_raum_id() int
        +set_raum_id(id: int) void
    }

    class RessourcenBuchung {
        -int ressourcen_id
        +get_ressourcen_id() int
        +set_ressourcen_id(id: int) void
    }

    class BuchungsService {
        +erstelle_raumbuchung(nutzer: Nutzer, raum: Raum, start: datetime, ende: datetime) RaumBuchung
        +erstelle_ressourcenbuchung(nutzer: Nutzer, ressource: Ressource, start: datetime, ende: datetime) RessourcenBuchung
        +storniere_buchung(buchungs_id: int, nutzer: Nutzer) bool
        +pruefe_zeitkonflikt(buchbare_id: int, start: datetime, ende: datetime) bool
        +get_buchungen_von_nutzer(nutzer_id: int) list
        +get_alle_buchungen() list
    }

    class BuchungsRepository {
        +speichere(buchung: Buchung) Buchung
        +finde_by_id(buchungs_id: int) Buchung
        +finde_by_nutzer(nutzer_id: int) list
        +finde_alle() list
        +aktualisiere(buchung: Buchung) Buchung
        +loesche(buchungs_id: int) bool
        +finde_konflikte(buchbare_id: int, start: datetime, ende: datetime) list
    }

    Buchung <|-- RaumBuchung : extends
    Buchung <|-- RessourcenBuchung : extends

    BuchungsService ..> BuchungsRepository : verwendet
    BuchungsService ..> Buchung : erzeugt / verwaltet
    BuchungsService ..> RaumBuchung : erzeugt
    BuchungsService ..> RessourcenBuchung : erzeugt
```

---

## 3. Raum- und Ressourcenverwaltung

Zeigt `RaumService`, `RessourcenService` und deren jeweilige Repositories sowie die Entitäten `Raum` und `Ressource`.

```mermaid
classDiagram

    class Raum {
        -int raum_id
        -str raumname
        -str raumnummer
        -int kapazitaet
        -str standort
        -RaumTyp typ
        -str beschreibung
        -list ausstattung
        +get_raum_id() int
        +get_raumname() str
        +set_raumname(name: str) void
        +get_kapazitaet() int
        +set_kapazitaet(kap: int) void
        +get_typ() RaumTyp
        +set_typ(typ: RaumTyp) void
        +ist_verfuegbar(start: datetime, ende: datetime) bool
        +get_buchungen() list
    }

    class Ressource {
        -int ressourcen_id
        -str name
        -RessourcenTyp typ
        -str beschreibung
        -str standort
        +get_ressourcen_id() int
        +get_name() str
        +set_name(name: str) void
        +get_typ() RessourcenTyp
        +set_typ(typ: RessourcenTyp) void
        +get_standort() str
        +set_standort(standort: str) void
        +ist_verfuegbar(start: datetime, ende: datetime) bool
        +get_buchungen() list
    }

    class RaumService {
        +get_alle_raeume() list
        +get_raum_by_id(raum_id: int) Raum
        +erstelle_raum(daten: dict) Raum
        +aktualisiere_raum(raum_id: int, daten: dict) Raum
        +loesche_raum(raum_id: int) bool
        +suche_verfuegbare_raeume(start: datetime, ende: datetime) list
    }

    class RessourcenService {
        +get_alle_ressourcen() list
        +get_ressource_by_id(ressourcen_id: int) Ressource
        +erstelle_ressource(daten: dict) Ressource
        +aktualisiere_ressource(ressourcen_id: int, daten: dict) Ressource
        +loesche_ressource(ressourcen_id: int) bool
        +suche_verfuegbare_ressourcen(start: datetime, ende: datetime) list
    }

    class RaumRepository {
        +speichere(raum: Raum) Raum
        +finde_by_id(raum_id: int) Raum
        +finde_alle() list
        +aktualisiere(raum: Raum) Raum
        +loesche(raum_id: int) bool
    }

    class RessourcenRepository {
        +speichere(ressource: Ressource) Ressource
        +finde_by_id(ressourcen_id: int) Ressource
        +finde_alle() list
        +aktualisiere(ressource: Ressource) Ressource
        +loesche(ressourcen_id: int) bool
    }

    RaumService ..> RaumRepository : verwendet
    RaumService ..> Raum : erzeugt / verwaltet

    RessourcenService ..> RessourcenRepository : verwendet
    RessourcenService ..> Ressource : erzeugt / verwaltet
```

---

## 4. Nutzerverwaltung

Zeigt `NutzerService`, `NutzerRepository` und die `Nutzer`-Entität mit der `Rolle`-Enumeration.

```mermaid
classDiagram

    class Rolle {
        <<enumeration>>
        MITARBEITER
        ADMIN
    }

    class Nutzer {
        -int nutzer_id
        -str name
        -str email
        -str passwort_hash
        -Rolle rolle
        +get_nutzer_id() int
        +get_name() str
        +set_name(name: str) void
        +get_email() str
        +set_email(email: str) void
        +get_passwort_hash() str
        +set_passwort_hash(hash: str) void
        +get_rolle() Rolle
        +set_rolle(rolle: Rolle) void
        +liste_buchungen() list
        +ist_admin() bool
    }

    class NutzerService {
        +registriere_nutzer(name: str, email: str, passwort: str) Nutzer
        +authentifiziere_nutzer(email: str, passwort: str) Nutzer
        +get_nutzer_by_id(nutzer_id: int) Nutzer
        +aendere_rolle(nutzer_id: int, neue_rolle: Rolle) Nutzer
    }

    class NutzerRepository {
        +speichere(nutzer: Nutzer) Nutzer
        +finde_by_id(nutzer_id: int) Nutzer
        +finde_by_email(email: str) Nutzer
        +finde_alle() list
        +aktualisiere(nutzer: Nutzer) Nutzer
    }

    Nutzer "1" --> "1" Rolle : hat

    NutzerService ..> NutzerRepository : verwendet
    NutzerService ..> Nutzer : erzeugt / verwaltet
```

---

## Beschreibung der Klassen

### Entitäten (Models)

| Klasse | Beschreibung |
|---|---|
| `Nutzer` | Repräsentiert einen Systembenutzer. Kann Mitarbeiter (bucht) oder Admin (verwaltet) sein. |
| `Raum` | Ein buchbarer Ort (z. B. Meetingraum, Arbeitsplatz). Enthält Kapazität, Standort und Ausstattung. |
| `Ressource` | Ein buchbares Objekt (z. B. Beamer, Laptop). Enthält Typ und Standort. |
| `Buchung` | Abstrakte Basisklasse für alle Reservierungen. Hält Zeitraum, Status und Erstellungsdatum. |
| `RaumBuchung` | Spezialisierung von `Buchung` für die Reservierung eines Raums. |
| `RessourcenBuchung` | Spezialisierung von `Buchung` für die Reservierung einer Ressource. |

### Service-Schicht (Geschäftslogik)

| Klasse | Beschreibung |
|---|---|
| `BuchungsService` | Zentrale Geschäftslogik: Erstellt Buchungen, prüft Zeitkonflikte, storniert Buchungen. |
| `RaumService` | Verwaltungslogik für Räume (CRUD, Verfügbarkeitssuche). |
| `RessourcenService` | Verwaltungslogik für Ressourcen (CRUD, Verfügbarkeitssuche). |
| `NutzerService` | Authentifizierung, Registrierung und Rollenverwaltung. |

### Repository-Schicht (Datenzugriff)

| Klasse | Beschreibung |
|---|---|
| `BuchungsRepository` | Datenbankzugriff für Buchungen inkl. Konfliktabfrage. |
| `RaumRepository` | Datenbankzugriff für Räume. |
| `RessourcenRepository` | Datenbankzugriff für Ressourcen. |
| `NutzerRepository` | Datenbankzugriff für Nutzer (inkl. E-Mail-Suche). |

### Enumerationen

| Enum | Werte | Verwendung |
|---|---|---|
| `Rolle` | `MITARBEITER`, `ADMIN` | Steuert Zugriffsrechte im System. |
| `BuchungsStatus` | `AKTIV`, `STORNIERT`, `ABGESCHLOSSEN` | Lebenszyklus einer Buchung. |
| `RaumTyp` | `MEETINGRAUM`, `KONFERENZRAUM`, `ARBEITSPLATZ`, `SCHULUNGSRAUM`, `PROJEKTRAUM` | Kategorisierung von Räumen. |
| `RessourcenTyp` | `BEAMER`, `WHITEBOARD`, `LAPTOP`, `MONITOR`, `ADAPTER`, `MODERATIONSMATERIAL`, `PRAESENTATIONSTECHNIK` | Kategorisierung von Ressourcen. |

---

## Architekturprinzipien

Das Diagramm folgt einer **dreischichtigen Architektur**:

```
┌──────────────────────────┐
│    Routes / Controller   │  ← HTTP-Endpunkte (Flask/Web-Schicht)
├──────────────────────────┤
│      Service-Schicht     │  ← Geschäftslogik, Konfliktprüfung
├──────────────────────────┤
│    Repository-Schicht    │  ← Datenzugriff (DB / Datei)
├──────────────────────────┤
│     Model / Entitäten    │  ← Datenstrukturen der Fachdomäne
└──────────────────────────┘
```

- **Vererbung**: `RaumBuchung` und `RessourcenBuchung` erben von der abstrakten Basisklasse `Buchung`, um gemeinsame Attribute (Zeitraum, Status, Nutzer) zu teilen.
- **Konfliktprüfung**: `BuchungsService.pruefe_zeitkonflikt()` delegiert an `BuchungsRepository.finde_konflikte()`, um Doppelbuchungen systemseitig zu verhindern.
- **Rollenbasierter Zugriff**: Die `Rolle`-Enumeration auf `Nutzer` steuert, welche Operationen (z. B. Admin-CRUD) zulässig sind.
- **Getter/Setter**: Alle Attribute der Entitäten sind `private` (`-`) und werden über öffentliche (`+`) Getter- und Setter-Methoden zugegriffen, um das Kapselung-Prinzip (Encapsulation) einzuhalten.
