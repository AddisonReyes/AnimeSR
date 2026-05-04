# Anime System Recommendations

Aplicacion full stack para descubrir recomendaciones de anime usando similitud por contenido. El proyecto conserva el notebook original para referencia historica y expone una experiencia web dividida en `FastAPI` para la API y `Next.js` para la interfaz.

## Resumen rapido

- `backend/`: API REST con el motor de recomendacion.
- `frontend/`: interfaz web para buscar animes, explorar generos y abrir detalles.
- `deprecated/`: notebook y datasets del proyecto original. Aunque esta carpeta sea legacy, el backend sigue usando `deprecated/anime.csv` para enriquecer etiquetas, asi que no debe eliminarse sin ajustar el codigo.
- `docker-compose.yml`: arranque de la pila completa con Docker.

## Como funciona

1. El backend carga `backend/anime-dataset-2023.csv` como dataset principal.
2. Enriquece tags con `deprecated/anime.csv` para recuperar etiquetas historicas como `Shounen`, `Shoujo` o `Seinen`.
3. Filtra contenido adulto usando etiquetas y rating.
4. Genera un indice TF-IDF a partir de titulo, sinopsis, estudio, fuente y tags.
5. Expone endpoints para destacados, busqueda por titulo, detalle y recomendaciones por anime o genero.
6. El frontend consume la API desde el navegador y presenta la experiencia con tarjetas, sugerencias y modal de detalle.

## Estructura del repositorio

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
│   │       └── catalog.py
│   └── requirements.txt
├── deprecated
│   ├── anime.csv
│   └── main.ipynb
├── docker-compose.yml
└── frontend
    ├── .dockerignore
    ├── Dockerfile
    ├── README.md
    ├── .env.example
    ├── app
    ├── components
    ├── lib
    └── package.json
```

## Requisitos locales

- Python 3.10 o superior
- Node.js 20 o superior recomendado
- npm

## Variables de entorno

Frontend:

- `NEXT_PUBLIC_API_BASE_URL`
  - URL base de la API consumida desde el navegador.
  - Valor por defecto: `http://127.0.0.1:8000`
  - Importante: al ser una variable publica de Next.js, debe apuntar a una URL accesible desde el navegador del usuario, no a un hostname interno como `backend`.
  - Archivo de ejemplo: `frontend/.env.example`

## Ejecutar en local

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

Aplicacion:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Healthcheck: `http://localhost:8000/api/health`

## Ejecutar con Docker

El repositorio incluye `Dockerfile` para backend y frontend, y un `docker-compose.yml` para levantar toda la pila.

```bash
docker-compose up --build
```

Servicios expuestos:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

Variables configurables desde Compose:

- `NEXT_PUBLIC_API_BASE_URL`
  - Por defecto apunta a `http://localhost:8000`
  - Si la API va a vivir en otra URL, hay que actualizar el valor en Compose y reconstruir la imagen del frontend.

Para detener la pila:

```bash
docker-compose down
```

Notas sobre archivos `.env`:

- No hay archivos `.env` ni `.env.example` en la raiz del repo.
- Frontend: `Next.js` lee `frontend/.env` automaticamente en desarrollo.

## Endpoints principales

- `GET /`
- `GET /api/health`
- `GET /api/genres?limit=18`
- `GET /api/anime/search?q=naruto&limit=8`
- `GET /api/anime/{anime_id}`
- `GET /api/recommendations/highlights?limit=12`
- `GET /api/recommendations/by-title?title=Naruto&limit=12`
- `GET /api/recommendations/by-genre?genre=Shounen&limit=12`

Los detalles del contrato de la API y del frontend estan en [backend/README.md](/home/dakotitah/github/Anime-System-Recomendations/backend/README.md) y [frontend/README.md](/home/dakotitah/github/Anime-System-Recomendations/frontend/README.md).
