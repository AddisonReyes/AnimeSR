from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import AnimeDetail, GenreOption, HealthResponse, RecommendationResponse, SearchResponse
from app.services.catalog import AnimeCatalog


def _cors_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.catalog = AnimeCatalog()
    yield


app = FastAPI(
    title="Anime Recommendation API",
    version="1.0.0",
    lifespan=lifespan,
    summary="API de recomendaciones de anime basada en contenido y metadatos.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_catalog(request: Request) -> AnimeCatalog:
    return request.app.state.catalog


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": "Anime Recommendation API"}


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health(catalog: AnimeCatalog = Depends(get_catalog)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        total_anime=len(catalog.records),
        total_safe_anime=len(catalog.safe_records),
    )


@app.get("/api/genres", response_model=list[GenreOption], tags=["catalog"])
def featured_genres(
    limit: int = Query(default=18, ge=1, le=30),
    catalog: AnimeCatalog = Depends(get_catalog),
) -> list[GenreOption]:
    return catalog.get_featured_genres(limit=limit)


@app.get("/api/anime/search", response_model=SearchResponse, tags=["anime"])
def search_anime(
    q: str = Query(..., min_length=1, max_length=80),
    limit: int = Query(default=8, ge=1, le=20),
    catalog: AnimeCatalog = Depends(get_catalog),
) -> SearchResponse:
    return SearchResponse(query=q, results=catalog.search(q, limit=limit))


@app.get("/api/anime/{anime_id}", response_model=AnimeDetail, tags=["anime"])
def anime_detail(anime_id: int, catalog: AnimeCatalog = Depends(get_catalog)) -> AnimeDetail:
    try:
        return catalog.get_anime_detail(anime_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/recommendations/highlights", response_model=RecommendationResponse, tags=["recommendations"])
def recommendation_highlights(
    limit: int = Query(default=12, ge=1, le=24),
    catalog: AnimeCatalog = Depends(get_catalog),
) -> RecommendationResponse:
    return catalog.get_highlights(limit=limit)


@app.get("/api/recommendations/by-title", response_model=RecommendationResponse, tags=["recommendations"])
def recommendation_by_title(
    title: str = Query(..., min_length=1, max_length=120),
    limit: int = Query(default=12, ge=1, le=24),
    catalog: AnimeCatalog = Depends(get_catalog),
) -> RecommendationResponse:
    try:
        return catalog.recommend_by_title(title, limit=limit)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/recommendations/by-genre", response_model=RecommendationResponse, tags=["recommendations"])
def recommendation_by_genre(
    genre: str = Query(..., min_length=1, max_length=80),
    limit: int = Query(default=12, ge=1, le=24),
    catalog: AnimeCatalog = Depends(get_catalog),
) -> RecommendationResponse:
    try:
        return catalog.recommend_by_genre(genre, limit=limit)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
