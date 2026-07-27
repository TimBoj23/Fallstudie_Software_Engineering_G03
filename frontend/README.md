# RePlan Frontend

React/Vite-Frontend für die Raum- und Ressourcenplanung.

## Voraussetzungen

- Node.js
- laufendes Flask-Backend unter `http://localhost:5002`

## Erster Start

Das Backend wird im Projekt-Hauptordner in Terminal 1 vorbereitet und gestartet:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Das Frontend wird in Terminal 2 vorbereitet und gestartet:

```bash
cd frontend
npm install
npm run dev
```

## Spätere Starts

Nach dem Schließen beider Terminals genügt in Terminal 1:

```bash
source .venv/bin/activate
python app.py
```

In Terminal 2:

```bash
cd frontend
npm run dev
```

Wurde nur eines der beiden Terminals geschlossen, muss nur der entsprechende Prozess erneut gestartet werden. Ein erneutes `npm install` oder `pip install` ist normalerweise nicht nötig.

Das Frontend läuft standardmässig unter:

```text
http://localhost:5173
```

## API-Konfiguration

Standard:

```text
http://localhost:5002/api
```

Optional kann die API-Basis per Umgebungsvariable gesetzt werden:

```text
VITE_API_BASE_URL=http://localhost:5002/api
```

## Wichtige Bereiche

- Räume und Shared Offices einschließlich grafischem Sitzplan
- Assets und automatische Platzwahl
- Eigene Buchungen bearbeiten, verlängern und einzeln oder als Serie stornieren
- Einladungen ohne echten E-Mail-Versand über Code, Passwort und kopierbaren Link
- In-App-Benachrichtigungen
- Einstellungen für Profil, E-Mail, Passwort, Profilbild und Kontolöschung
- Adminbereich mit Nutzern, Buchungen, Protokoll, Statistik und geschütztem Demo-Reset

## Design-System

Die zentralen Design-Werte liegen in:

```text
src/styles/theme.css
```

Dort werden Farben, Abstände, Radius, Schatten und Schriftgroessen als CSS Custom Properties definiert.
Alle weiteren Styles sollen diese Tokens verwenden, damit neue Elemente konsistent bleiben.
