# Backend

The backend is a `FastAPI` service that loads the anime catalog, filters unsafe content, and serves search and recommendation responses in real time.

## Stack

- `FastAPI`
- `Pydantic`
- `scikit-learn`
- `uvicorn`

## Data Sources

- `backend/anime-dataset-2023.csv`
  - Primary dataset with titles, scores, synopses, studios, and image assets.
- `deprecated/anime.csv`
  - Legacy dataset still used to recover additional editorial tags.

The service depends on both files. If their locations change, update the path resolution logic in [backend/app/services/catalog.py](/home/dakotitah/github/Anime-System-Recomendations/backend/app/services/catalog.py).

## Catalog Flow

1. `AnimeCatalog` is initialized once during the FastAPI lifespan.
2. Raw data is cleaned, normalized, and filtered for adult content.
3. The service builds:
   - a title lookup
   - a genre lookup
   - a TF-IDF matrix for content similarity
4. Recommendation results are cached by title anchor and by genre for better performance.

## Internal Structure

- [backend/app/main.py](/home/dakotitah/github/Anime-System-Recomendations/backend/app/main.py)
  - FastAPI app setup, routing, OpenAPI metadata, and HTTP error handling.
- [backend/app/schemas.py](/home/dakotitah/github/Anime-System-Recomendations/backend/app/schemas.py)
  - Pydantic response models and OpenAPI examples.
- [backend/app/services/catalog.py](/home/dakotitah/github/Anime-System-Recomendations/backend/app/services/catalog.py)
  - Search, ranking, recommendation, caching, and catalog indexing logic.
- [backend/app/services/catalog_support.py](/home/dakotitah/github/Anime-System-Recomendations/backend/app/services/catalog_support.py)
  - Parsing, normalization, and record-to-schema conversion helpers.

## Environment

- No required runtime environment variables are needed for the API in its current form.
- CORS is intentionally open so the API can be consumed publicly from any frontend.

## Endpoints

- `GET /`
  - Simple entrypoint response to confirm the API is online.
- `GET /docs`
  - Interactive Swagger UI generated from the OpenAPI schema.
- `GET /redoc`
  - Alternative API reference view powered by ReDoc.
- `GET /api/health`
  - Returns `status`, `total_anime`, and `total_safe_anime`.
- `GET /api/genres?limit=18`
  - Returns featured genres for browsing.
- `GET /api/anime/search?q=naruto&limit=8`
  - Performs exact, partial, and fuzzy title matching.
- `GET /api/anime/{anime_id}`
  - Returns the full safe-public detail payload for one anime.
- `GET /api/recommendations/highlights?limit=12`
  - Returns curated highlight recommendations from the catalog.
- `GET /api/recommendations/by-title?title=Naruto&limit=12`
  - Returns content-based recommendations anchored to a title.
- `GET /api/recommendations/by-genre?genre=Shounen&limit=12`
  - Returns recommendations from a genre or editorial tag.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir .
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

## Run Tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
```

The backend test suite currently validates the main public API contract and recommendation flows:

- root and health endpoints
- featured genres
- title search
- anime detail lookup
- title-based recommendations
- genre-based recommendations
- representative 404 cases

## Run with Docker

From the repository root:

```bash
docker-compose up --build backend
```

The backend image is built from the repository root because it needs access to both `backend/` and `deprecated/`.

## Railway

The backend `Dockerfile` is now production-ready for Railway:

- It reads `PORT` automatically with a fallback to `8000`.
- It starts through [backend/start.sh](/home/dakotitah/github/Anime-System-Recomendations/backend/start.sh), which uses `exec uvicorn ...` for cleaner signal handling.
- It runs as a non-root user inside the container.

Important for this monorepo:

- The Docker build context must include the repository root, because the image copies:
  - `backend/`
  - `deprecated/`
- If Railway is building from the full repository, set `RAILWAY_DOCKERFILE_PATH=backend/Dockerfile`.
- If you try to build from the `backend/` folder alone, the build will fail because `deprecated/anime.csv` will be outside the Docker build context.
