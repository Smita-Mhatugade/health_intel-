# HealthIntel — AI Medical Analysis Frontend

Modern React frontend for the HealthIntel FastAPI backend. Provides chat-based input, dynamic forms, hospital search with map, history, and PDF export.

## Setup

```bash
# 1. Install dependencies
bun install     # or: npm install

# 2. Configure backend URL
cp .env.example .env
# edit VITE_API_URL if your backend runs elsewhere

# 3. Start the dev server
bun dev         # or: npm run dev
```

## Backend

Start the FastAPI backend (separate repo) on `http://localhost:8000`:

```bash
uvicorn main:app --reload --port 8000
```

The frontend reads the URL from `VITE_API_URL` (or `REACT_APP_API_URL`). You can also override it at runtime via the in-app **Settings** dialog.

## Routes

| Path         | Page      | Description                                  |
|--------------|-----------|----------------------------------------------|
| `/`          | Home      | Hero + disease module cards                  |
| `/analyze`   | Analyze   | Chat parser + dynamic forms + preview        |
| `/hospitals` | Hospitals | Map + geolocation/address/manual + radius    |
| `/history`   | History   | Saved analyses + export to PDF               |
| `/about`     | About     | Project info, tech stack, disclaimers        |

## Tech stack

- React 18 + Vite + TypeScript
- Tailwind CSS + shadcn/ui (Teal/Slate medical theme, dark mode)
- TanStack Query for data fetching, Zustand for global state
- React Router v6
- Leaflet + OpenStreetMap (with Nominatim geocoding)
- jsPDF + jspdf-autotable for PDF export

## Disclaimer

HealthIntel is for **informational purposes only** and is **not** a substitute for professional medical advice, diagnosis, or treatment.
