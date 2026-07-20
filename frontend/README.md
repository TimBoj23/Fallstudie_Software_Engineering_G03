# RePlan Frontend

React/Vite-Frontend für die Raum- und Ressourcenplanung.

## Voraussetzungen

- Node.js
- laufendes Flask-Backend unter `http://localhost:5000`

## Installation

```powershell
cd frontend
npm install
```

## Start

```powershell
npm run dev
```

Das Frontend läuft standardmässig unter:

```text
http://localhost:5173
```

## API-Konfiguration

Standard:

```text
http://localhost:5000/api
```

Optional kann die API-Basis per Umgebungsvariable gesetzt werden:

```text
VITE_API_BASE_URL=http://localhost:5000/api
```

## Design-System

Die zentralen Design-Werte liegen in:

```text
src/styles/theme.css
```

Dort werden Farben, Abstände, Radius, Schatten und Schriftgroessen als CSS Custom Properties definiert.
Alle weiteren Styles sollen diese Tokens verwenden, damit neue Elemente konsistent bleiben.
