# AGENTS

## Repository Goal

This is a full-stack anime recommendation project built around a content-based recommendation engine. The backend exposes a public API through `FastAPI`, and the frontend consumes it through `Next.js`.

## Quick Map

- `README.md`: high-level project overview and local/Docker setup.
- `backend/`: API, schemas, OpenAPI docs, and recommendation engine logic.
- `frontend/`: UI, hooks, components, and API client helpers.
- `deprecated/`: historical material. `deprecated/anime.csv` is still an active backend dependency.

## Useful Commands

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

Docker:

```bash
docker-compose up --build
docker-compose down
```

Quick validation:

```bash
python3 -m py_compile backend/app/main.py backend/app/schemas.py backend/app/services/catalog.py backend/app/services/catalog_support.py
cd frontend && npm run lint
```

## Important Backend Notes

- `backend/app/services/catalog.py` resolves dataset paths from the repository root.
- `backend/app/services/catalog_support.py` owns parsing, normalization, and record mapping.
- The backend needs both:
  - `backend/anime-dataset-2023.csv`
  - `deprecated/anime.csv`
- Do not remove or move `deprecated/anime.csv` without updating the backend path logic.
- Public responses exclude adult content based on tags and rating labels.
- Title-based and genre-based recommendations are cached in memory.
- CORS is intentionally open for public API consumption.
- Railway/Docker production startup lives in [backend/start.sh](/home/dakotitah/github/Anime-System-Recomendations/backend/start.sh).

## Important Frontend Notes

- `frontend/components/anime-explorer.tsx` is the main client-side container.
- `frontend/hooks/use-anime-explorer.ts` owns the main page interaction logic.
- `NEXT_PUBLIC_API_BASE_URL` must be reachable from the browser, not just from internal Docker or private service networking.
- If `NEXT_PUBLIC_API_BASE_URL` changes for a built frontend image, the image should be rebuilt.
- `frontend/next.config.mjs` uses `output: "standalone"` for container-friendly builds.
- Local frontend environment variables live in `frontend/.env`.

## Rules for Future Changes

- If you change routes, environment variables, startup commands, or deployment behavior, update:
  - `README.md`
  - `backend/README.md`
  - `frontend/README.md`
- If you change folder structure, double-check:
  - `backend/app/services/catalog.py`
  - `backend/start.sh`
  - `backend/Dockerfile`
  - `docker-compose.yml`
- Do not commit local artifacts such as:
  - `.venv/`
  - `.next/`
  - `node_modules/`
  - `frontend/.env`

## Current State

- There is no automated test suite yet.
- The minimum recommended validation flow is Python compilation, frontend linting, frontend production build, and a manual check of search, recommendations, and the detail modal.
