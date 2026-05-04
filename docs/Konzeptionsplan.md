# Konzeptionsplan

## Projekt: Entwicklung einer Raum- und Ressourcenplanungs-App

## Projektziel

Ziel des Projekts ist die Konzeption, Planung und prototypische Umsetzung einer webbasierten Raum- und Ressourcenplanungs-App.  
Die Anwendung soll es ermöglichen, Räume und Ressourcen wie Beamer, Laptops oder Arbeitsplätze effizient zu verwalten, Verfügbarkeiten zu prüfen und Buchungen konfliktfrei durchzuführen.

Im Vordergrund steht dabei nicht nur die technische Umsetzung, sondern insbesondere ein strukturierter **Software-Engineering-Prozess**.  
Dazu gehören die systematische Anforderungsanalyse, saubere Modellierung, Planung der Architektur, Priorisierung der Arbeitspakete, Sprint-Planung, Qualitätssicherung sowie nachvollziehbare Dokumentation.

---

## Kickoff / Organisatorisches / Themenauswahl / Projektrollen

### Ziel der Phase

In der Kickoff-Phase wird der organisatorische und methodische Rahmen des Projekts geschaffen.  
Hierbei wird das Thema verbindlich festgelegt, die Projektziele werden grob definiert und erste Rollen und Verantwortlichkeiten werden verteilt.

### Inhalte

- Abstimmung des Projektrahmens
- Festlegung des Themas: Raum- und Ressourcenplanungs-App
- Definition des grundsätzlichen Projektziels
- Klärung organisatorischer Rahmenbedingungen
- Grobe Zeit- und Meilensteinplanung
- Festlegung des Entwicklungs- und Kommunikationsprozesses

### Begründung der Themenwahl

Die Wahl des Themas erfolgt, weil es sich um ein praxisnahes und klar eingrenzbares Problem handelt, das typische Herausforderungen des Software Engineerings abbildet:

- Erhebung und Strukturierung von Anforderungen
- Modellierung fachlicher Prozesse
- Konfliktbehandlung bei Buchungen
- Planung eines skalierbaren und wartbaren Systems
- Testbarkeit der Geschäftslogik
- Nachvollziehbare Dokumentation von Entscheidungen

Das Thema eignet sich daher besonders gut für eine Fallstudie mit Software-Engineering-Schwerpunkt.

### Organisatorische Grundlagen

- Gemeinsames Repository anlegen (erfolgt am 13.04.2026)
- Branching-Strategie definieren (erfolgt am 13.04.2026)
- Kommunikationskanäle festlegen (steht aus)
- Meeting-Rhythmus abstimmen (steht aus)
- Definition von Arbeitsweise und Abstimmungsformaten (steht aus)

### Vorgesehene Projektrollen

Die Rollen dienen in erster Linie der Strukturierung und Verantwortung, können je nach Teamgröße kombiniert werden.

#### Projektkoordination / Projektmanagement

- Terminüberwachung
- Pflege des Zeitplans
- Koordination von Meetings
- Nachverfolgung offener Aufgaben
- Sicherstellung des Projektfortschritts

#### Requirements Engineering / Dokumentation

- Sammlung und Strukturierung von Anforderungen
- Erstellung von Use Cases und User Stories
- Pflege des Anforderungskatalogs
- Dokumentation fachlicher Entscheidungen

#### Software-Architektur / Systemdesign

- Entwurf der Systemarchitektur
- Modellierung von Komponenten und Datenstrukturen
- Definition technischer Schnittstellen
- Sicherstellung von Wartbarkeit und Erweiterbarkeit

#### Entwicklung

- Umsetzung der Kernfunktionalitäten
- Implementierung der Geschäftslogik
- Einhaltung der Architekturvorgaben
- Codepflege und Refactoring

#### Qualitätssicherung / Testing

- Testplanung
- Erstellung von Testfällen
- Durchführung von Funktionstests
- Überprüfung der Konfliktlogik und Randfälle

### Erste Projektmanagement-Entscheidungen

- Iteratives Vorgehen in drei Sprints
- Fokus auf MVP (Minimum Viable Product) und schrittweise Erweiterung
- Frühe Priorisierung zentraler Funktionen
- Kontinuierliche Dokumentation statt Dokumentation erst am Ende

---

## Finalisierung Thema / Stakeholderanalyse / Anforderungskatalog / PM

### Ziel der Phase

In dieser Phase wird das Projektthema fachlich präzisiert.  
Der Fokus liegt auf dem Verständnis des Anwendungsproblems, der Identifikation relevanter Stakeholder sowie der Erstellung eines ersten strukturierten Anforderungskatalogs.

### Finalisierung des Themas

Die Raum- und Ressourcenplanungs-App soll ein System bereitstellen, das:

- Räume verwaltbar macht
- Ressourcen erfassbar macht
- Buchungen ermöglicht
- Konflikte erkennt und verhindert
- Verfügbarkeiten transparent darstellt
- eine einfache Rollen- und Rechteverteilung unterstützt
- **ergänzen**

### Problemstellung

In vielen Kontexten erfolgt die Planung von Räumen und Ressourcen unübersichtlich, beispielsweise über Tabellen, Chat-Nachrichten oder informelle Absprachen.  
Dadurch entstehen:

- Doppelbuchungen
- fehlende Transparenz
- ineffiziente Nutzung vorhandener Ressourcen
- hoher manueller Abstimmungsaufwand

Die App soll diesen Prozess strukturieren und digital abbilden.

### Stakeholderanalyse

#### Primäre Stakeholder

**Nutzerinnen und Nutzer**

- möchten Räume oder Ressourcen schnell finden und buchen
- erwarten Übersichtlichkeit und einfache Bedienbarkeit

**Verwaltende / Administratoren**

- pflegen Räume und Ressourcen
- verwalten Verfügbarkeiten
- überwachen Buchungen
- benötigen Kontroll- und Änderungsmöglichkeiten

#### Sekundäre Stakeholder

**Projektteam**

- benötigt klare Anforderungen und stabile Planung
- ist auf sinnvolle Abgrenzung des Projektumfangs angewiesen

**Lehrende / Prüfende**

- erwarten nachvollziehbares Vorgehen
- bewerten nicht nur das Produkt, sondern den Entwicklungsprozess

### Stakeholder-Erwartungen

- funktionierende Kernlogik
- konfliktfreie Buchungsverwaltung
- nachvollziehbare Planung
- saubere Dokumentation
- softwaretechnisch begründete Entscheidungen

### Lastenheft

Entwicklung eines Raum- und Ressourcenplanungs-Systems
Dieses Dokument legt die Anforderungen und Spezifikationen für die Entwicklung einer
Web-App zur Verwaltung von Raum- und Ressourcenplanung für Unternehmen fest. Es
dient als Grundlage für die Entwicklung und Implementierung der Softwarelösung /
Fallstudie.
Das Ziel des Projektes ist die Entwicklung einer benutzerfreundlichen, effizienten und
zuverlässigen Software zur Verwaltung, Planung, Buchung und Nutzungsauswertungen von
Räumen und Ressourcen.

#### Funktionale Anforderungen

- Stammdatenverwaltung
  - Verwaltung von Räumen und Arbeitsplätzen (inkl. Location, z.B. Standort und Gebäude)
  - Verwaltung von Resourcen (inkl. Vor- und Nachlaufzeiten, z.B. MedienkoGer muss
  gecheckt werden oder Raumwechsel)
- Nutzung der Software
  - Buchung von Räumen und Resourcen (Vermeidung von Doppelbuchungen)
  - Übersicht eigener Buchungen (inkl. Stornierungen)
- Reporting und Visualisierung
  - Übersichtliche Darstellung von Resourcennutzung (z. B. pro Tag, Woche, Mitarbeiter)
  - Exportfunktionen (CSV & Excel)

#### Nicht-funktionale Anforderungen

- Leistung & Performance
  - Performante Verarbeitung der Daten
  - Performante Ladezeit des Front-Ends
  - Gleichzeitige Nutzung der App / Webseite von mehreren Nutzer:innen
- Sicherheit
  - Verschlüsselte Datenübertragung und Speicherung
  - Regelkonformität bezüglich Datenschutz (DSGVO)
- Benutzerfreundlichkeit
  - Intuitive Benutzeroberflächen und Navigation
  - Mehrsprachige Unterstützung
  - Barrierefreie Zugänglichkeitsfeatures

- Die Software ist agil zu entwickeln um Modifikationen während der Entwicklung zu erlauben.

### Projektmanagement-Schwerpunkte in dieser Phase

- Projektumfang bewusst klein und realistisch halten
- MVP früh definieren
- frühe Identifikation technischer Risiken
- Planung nicht nur nach Features, sondern auch nach Engineering-Aufgaben strukturieren

### Ergebnisse der Phase

- Thema fachlich finalisiert
- Stakeholder identifiziert
- erste Anforderungen dokumentiert
- Projektumfang grob eingegrenzt

---

## Detaillierte Anforderungen / Use Cases / Issues & Priorisierung

### Ziel der Phase

Die Anforderungen werden verfeinert und in konkrete Anwendungsfälle und bearbeitbare Arbeitspakete überführt.  
Diese Phase ist zentral für den Software-Engineering-Fokus, da hier die Grundlage für Architektur, Implementierung und Tests geschaffen wird.

### Detaillierte Anforderungen

#### Fachliche Kernobjekte

**ergänzen - eventuell ganz rausnehmen**

#### Mögliche Attribute

**ergänzen - eventuell ganz rausnehmen**

---

### Use Cases

#### Use Case 1: Raum suchen

Ein Nutzer möchte einen freien Raum für einen bestimmten Zeitraum finden.

**Ablauf**

1. Nutzer gibt Zeitraum ein
2. System prüft Verfügbarkeit
3. System zeigt passende Räume an

#### Use Case 2: Ressource buchen

Ein Nutzer möchte eine Ressource für einen bestimmten Zeitraum reservieren.

**Ablauf**

1. Nutzer wählt Ressource
2. System prüft Verfügbarkeit
3. System erstellt Buchung
4. System bestätigt Buchung

#### Use Case 3: Konflikt verhindern

Ein Nutzer versucht, einen bereits gebuchten Raum zu reservieren.

**Ablauf**

1. Nutzer startet Buchung
2. System erkennt Überschneidung
3. System lehnt Buchung ab
4. System zeigt Hinweis an

---

### User Stories

**ergänzen - eventuell ganz rausnehmen**

### Abgrenzung des MVP

Der MVP konzentriert sich auf die zentralen Kernfunktionen:

- Anzeige von Räumen und Ressourcen
- Erstellung von Buchungen
- Konfliktprüfung
- Stornierung von Buchungen
- einfache Administrationsfunktionen
- **ergänzen**

Nicht Teil des MVP:

- komplexes Rollen- und Rechtesystem
- Benachrichtigungen per E-Mail
- Kalender-Synchronisierung
- Mehrsprachigkeit
- Optimierungsalgorithmen
- Echtzeit-Kollaboration
- **ergänzen**

### Issues und Arbeitspakete

Die Anforderungen werden in technische und fachliche Issues überführt.

#### Beispielhafte fachliche Issues

- **Beispiele nennen**

#### Beispielhafte technische Issues

- **Beispiele nennen**

### Priorisierung

Die Priorisierung erfolgt nach:

- fachlicher Relevanz
- Abhängigkeiten
- Risiko
- Umsetzbarkeit im Zeitrahmen
- Beitrag zum MVP

#### Priorität Hoch

- **Beispiele nennen**

#### Priorität Mittel

- **Beispiele nennen**

#### Priorität Niedrig

- **Beispiele nennen**

### Software-Engineering-Schwerpunkt

In dieser Phase steht besonders im Fokus:

- präzise Übersetzung fachlicher Anforderungen in technische Aufgaben
- Vermeidung von Scope Creep
- Nachvollziehbarkeit von Priorisierungsentscheidungen
- Vorbereitung einer testbaren und wartbaren Umsetzung

### Ergebnisse der Phase

- detaillierte Anforderungen liegen vor
- Use Cases dokumentiert
- Issues erstellt
- MVP klar priorisiert

---

## Sprint I

### Ziel des Sprints

Sprint I konzentriert sich auf die konzeptionelle und technische Grundlage des Systems.  
Im Vordergrund stehen Architektur, Modellierung, Entwicklungsprozess und erste Basiskomponenten.

### Schwerpunkte

- Abschluss der Planungsphase
- Festlegung der Systemarchitektur
- Modellierung zentraler Entitäten
- Einrichtung des Entwicklungsprozesses
- Vorbereitung eines lauffähigen Grundgerüsts

### Geplante Inhalte

#### Architektur und Systemdesign

- Auswahl des Technologie-Stacks
- Definition der Schichtenarchitektur
- Trennung von UI, Fachlogik und Datenhaltung
- Planung zentraler Komponenten
- erste Architekturübersicht erstellen

#### Datenmodellierung

- Modellierung der Entitäten Raum, Ressource, Buchung und Nutzer
- Beziehungen zwischen den Entitäten definieren
- Validierungsregeln festlegen

#### Entwicklungsprozess

- Branching-Modell definieren
- Pull-Request-Regeln festlegen
- Definition von Code-Review-Vorgehen
- Definition von Commit-Konventionen
- Issue-Workflow festlegen

#### Qualitätssicherung vorbereiten

- Teststrategie definieren
- zentrale Testfälle identifizieren
- Kriterien für Abnahme des MVP formulieren

### Geplante Ergebnisse von Sprint I

- Architekturkonzept liegt vor
- Datenmodell ist definiert
- Repository-Struktur ist eingerichtet
- erste technische Grundlage ist vorhanden
- Kernanforderungen sind stabil dokumentiert

### Review-Kriterien

- Sind Anforderungen und Architektur konsistent?
- Ist der MVP realistisch abgegrenzt?
- Sind die zentralen Entitäten und Abläufe korrekt modelliert?
- Ist das Projekt organisatorisch und technisch bereit für die Umsetzung?

---

## Sprint II

### Ziel des Sprints

Sprint II dient der Umsetzung der wichtigsten Kernfunktionen des Systems.  
Der Schwerpunkt liegt auf der Implementierung des MVP und der Absicherung der zentralen Geschäftslogik.

### Schwerpunkte

- Implementierung der Kernfunktionalitäten
- Aufbau der Buchungslogik
- Umsetzung der Konfliktprüfung
- Erstellung erster Tests
- erste integrierte, lauffähige Systemversion

### Geplante Inhalte

#### Implementierung

- Ansicht für Räume und Ressourcen
- Buchungsformular
- Erstellen von Buchungen
- Speichern und Anzeigen bestehender Buchungen
- Validierung von Eingaben

#### Konflikt- und Fachlogik

- Überschneidungen bei Zeiträumen prüfen
- Verhinderung von Doppelbuchungen
- Behandlung ungültiger Buchungszeiträume
- Stornierung und Aktualisierung von Buchungen

#### Testing

- Unit-Tests für Konfliktprüfung
- Tests für Validierungsregeln
- manuelle Funktionstests für Kernabläufe

#### Dokumentation

- Fortschreibung der Architektur
- Dokumentation technischer Entscheidungen
- Beschreibung bekannter Einschränkungen

### Geplante Ergebnisse von Sprint II

- MVP ist in wesentlichen Teilen umgesetzt
- zentrale Kernlogik funktioniert
- erste Tests liegen vor
- System ist demonstrierbar

### Review-Kriterien

- Funktionieren die Kernabläufe stabil?
- Werden Konflikte zuverlässig erkannt?
- Entspricht die Umsetzung den Anforderungen?
- Ist die Lösung strukturell wartbar?

---

## Sprint III

### Ziel des Sprints

Sprint III fokussiert sich auf Stabilisierung, Qualitätssicherung, Refactoring und Abschluss der produktnahen Funktionen.  
Hier steht Software Engineering besonders stark im Vordergrund, da nicht nur Features ergänzt, sondern Qualität und Wartbarkeit gesichert werden.

### Schwerpunkte

- Refactoring
- Erweiterung von Tests
- Fehlerbehebung
- Verbesserung der Bedienbarkeit
- Vorbereitung der finalen Dokumentation und Präsentation

### Geplante Inhalte

#### Qualitätsverbesserung

- Code aufräumen und vereinheitlichen
- redundante Logik reduzieren
- Struktur und Lesbarkeit verbessern
- Namensgebung und Modulgrenzen überprüfen

#### Testing und Validierung

- weitere Unit-Tests ergänzen
- Integration zentraler Komponenten prüfen
- Randfälle testen
- Fehlerprotokoll führen und beheben

#### Funktionale Ergänzungen

- Administrationsfunktionen abrunden
- Buchungsübersichten verbessern
- kleinere UX-Verbesserungen umsetzen

#### Engineering-Reflexion

- Abgleich zwischen Planung und tatsächlicher Umsetzung
- Bewertung getroffener Architekturentscheidungen
- Analyse von Abweichungen, Risiken und Lessons Learned

### Geplante Ergebnisse von Sprint III

- stabile und präsentierbare Systemversion
- verbesserte Testabdeckung
- dokumentierte Qualitätsmaßnahmen
- nachvollziehbare Reflexion des Entwicklungsprozesses

### Review-Kriterien

- Ist das System stabil genug für Demonstration und Bewertung?
- Wurden zentrale Qualitätsziele erreicht?
- Sind Architektur und Code nachvollziehbar dokumentiert?
- Lassen sich Entscheidungen softwaretechnisch begründen?

---

## Finalisierung System & Dokumentation

### Ziel der Phase

In der Finalisierungsphase werden System, Dokumentation und Präsentationsmaterial vollständig abgeschlossen.  
Neben der letzten Qualitätssicherung steht vor allem die strukturierte Darstellung des Software-Engineering-Prozesses im Vordergrund.

### Inhalte

#### Technische Finalisierung

- letzte Fehlerbehebungen
- Abschluss offener Issues
- Endkontrolle des Systems
- finale Testdurchläufe

#### Dokumentation

- Überarbeitung des Anforderungskatalogs
- finale Beschreibung der Architektur
- Dokumentation der Use Cases
- Dokumentation von Testfällen und Ergebnissen
- Reflexion des Projektverlaufs
- Lessons Learned

#### Fokus auf Software Engineering

Die Dokumentation soll deutlich machen:

- wie Anforderungen systematisch erhoben wurden
- wie aus Anforderungen technische Arbeitspakete entstanden
- wie Architekturentscheidungen getroffen wurden
- wie Qualität gesichert wurde
- wie Planung und Umsetzung miteinander verzahnt waren

#### Präsentationsvorbereitung

- Erstellung einer klaren Projektvorstellung
- Visualisierung der Systemarchitektur
- Vorbereitung eines Demo-Ablaufs
- Verteilung der Vortragsanteile im Team

### Abschließende Artefakte

- fertiges System bzw. funktionsfähiger Prototyp
- Konzeptionsplan
- Anforderungskatalog
- Use Cases
- Architekturübersicht
- Testdokumentation
- Präsentationsunterlagen

---

## Resultate / Vorstellungen Fr 16.05.2025 * 09:00 – 12:15

### Ziel der Vorstellung

Die Vorstellung soll nicht nur das Endprodukt zeigen, sondern insbesondere den Entwicklungs- und Planungsprozess aus Sicht des Software Engineerings nachvollziehbar machen.

### Inhalte der Abschlussvorstellung

- Problemstellung und Motivation
- Ziel des Projekts
- Stakeholder und Anforderungen
- MVP und Priorisierung
- Architektur und Systementwurf
- wichtigste Kernfunktionen
- Teststrategie und Qualitätssicherung
- Reflexion des Projektverlaufs
- Lessons Learned

### Erwartete Resultate

- nachvollziehbar geplantes Projekt
- prototypisch umgesetzte Raum- und Ressourcenplanungs-App
- klar dokumentierter Software-Engineering-Prozess
- begründete Entscheidungen zu Architektur, Planung und Umsetzung
- erkennbare Verbindung zwischen Anforderungen, Design, Implementierung und Tests

### Abschließende Reflexion

Ein zentrales Ergebnis des Projekts soll sein, dass gezeigt wird, wie ein vergleichsweise kleines Softwaresystem mit Methoden des Software Engineerings strukturiert geplant, entwickelt und bewertet werden kann.  
Der fachliche Mehrwert liegt daher nicht allein in der App selbst, sondern vor allem in der nachvollziehbaren Anwendung von Software-Engineering-Prinzipien.

---

## Ergänzende Planungsgrundsätze

### Projektabgrenzung

Das Projekt wird bewusst in einem realistischen Rahmen gehalten.  
Komplexität wird nur dort aufgebaut, wo sie fachlich oder softwaretechnisch sinnvoll ist.

### MVP-orientiertes Vorgehen

Zunächst werden die Funktionen umgesetzt, die für die Kernidee des Systems unverzichtbar sind.  
Erweiterungen erfolgen nur dann, wenn der MVP stabil ist.

### Dokumentation als kontinuierlicher Prozess

Dokumentation wird nicht erst zum Schluss erstellt, sondern in allen Projektphasen fortlaufend gepflegt.

### Qualität vor Funktionsumfang

Da der Schwerpunkt auf Software Engineering liegt, ist eine kleinere, aber sauber geplante und gut dokumentierte Lösung wertvoller als ein überladener, instabiler Prototyp.

### Nachvollziehbarkeit von Entscheidungen

Wichtige Entscheidungen zu Anforderungen, Architektur, Priorisierung und Testing sollen stets begründet und dokumentiert werden.

---
