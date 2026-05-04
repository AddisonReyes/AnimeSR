# Backend

API REST en `FastAPI` para cargar el catalogo de anime, filtrar contenido no deseado y servir recomendaciones en tiempo real.

## Stack

- `FastAPI`
- `Pydantic`
- `scikit-learn`
- `uvicorn`

## Fuentes de datos

- `backend/anime-dataset-2023.csv`
  - Dataset principal con metadatos, score, sinopsis, estudio y assets.
- `deprecated/anime.csv`
  - Dataset legacy usado para recuperar tags adicionales.

El servicio depende de ambos archivos. Si cambia su ubicacion, tambien hay que ajustar la resolucion de rutas en [backend/app/services/catalog.py](/home/dakotitah/github/Anime-System-Recomendations/backend/app/services/catalog.py).

## Flujo del catalogo

1. `AnimeCatalog` se inicializa una sola vez durante el `lifespan` de FastAPI.
2. Se limpian campos, se normalizan listas y se detecta contenido adulto.
3. Se construyen:
   - un lookup por titulo
   - un lookup por genero
   - una matriz TF-IDF para similitud
4. Se cachean recomendaciones por anime y por genero para evitar recalculo innecesario.

## Variables de entorno

- No hay variables obligatorias para levantar la API en su estado actual.
- El CORS esta abierto para cualquier origen para que la API sea consumible desde cualquier frontend.

## Endpoints

- `GET /`
  - Respuesta basica para comprobar que la API esta arriba.
- `GET /docs`
  - Swagger UI interactivo generado desde OpenAPI.
- `GET /redoc`
  - Documentacion alternativa en formato ReDoc.
- `GET /api/health`
  - Devuelve `status`, `total_anime` y `total_safe_anime`.
- `GET /api/genres?limit=18`
  - Lista de generos destacados.
- `GET /api/anime/search?q=naruto&limit=8`
  - Busqueda por nombre con coincidencias aproximadas.
- `GET /api/anime/{anime_id}`
  - Detalle completo de un anime seguro para mostrar en la UI.
- `GET /api/recommendations/highlights?limit=12`
  - Destacados generales del catalogo.
- `GET /api/recommendations/by-title?title=Naruto&limit=12`
  - Recomendaciones similares a un titulo.
- `GET /api/recommendations/by-genre?genre=Shounen&limit=12`
  - Recomendaciones por genero o etiqueta.

## Ejecutar en local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir .
```

Healthcheck:

```bash
curl http://127.0.0.1:8000/api/health
```

## Ejecutar con Docker

Desde la raiz del repositorio:

```bash
docker-compose up --build backend
```

La imagen del backend se construye desde la raiz del repo porque necesita copiar tanto `backend/` como `deprecated/`.
