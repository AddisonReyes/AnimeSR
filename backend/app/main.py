from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    AnimeDetail,
    ErrorResponse,
    GenreOption,
    HealthResponse,
    RecommendationResponse,
    RootResponse,
    SearchResponse,
)
from app.services.catalog import AnimeCatalog

API_DESCRIPTION = """
Public read-only API for the AnimeSR catalog and recommendation engine.

### What you can do here

- Search anime titles with fuzzy matching.
- Browse high-signal featured genres.
- Retrieve full anime detail payloads for UI modals or catalog pages.
- Generate content-based recommendations from a title or a genre.
- Inspect curated highlights from the safe public catalog.

### Recommendation model

Recommendations are generated from normalized title metadata, synopsis text, studios, source material,
genres, and legacy editorial tags. Adult content is filtered before public responses are returned.

### Notes for integrators

- No authentication is required.
- CORS is open for public consumption.
""".strip()

OPENAPI_TAGS = [
    {
        "name": "root",
        "description": "Entry and discovery endpoints for checking that the API is online.",
    },
    {
        "name": "system",
        "description": "Operational endpoints such as health checks and catalog counters.",
    },
    {
        "name": "catalog",
        "description": "Genre browsing endpoints that expose public catalog navigation options.",
    },
    {
        "name": "anime",
        "description": "Anime search and detail endpoints for retrieving public-safe catalog items.",
    },
    {
        "name": "recommendations",
        "description": "Recommendation endpoints powered by the content-based ranking engine.",
    },
]

NOT_FOUND_RESPONSE = {
    "model": ErrorResponse,
    "description": "The requested anime, title, or genre could not be resolved from the public-safe catalog.",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.catalog = AnimeCatalog()
    yield


app = FastAPI(
    title="Anime Recommendation API",
    version="1.0.0",
    lifespan=lifespan,
    summary="Content-based anime recommendation API.",
    description=API_DESCRIPTION,
    contact={
        "name": "AnimeSR repository",
        "url": "https://github.com/AddisonReyes/Anime-System-Recomendations",
    },
    openapi_tags=OPENAPI_TAGS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_catalog(request: Request) -> AnimeCatalog:
    return request.app.state.catalog


@app.get(
    "/",
    response_model=RootResponse,
    tags=["root"],
    summary="Describe the API entrypoint",
    description="Lightweight discovery endpoint for verifying that the service is online.",
    response_description="Human-readable identifier for the API service.",
)
def root() -> RootResponse:
    return RootResponse(message="Anime Recommendation API")


@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["system"],
    summary="Check API health and catalog size",
    description=(
        "Returns a lightweight heartbeat plus counters for the full dataset loaded in memory and the "
        "safe subset exposed publicly."
    ),
    response_description="API health status and dataset counters.",
)
def health(catalog: AnimeCatalog = Depends(get_catalog)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        total_anime=len(catalog.records),
        total_safe_anime=len(catalog.safe_records),
    )


@app.get(
    "/api/genres",
    response_model=list[GenreOption],
    tags=["catalog"],
    summary="List featured genres",
    description=(
        "Returns a ranked subset of genres and editorial tags that are suitable for public browsing. "
        "These entries are derived from the safe catalog only."
    ),
    response_description="Ordered list of featured genres with display labels and catalog counts.",
    responses={
        200: {
            "description": "Ordered list of featured genres available for browsing.",
            "content": {
                "application/json": {
                    "example": [
                        {"name": "Action", "display_name": "Action", "count": 1450},
                        {"name": "Shounen", "display_name": "Shonen", "count": 428},
                    ]
                }
            },
        }
    },
)
def featured_genres(
    limit: int = Query(
        default=18,
        ge=1,
        le=30,
        description="Maximum number of featured genres to return.",
        openapi_examples={
            "default": {"summary": "Default sized genre strip", "value": 18},
            "compact": {"summary": "Compact response for smaller UIs", "value": 8},
        },
    ),
    catalog: AnimeCatalog = Depends(get_catalog),
) -> list[GenreOption]:
    return catalog.get_featured_genres(limit=limit)


@app.get(
    "/api/anime/search",
    response_model=SearchResponse,
    tags=["anime"],
    summary="Search anime by title",
    description=(
        "Performs exact, prefix, substring, and fuzzy title matching against the public-safe catalog. "
        "Results are ranked so the most likely title matches appear first."
    ),
    response_description="Original query plus the ordered list of matching anime titles.",
)
def search_anime(
    q: str = Query(
        ...,
        min_length=1,
        max_length=80,
        description="Anime title or partial title to search for.",
        openapi_examples={
            "popular": {"summary": "Popular shounen title", "value": "Naruto"},
            "partial": {"summary": "Partial franchise title", "value": "fullmetal"},
        },
    ),
    limit: int = Query(
        default=8,
        ge=1,
        le=20,
        description="Maximum number of search matches to return.",
        openapi_examples={
            "default": {"summary": "Default search response size", "value": 8},
            "large": {"summary": "Broader search result set", "value": 15},
        },
    ),
    catalog: AnimeCatalog = Depends(get_catalog),
) -> SearchResponse:
    return SearchResponse(query=q, results=catalog.search(q, limit=limit))


@app.get(
    "/api/anime/{anime_id}",
    response_model=AnimeDetail,
    tags=["anime"],
    summary="Get full anime details",
    description=(
        "Returns the full detail payload for a single public-safe anime record, including synopsis, studios, "
        "source material, and popularity metadata."
    ),
    response_description="Full detail payload for the requested anime.",
    responses={
        404: {
            **NOT_FOUND_RESPONSE,
            "content": {
                "application/json": {
                    "example": {"detail": "No safe anime found with id 999999."}
                }
            },
        }
    },
)
def anime_detail(
    anime_id: int, catalog: AnimeCatalog = Depends(get_catalog)
) -> AnimeDetail:
    try:
        return catalog.get_anime_detail(anime_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get(
    "/api/recommendations/highlights",
    response_model=RecommendationResponse,
    tags=["recommendations"],
    summary="Get editorial-style highlights",
    description=(
        "Returns a curated list of high-signal titles from the safe public catalog. "
        "This is a good default entrypoint when the client does not yet have a title or genre anchor."
    ),
    response_description="Highlight recommendations from across the catalog.",
)
def recommendation_highlights(
    limit: int = Query(
        default=12,
        ge=1,
        le=24,
        description="Maximum number of highlight recommendations to return.",
        openapi_examples={
            "default": {"summary": "Default homepage carousel size", "value": 12},
            "compact": {"summary": "Smaller featured set", "value": 6},
        },
    ),
    catalog: AnimeCatalog = Depends(get_catalog),
) -> RecommendationResponse:
    return catalog.get_highlights(limit=limit)


@app.get(
    "/api/recommendations/by-title",
    response_model=RecommendationResponse,
    tags=["recommendations"],
    summary="Recommend anime from a title anchor",
    description=(
        "Finds the closest public-safe title match for the provided query and returns content-based "
        "recommendations derived from that anchor item."
    ),
    response_description="Anchor anime plus a ranked list of related recommendations.",
    responses={
        404: {
            **NOT_FOUND_RESPONSE,
            "content": {
                "application/json": {
                    "example": {"detail": 'No anime matched "Naruto X".'}
                }
            },
        }
    },
)
def recommendation_by_title(
    title: str = Query(
        ...,
        min_length=1,
        max_length=120,
        description="Anime title used as the recommendation anchor.",
        openapi_examples={
            "popular": {"summary": "Popular anchor title", "value": "Naruto"},
            "prestige": {
                "summary": "Prestige anchor title",
                "value": "Fullmetal Alchemist: Brotherhood",
            },
        },
    ),
    limit: int = Query(
        default=12,
        ge=1,
        le=24,
        description="Maximum number of recommendations to return.",
        openapi_examples={
            "default": {"summary": "Default recommendation size", "value": 12},
            "short": {"summary": "Smaller recommendation strip", "value": 5},
        },
    ),
    catalog: AnimeCatalog = Depends(get_catalog),
) -> RecommendationResponse:
    try:
        return catalog.recommend_by_title(title, limit=limit)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get(
    "/api/recommendations/by-genre",
    response_model=RecommendationResponse,
    tags=["recommendations"],
    summary="Recommend anime from a genre or tag",
    description=(
        "Returns recommendations drawn from a requested genre or editorial tag. "
        "Common spelling aliases such as `Shonen` and `Shojo` are normalized internally."
    ),
    response_description="Genre-anchored recommendation set from the public-safe catalog.",
    responses={
        404: {
            **NOT_FOUND_RESPONSE,
            "content": {
                "application/json": {
                    "example": {
                        "detail": 'No genre named "Space Opera" was found in the dataset.'
                    }
                }
            },
        }
    },
)
def recommendation_by_genre(
    genre: str = Query(
        ...,
        min_length=1,
        max_length=80,
        description="Genre or tag used to build the recommendation set.",
        openapi_examples={
            "canonical": {"summary": "Canonical genre label", "value": "Shounen"},
            "alias": {"summary": "Accepted spelling alias", "value": "Shonen"},
        },
    ),
    limit: int = Query(
        default=12,
        ge=1,
        le=24,
        description="Maximum number of recommendations to return.",
        openapi_examples={
            "default": {"summary": "Default recommendation size", "value": 12},
            "short": {"summary": "Smaller recommendation strip", "value": 5},
        },
    ),
    catalog: AnimeCatalog = Depends(get_catalog),
) -> RecommendationResponse:
    try:
        return catalog.recommend_by_genre(genre, limit=limit)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
