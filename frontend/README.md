# Frontend

The frontend is a `Next.js 14 + TypeScript` application that consumes the backend API and presents anime recommendations in an interactive UI.

## Features

- Incremental title search
- Autocomplete suggestions
- Related recommendations based on the strongest search result
- Genre and editorial tag browsing
- Summary cards with score, episode count, and short synopsis
- Detail modal with deeper metadata
- Footer links to API docs and source code

## Structure

- [frontend/components/anime-explorer.tsx](/home/dakotitah/github/Anime-System-Recomendations/frontend/components/anime-explorer.tsx)
  - Main page container that wires the UI together.
- [frontend/hooks/use-anime-explorer.ts](/home/dakotitah/github/Anime-System-Recomendations/frontend/hooks/use-anime-explorer.ts)
  - Primary client-side state and interaction logic.
- [frontend/components/anime-search-panel.tsx](/home/dakotitah/github/Anime-System-Recomendations/frontend/components/anime-search-panel.tsx)
  - Search box, autocomplete suggestions, genre pills, and featured titles.
- [frontend/components/anime-results-section.tsx](/home/dakotitah/github/Anime-System-Recomendations/frontend/components/anime-results-section.tsx)
  - Results header, notices, cards, and empty state.
- [frontend/components/anime-footer.tsx](/home/dakotitah/github/Anime-System-Recomendations/frontend/components/anime-footer.tsx)
  - Footer content and external links.
- [frontend/lib/api.ts](/home/dakotitah/github/Anime-System-Recomendations/frontend/lib/api.ts)
  - Centralized API access and query-string helpers.

## Environment Variable

- `NEXT_PUBLIC_API_BASE_URL`
  - Default: `http://127.0.0.1:8000`
  - Correct local development example: `http://localhost:8000`
  - Incorrect browser-facing example: `http://backend:8000`
  - Example file: `frontend/.env.example`

Because this variable is public and evaluated for browser-side requests, it must point to a URL reachable from the user's browser, not just from Docker networking.

## Backend Runtime Note

- The backend can lazily initialize title-based recommendations to reduce Railway memory usage.
- Because of that, the first title recommendation request after a cold backend start can take a bit longer than later requests.
- If you prefer startup latency over lower idle RAM, the backend supports `ANIMESR_PRELOAD_TFIDF=1`.

## Run Locally

```bash
cp .env.example .env
npm install
npm run dev
```

Application URL:

- `http://localhost:3000`

## Run with Docker

From the repository root:

```bash
docker-compose up --build frontend
```

The frontend image uses Next.js `standalone` output to simplify production container deployment.
