# Backend

API en `FastAPI` para servir recomendaciones en tiempo real usando el dataset nuevo como base principal.

## Idea del recomendador

- Usa `backend/anime-dataset-2023.csv` como fuente principal.
- Enriquece metadatos con `deprecated/anime.csv` para recuperar tags como `Shounen`, `Shoujo` o `Seinen`.
- Responde a dos entradas principales:
  - nombre de anime
  - genero / etiqueta

## Endpoints

- `GET /api/health`
- `GET /api/genres`
- `GET /api/anime/search?q=naruto`
- `GET /api/anime/{anime_id}`
- `GET /api/recommendations/highlights`
- `GET /api/recommendations/by-title?title=Naruto`
- `GET /api/recommendations/by-genre?genre=Shounen`

## Ejecutar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir .
```
