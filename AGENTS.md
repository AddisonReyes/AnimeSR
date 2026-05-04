# AGENTS

## Objetivo del repositorio

Proyecto full stack para recomendaciones de anime basado en contenido. El backend expone una API en `FastAPI` y el frontend la consume desde `Next.js`.

## Mapa rapido

- `README.md`: vision general y arranque local o con Docker.
- `backend/`: API, modelos Pydantic y logica de recomendacion.
- `frontend/`: interfaz, componentes y capa de acceso a la API.
- `deprecated/`: material historico. `deprecated/anime.csv` sigue siendo dependencia activa del backend.

## Comandos utiles

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

Validacion rapida:

```bash
python3 -m py_compile backend/app/main.py backend/app/schemas.py backend/app/services/catalog.py
cd frontend && npm run lint
```

## Notas importantes del backend

- `backend/app/services/catalog.py` resuelve rutas a partir de la raiz del repo.
- El backend necesita:
  - `backend/anime-dataset-2023.csv`
  - `deprecated/anime.csv`
- No elimines ni muevas `deprecated/anime.csv` sin ajustar esas rutas.
- La API excluye contenido adulto usando tags y ratings.
- Las recomendaciones por titulo y genero tienen cache en memoria.
- El CORS esta abierto para cualquier origen.

## Notas importantes del frontend

- `frontend/components/anime-explorer.tsx` es un componente cliente.
- Para desarrollo local, las variables de entorno viven en `frontend/.env`.
- `NEXT_PUBLIC_API_BASE_URL` debe ser accesible desde el navegador, no solo desde la red interna de Docker.
- Si se cambia `NEXT_PUBLIC_API_BASE_URL` en una imagen ya construida del frontend, hay que reconstruirla porque es una variable publica de Next.js.
- `frontend/next.config.mjs` usa `output: "standalone"` para la imagen Docker.

## Reglas para cambios futuros

- Si cambias endpoints, variables de entorno o comandos de arranque, actualiza:
  - `README.md`
  - `backend/README.md`
  - `frontend/README.md`
- Si cambias la estructura de carpetas, revisa tambien:
  - `backend/app/services/catalog.py`
  - `docker-compose.yml`
  - `backend/Dockerfile`
- No mezcles artefactos locales en commits:
  - `.venv/`
  - `.next/`
  - `node_modules/`
  - `frontend/.env`

## Estado actual

- No hay suite automatizada de tests en el repo.
- La validacion minima recomendada es compilacion Python, `npm run lint` y una prueba manual del flujo de busqueda y recomendaciones.
