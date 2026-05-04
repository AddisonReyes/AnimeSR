from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AnimeSummary(BaseModel):
    anime_id: int
    title: str
    english_name: str | None = None
    image_url: str | None = None
    score: float | None = None
    episodes: int | None = None
    type: str | None = None
    tags: list[str] = Field(default_factory=list)
    short_synopsis: str | None = None


class AnimeDetail(AnimeSummary):
    other_name: str | None = None
    synopsis: str | None = None
    aired: str | None = None
    premiered: str | None = None
    status: str | None = None
    producers: list[str] = Field(default_factory=list)
    licensors: list[str] = Field(default_factory=list)
    studios: list[str] = Field(default_factory=list)
    source: str | None = None
    duration: str | None = None
    rating_label: str | None = None
    rank: int | None = None
    popularity: int | None = None
    favorites: int | None = None
    scored_by: int | None = None
    members: int | None = None


class GenreOption(BaseModel):
    name: str
    display_name: str
    count: int


class RecommendationResponse(BaseModel):
    source_type: Literal["title", "genre", "highlights"]
    source_label: str
    anchor: AnimeSummary | None = None
    results: list[AnimeSummary]


class SearchResponse(BaseModel):
    query: str
    results: list[AnimeSummary]


class HealthResponse(BaseModel):
    status: str
    total_anime: int
    total_safe_anime: int
