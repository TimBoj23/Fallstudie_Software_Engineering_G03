# Projektentstehung RePlan

## Ausgangslage

RePlan ist im Rahmen der Fallstudie Software Engineering als Buchungssystem für gemeinsam genutzte Arbeitsumgebungen entstanden. Ziel war es, eine Anwendung zu entwickeln, mit der Nutzer Seminarräume, Sitzplätze in Shared Offices und Assets wie Laptops, Beamer oder Präsentationstechnik buchen können.

Zu Beginn lag der Schwerpunkt auf einer funktionsfähigen Backend-Logik mit einfacher Datenhaltung. Im weiteren Verlauf wurde deutlich, dass die Anwendung neben der reinen Buchungsfunktion auch eine nachvollziehbare Nutzerverwaltung, realistische Demo-Daten und eine saubere Verbindung zwischen Frontend und Backend benötigt.

## Probleme

- Frontend und Backend wurden zeitweise unabhängig voneinander entwickelt. Dadurch entstanden unterschiedliche Strukturen und eine teilweise autarke Frontend-Logik.
- Die anfängliche JSON-Datenhaltung war für eine Demo nutzbar, wirkte aber nicht wie eine belastbare Datenbanklösung.
- Buchungen waren in der Oberfläche schwer nachvollziehbar, weil teilweise technische IDs statt sprechender Namen angezeigt wurden.
- Die Admin-Oberfläche zeigte anfangs zu wenig Kontext, zum Beispiel fehlten Nutzerfotos, Besitzerinformationen und einfache Filtermöglichkeiten.
- Demo-Nutzer und Demo-Daten wirkten teilweise künstlich oder doppelt vorhanden.
- Bildpflege über direkte Bild-URLs war für eine normale Benutzeroberfläche untypisch.

## Ideen und Lösungsansätze

- Das Backend bleibt die zentrale Quelle für Buchungslogik, Nutzerverwaltung und Datenhaltung.
- JSON-Daten wurden über eine Repository-Schicht in eine SQLite-basierte Speicherung überführt, damit die Demo realistischer wirkt.
- Räume, Sitzplätze und Assets wurden als getrennte buchbare Objekte modelliert.
- Sitzplätze können separat gebucht werden; bei Raumbuchungen kann weiterhin automatisch ein Sitzplatz zugewiesen werden.
- Buchungsübersichten zeigen sprechende Namen, Bilder und Nutzerinformationen statt technischer IDs.
- Die Admin-Oberfläche wurde um Nutzerverwaltung, Passwort-Reset, Rollenbearbeitung, Upload von Bildern und Filterfunktionen erweitert.
- Demo-Daten wurden bereinigt und realistischer aufgebaut: eindeutige Nutzer, neue Räume, neue Assets und passende Bilder.

## Aufgabenverteilung

| Person | Rolle und Verantwortlichkeit |
| --- | --- |
| Tim | Backend, Scrummaster, Qualitätsmanager |
| Alexander | Backend, Requirements Engineer |
| Florian | Frontend, Projektmanager, GitHub-Issues-Manager |
| Denis | Frontend |

## Ergebnis

Das Projekt entwickelte sich von einem einfachen MVP zu einer verbundenen Fullstack-Anwendung. Die Kernlogik liegt im Backend, während das Frontend die Buchungsvorgänge, Admin-Funktionen und Demo-Daten benutzerfreundlich darstellt. Für die Präsentation stehen realistischere Nutzer, Räume, Sitzplätze und Assets bereit.
