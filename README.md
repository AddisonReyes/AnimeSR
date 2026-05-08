# Anime System Recommendations

Anime System Recommendations is a full-stack anime discovery app built around content-based recommendations. The repository keeps the original notebook-based work for historical reference, while the current product is split into a `FastAPI` backend and a `Next.js` frontend.

## Overview

- `backend/`: REST API and recommendation engine.
- `frontend/`: web interface for search, browsing, and detail views.
- `deprecated/`: original notebook and legacy datasets. Even though this folder is legacy, the backend still uses `deprecated/anime.csv` to enrich tags, so it must not be removed without updating the code.
- `docker-compose.yml`: local orchestration for the full stack.

## How It Works

1. The backend loads `backend/anime-dataset-2023.csv` as the primary dataset.
2. It enriches the catalog with tag data from `deprecated/anime.csv`.
3. Adult titles are filtered out before public responses are returned.
4. The backend lazily builds a TF-IDF feature matrix for title-based recommendations from title, synopsis, tags, studios, and source material.
5. The API exposes search, detail, genre browsing, highlights, and recommendation endpoints.
6. The frontend consumes the API in the browser and renders the experience with search suggestions, cards, a detail modal, and a styled footer.

## Repository Structure

```text
.
├── AGENTS.md
├── README.md
├── backend
│   ├── Dockerfile
│   ├── README.md
│   ├── anime-dataset-2023.csv
│   ├── app
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── services
│   │       ├── catalog.py
│   │       └── catalog_support.py
│   ├── requirements.txt
│   └── start.sh
├── deprecated
│   ├── anime.csv
│   └── main.ipynb
├── docker-compose.yml
└── frontend
    ├── .dockerignore
    ├── .env.example
    ├── Dockerfile
    ├── README.md
    ├── app
    ├── components
    ├── hooks
    ├── lib
    └── package.json
```

## Local Requirements

- Python 3.10+
- Node.js 20+ recommended
- npm

## Environment Variables

Frontend:

- `NEXT_PUBLIC_API_BASE_URL`
  - Base URL used by the browser to reach the backend API.
  - Default: `http://127.0.0.1:8000`
  - Because this is a public Next.js variable, it must point to a URL reachable from the browser. Do not point it to an internal hostname such as `backend`.
  - Example file: `frontend/.env.example`

Backend:

- `ANIMESR_PRELOAD_TFIDF`
  - Optional.
  - Default: `0`
  - Set to `1` to build the title recommendation engine during startup instead of waiting for the first title-based recommendation request.
- `ANIMESR_TFIDF_IDLE_TTL_SECONDS`
  - Optional.
  - Default: `900`
  - Number of idle seconds before the backend releases the in-memory title recommendation engine.
  - Set to `0` to keep the engine loaded once it has been built.

## Run Locally

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir .
```

Frontend:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

App URLs:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Health check: `http://localhost:8000/api/health`
- Swagger UI: `http://localhost:8000/docs`

## Run with Docker

The repository includes a Docker setup for both services and a root `docker-compose.yml` file for the full stack.

```bash
docker-compose up --build
```

Exposed services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

Configurable Compose variable:

- `NEXT_PUBLIC_API_BASE_URL`
  - Default: `http://localhost:8000`
  - If the API lives at another URL, update the variable and rebuild the frontend image.

Stop the stack:

```bash
docker-compose down
```

Notes about `.env` files:

- There are no root-level `.env` or `.env.example` files in this repository.
- The frontend reads `frontend/.env` automatically in local development.

## Testing And CI

Backend tests:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
```

Frontend checks:

```bash
cd frontend
npm clean-install --progress=false
npm run lint
npm run build
```

GitHub Actions:

- The repository now includes [.github/workflows/ci.yml](/home/dakotitah/github/Anime-System-Recomendations/.github/workflows/ci.yml).
- Every push and pull request runs:
  - backend module compilation plus backend tests on Python 3.11
  - frontend dependency install, lint, and production build on Node 22

## Main API Endpoints

- `GET /`
- `GET /docs`
- `GET /redoc`
- `GET /api/health`
- `GET /api/genres?limit=18`
- `GET /api/anime/search?q=naruto&limit=8`
- `GET /api/anime/{anime_id}`
- `GET /api/recommendations/highlights?limit=12`
- `GET /api/recommendations/by-title?title=Naruto&limit=12`
- `GET /api/recommendations/by-genre?genre=Shounen&limit=12`

More detailed backend and frontend documentation lives in [backend/README.md](/home/dakotitah/github/Anime-System-Recomendations/backend/README.md) and [frontend/README.md](/home/dakotitah/github/Anime-System-Recomendations/frontend/README.md).

## Runtime Cost Notes

- Search, detail, featured genres, and highlights are available without preloading the title recommendation matrix.
- The first `GET /api/recommendations/by-title` request after a cold start can be slower because the TF-IDF engine is built on demand.
- After a period of inactivity, the backend can release that engine again to reduce steady-state Railway memory usage.
