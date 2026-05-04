# Anime System Recommendations

Este proyecto ahora queda dividido en tres partes:

- `deprecated/`
  - El proyecto original en notebook. Se mantiene intacto.
- `backend/`
  - API en FastAPI con un recomendador pensado para consultas por anime y por genero.
- `frontend/`
  - Interfaz web en Next.js para explorar recomendaciones de forma visual e interactiva.

## Cambio de enfoque

El notebook original recomendaba en funcion de `user_id`, lo cual era util para experimentacion local pero no encajaba bien con una web abierta al publico. La nueva version cambia a un enfoque basado en contenido:

- busqueda por nombre de anime
- recomendaciones similares segun texto, tags y metadatos
- exploracion por etiquetas como `Action`, `Fantasy`, `Shounen`, `Seinen`, etc.

## Estructura

```text
backend/
  app/
    main.py
    schemas.py
    services/catalog.py
deprecated/
  main.ipynb
frontend/
  app/
  components/
  lib/
```

## Levantar el proyecto

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir .
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```
