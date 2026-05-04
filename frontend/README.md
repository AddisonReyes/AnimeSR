# Frontend

Aplicacion en `Next.js 14 + TypeScript` para consumir la API del backend y presentar recomendaciones de anime en una UI interactiva.

## Funcionalidades

- Busqueda incremental por titulo.
- Sugerencias para autocompletar.
- Recomendaciones similares al primer resultado relevante.
- Exploracion por genero o tag.
- Tarjetas con score, episodios y sinopsis breve.
- Modal con detalle ampliado del anime.

## Puntos tecnicos

- La vista principal vive en [frontend/components/anime-explorer.tsx](/home/dakotitah/github/Anime-System-Recomendations/frontend/components/anime-explorer.tsx).
- Todas las llamadas a la API salen desde [frontend/lib/api.ts](/home/dakotitah/github/Anime-System-Recomendations/frontend/lib/api.ts).
- El consumo de datos ocurre del lado del cliente, asi que `NEXT_PUBLIC_API_BASE_URL` debe apuntar a una URL alcanzable desde el navegador.

## Variable de entorno

- `NEXT_PUBLIC_API_BASE_URL`
  - Valor por defecto: `http://127.0.0.1:8000`
  - Ejemplo para desarrollo local: `http://localhost:8000`
  - Ejemplo incorrecto para navegador: `http://backend:8000`
  - Archivo de ejemplo: `frontend/.env.example`

## Ejecutar en local

```bash
cp .env.example .env
npm install
npm run dev
```

Aplicacion:

- `http://localhost:3000`

## Ejecutar con Docker

Desde la raiz del repositorio:

```bash
docker-compose up --build frontend
```

La imagen del frontend usa `Next.js` en modo `standalone` para simplificar el despliegue.
