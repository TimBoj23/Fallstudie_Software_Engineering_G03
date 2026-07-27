# Sprint III – Umsetzungsplan RePlan

## Ziel

Der Branch `G03_Backend` basiert lokal auf `main`. Trotz des Branch-Namens werden Backend- und Frontend-Anpassungen gesammelt umgesetzt.

Ziel des Sprints ist es, RePlan von einer lokalen MVP-Demo weiter in Richtung einer stabileren Buchungsanwendung zu entwickeln. Im Fokus stehen SQL-Persistenz, bessere Uebersichten, Medien/Bilder, Passwortverwaltung und Admin-Funktionen.

## Anforderungen

### Persistenz

- JSON-Dateien sollen nicht mehr die primaere Datenhaltung sein.
- Eine SQL-Datenbank soll die Daten verwalten.
- Bestehende JSON-Daten sollen beim ersten Start in die SQL-Datenbank migriert werden koennen.

### Buchbare Objekte

Die App verwaltet drei buchbare Objekttypen:

- Assets
- Sitzplaetze in Shared Offices
- Seminarräume bzw. ganze Raeume

### Uebersichten und Suche

- Raeume, Sitzplaetze und Assets brauchen Such- und Filterfunktionen.
- Die Uebersichten sollen zeigen, ob ein Objekt im gewaehlten Zeitraum buchbar oder belegt ist.
- Fuer die Demo sollen mehr Beispielobjekte vorhanden sein.

### Bilder

- Seminarräume sollen Bild-URLs bzw. Bildpfade besitzen.
- Assets sollen Bild-URLs bzw. Bildpfade besitzen.
- Sitzplaetze sollen vorhandene reale Arbeitsplatzbilder passend zur Monitoranzahl verwenden.

### Authentifizierung und Passwortverwaltung

- Nutzer sollen eine Passwort-vergessen-/Passwort-zuruecksetzen-Funktion erhalten.
- Admins sollen Nutzer anlegen koennen.
- Admins sollen eine Uebersicht aller registrierten Nutzer sehen.
- Admins sollen Passwoerter zentral zuruecksetzen koennen.

### Buchungsregeln

- Ein Sitzplatz darf nicht doppelt gebucht werden.
- Zusaetzlich darf ein Nutzer nicht mehrere Sitzplaetze im gleichen Zeitraum buchen.

### Nutzerbereich

- Angemeldete Nutzer sollen ihre Buchungen nach Objekttyp filtern koennen:
  - Assets
  - Seminarräume
  - Sitzplaetze
- Nutzer sollen eine Historie gebuchter Objekte nach Datum anzeigen koennen.

## Umsetzung in Stufen

### Stufe 1 - Basis und Backend-Regeln

- SQLite-Persistenz einfuehren
- bestehende Repository-Schnittstellen beibehalten
- JSON-Daten beim ersten Zugriff migrieren
- Bilderfelder in Room, Asset und Seat ergaenzen
- Regel gegen parallele Sitzplatzbuchungen pro Nutzer ergaenzen
- Admin-Endpunkte fuer Nutzerliste, Nutzeranlage und Passwortreset ergaenzen
- Passwortreset-Endpunkt fuer Nutzer bereitstellen

### Stufe 2 - Frontend-Integration

- Bilder in ResourceCards anzeigen
- Buchbar/Belegt-Status in den Uebersichten anzeigen
- Filter in `Meine Buchungen` fuer Typ und Datum ergaenzen
- Admin-Tab fuer Nutzerverwaltung ergaenzen
- Admin-Passwortreset im Frontend anbinden

### Stufe 3 - Demo-Daten und Qualitaet

- mehr Demo-Raeume, Assets und Sitzplaetze erzeugen
- sinnvolle Bild-URLs/Grafiken hinterlegen
- Tests fuer neue Buchungsregel und Nutzerverwaltung ergaenzen
- Frontend-Build und Backend-Tests pruefen

## Technische Entscheidung

Fuer diesen Sprint wird SQLite verwendet. Das passt zur aktuellen Projektgroesse, benoetigt keinen externen Datenbankserver und ermoeglicht trotzdem eine SQL-basierte Persistenz.

Die bestehenden Services sollen moeglichst wenig geaendert werden. Deshalb bleibt die Repository-Schnittstelle erhalten. Die neue SQL-Schicht ersetzt die bisherige JSON-Dateipersistenz intern.

## Finalisierungsrunde vom 27.07.2026

Die folgenden Erweiterungen wurden nach der ursprünglichen Sprint-Planung ergänzt:

- Demo-Datenbestand und Admin-Reset für Präsentationen bereinigt
- manuell teilbare Einladungscodes ohne echten E-Mail-Versand umgesetzt
- Shared-Office-Bezeichnungen, Teilbelegungsanzeige und grafischen Sitzplan ergänzt
- Buchungen inklusive Folgeterminen bearbeitbar und verlängerbar gemacht
- Einzel- und Serienstornierung voneinander getrennt
- In-App-Benachrichtigungen für bevorstehende, laufende und stornierte Buchungen ergänzt
- Profilbildauswahl mit Vorschau und verständlichem Browser-Dateidialog verbessert
- Dokumentstruktur und Sprint-Dateinamen vereinheitlicht

Die daraus abgeleiteten GitHub-Issue-Vorlagen stehen in `docs/Kanban_Aktualisierungen.md`.
