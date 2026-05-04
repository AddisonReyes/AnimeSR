from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ROOT_RESPONSE_EXAMPLE = {"message": "Anime Recommendation API"}
ERROR_RESPONSE_EXAMPLE = {"detail": 'No anime matched "Naruto X".'}
ANIME_SUMMARY_EXAMPLE = {
    "anime_id": 5114,
    "title": "Fullmetal Alchemist: Brotherhood",
    "english_name": "Fullmetal Alchemist: Brotherhood",
    "image_url": "https://cdn.myanimelist.net/images/anime/1223/96541.jpg",
    "score": 9.1,
    "episodes": 64,
    "type": "TV",
    "tags": ["Action", "Adventure", "Fantasy", "Shounen"],
    "short_synopsis": "Two brothers search for the Philosopher's Stone after a failed alchemy ritual changes their lives.",
}
ANIME_DETAIL_EXAMPLE = {
    **ANIME_SUMMARY_EXAMPLE,
    "other_name": "Hagane no Renkinjutsushi: Fullmetal Alchemist",
    "synopsis": (
        "Two brothers search for the Philosopher's Stone after a failed alchemy ritual changes their lives forever, "
        "pushing them into military conspiracies, moral dilemmas, and large-scale battles."
    ),
    "aired": "Apr 5, 2009 to Jul 4, 2010",
    "premiered": "Spring 2009",
    "status": "Finished Airing",
    "producers": ["Aniplex", "Square Enix"],
    "licensors": ["Funimation"],
    "studios": ["Bones"],
    "source": "Manga",
    "duration": "24 min per ep",
    "rating_label": "R - 17+ (violence & profanity)",
    "rank": 1,
    "popularity": 3,
    "favorites": 230000,
    "scored_by": 2000000,
    "members": 3300000,
}
GENRE_OPTION_EXAMPLE = {"name": "Shounen", "display_name": "Shonen", "count": 428}
RECOMMENDATION_RESPONSE_EXAMPLE = {
    "source_type": "title",
    "source_label": "Similar to Fullmetal Alchemist: Brotherhood",
    "anchor": ANIME_SUMMARY_EXAMPLE,
    "results": [
        {
            "anime_id": 9253,
            "title": "Steins;Gate",
            "english_name": "Steins;Gate",
            "image_url": "https://cdn.myanimelist.net/images/anime/1935/127974.jpg",
            "score": 9.07,
            "episodes": 24,
            "type": "TV",
            "tags": ["Drama", "Sci-Fi", "Suspense"],
            "short_synopsis": "A self-proclaimed mad scientist accidentally discovers a way to send messages through time.",
        },
        {
            "anime_id": 11061,
            "title": "Hunter x Hunter (2011)",
            "english_name": "Hunter x Hunter (2011)",
            "image_url": "https://cdn.myanimelist.net/images/anime/1337/99013.jpg",
            "score": 9.04,
            "episodes": 148,
            "type": "TV",
            "tags": ["Action", "Adventure", "Fantasy", "Shounen"],
            "short_synopsis": "A determined boy enters the Hunter Exam while searching for the legendary father who left him behind.",
        },
    ],
}
SEARCH_RESPONSE_EXAMPLE = {
    "query": "fullmetal",
    "results": [
        ANIME_SUMMARY_EXAMPLE,
        {
            "anime_id": 121,
            "title": "Fullmetal Alchemist",
            "english_name": "Fullmetal Alchemist",
            "image_url": "https://cdn.myanimelist.net/images/anime/1208/94745.jpg",
            "score": 8.11,
            "episodes": 51,
            "type": "TV",
            "tags": ["Action", "Adventure", "Drama", "Fantasy", "Shounen"],
            "short_synopsis": "Two brothers become state alchemists while searching for a way to restore their bodies.",
        },
    ],
}
HEALTH_RESPONSE_EXAMPLE = {"status": "ok", "total_anime": 24905, "total_safe_anime": 24600}


class RootResponse(BaseModel):
    message: str = Field(
        description="Human-readable identifier for the API entrypoint.",
        examples=["Anime Recommendation API"],
    )

    model_config = ConfigDict(json_schema_extra={"example": ROOT_RESPONSE_EXAMPLE})


class ErrorResponse(BaseModel):
    detail: str = Field(
        description="Human-readable explanation of why the request could not be fulfilled.",
        examples=['No anime matched "Naruto X".'],
    )

    model_config = ConfigDict(json_schema_extra={"example": ERROR_RESPONSE_EXAMPLE})


class AnimeSummary(BaseModel):
    anime_id: int = Field(
        description="Unique anime identifier taken from the dataset and used across API endpoints.",
        examples=[5114],
    )
    title: str = Field(
        description="Primary title displayed by the API and used as the canonical catalog label.",
        examples=["Fullmetal Alchemist: Brotherhood"],
    )
    english_name: str | None = Field(
        default=None,
        description="English or localized title when available and different from the canonical title.",
        examples=["Fullmetal Alchemist: Brotherhood"],
    )
    image_url: str | None = Field(
        default=None,
        description="Poster or cover image URL suitable for cards, lists, and detail views.",
        examples=["https://cdn.myanimelist.net/images/anime/1223/96541.jpg"],
    )
    score: float | None = Field(
        default=None,
        description="Community score from the source dataset.",
        examples=[9.1],
    )
    episodes: int | None = Field(
        default=None,
        description="Known number of episodes when the dataset provides it.",
        examples=[64],
    )
    type: str | None = Field(
        default=None,
        description="Production format such as TV, Movie, OVA, or Special.",
        examples=["TV"],
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Merged list of genres and legacy editorial tags used by search and recommendation logic.",
        examples=[["Action", "Adventure", "Fantasy", "Shounen"]],
    )
    short_synopsis: str | None = Field(
        default=None,
        description="Shortened synopsis intended for compact UI cards or search results.",
        examples=["Two brothers search for the Philosopher's Stone after a failed alchemy ritual changes their lives."],
    )

    model_config = ConfigDict(json_schema_extra={"example": ANIME_SUMMARY_EXAMPLE})


class AnimeDetail(AnimeSummary):
    other_name: str | None = Field(
        default=None,
        description="Alternative title stored in the dataset, often romanized or regional.",
        examples=["Hagane no Renkinjutsushi: Fullmetal Alchemist"],
    )
    synopsis: str | None = Field(
        default=None,
        description="Full synopsis used in the anime detail modal and richer catalog views.",
        examples=[
            "Two brothers search for the Philosopher's Stone after a failed alchemy ritual changes their lives forever."
        ],
    )
    aired: str | None = Field(
        default=None,
        description="Broadcast date range as provided by the source dataset.",
        examples=["Apr 5, 2009 to Jul 4, 2010"],
    )
    premiered: str | None = Field(
        default=None,
        description="Season and year of premiere when available.",
        examples=["Spring 2009"],
    )
    status: str | None = Field(
        default=None,
        description="Release status such as Finished Airing, Currently Airing, or Not yet aired.",
        examples=["Finished Airing"],
    )
    producers: list[str] = Field(
        default_factory=list,
        description="Producers credited in the dataset.",
        examples=[["Aniplex", "Square Enix"]],
    )
    licensors: list[str] = Field(
        default_factory=list,
        description="Distribution or licensing companies credited in the dataset.",
        examples=[["Funimation"]],
    )
    studios: list[str] = Field(
        default_factory=list,
        description="Animation studios associated with the title.",
        examples=[["Bones"]],
    )
    source: str | None = Field(
        default=None,
        description="Original source material such as Manga, Light novel, or Original.",
        examples=["Manga"],
    )
    duration: str | None = Field(
        default=None,
        description="Episode or runtime duration in the original dataset format.",
        examples=["24 min per ep"],
    )
    rating_label: str | None = Field(
        default=None,
        description="Content rating label from the dataset.",
        examples=["R - 17+ (violence & profanity)"],
    )
    rank: int | None = Field(
        default=None,
        description="Ranking position in the source dataset when available.",
        examples=[1],
    )
    popularity: int | None = Field(
        default=None,
        description="Popularity ranking in the source dataset. Lower numbers mean more popular titles.",
        examples=[3],
    )
    favorites: int | None = Field(
        default=None,
        description="Favorite count captured from the source dataset.",
        examples=[230000],
    )
    scored_by: int | None = Field(
        default=None,
        description="Number of users who contributed to the public score.",
        examples=[2000000],
    )
    members: int | None = Field(
        default=None,
        description="Member count captured from the source dataset.",
        examples=[3300000],
    )

    model_config = ConfigDict(json_schema_extra={"example": ANIME_DETAIL_EXAMPLE})


class GenreOption(BaseModel):
    name: str = Field(
        description="Canonical internal genre or tag name used by the recommendation engine.",
        examples=["Shounen"],
    )
    display_name: str = Field(
        description="UI-friendly label that may normalize capitalization or spelling for display.",
        examples=["Shonen"],
    )
    count: int = Field(
        description="Number of safe catalog titles associated with this genre or tag.",
        examples=[428],
    )

    model_config = ConfigDict(json_schema_extra={"example": GENRE_OPTION_EXAMPLE})


class RecommendationResponse(BaseModel):
    source_type: Literal["title", "genre", "highlights"] = Field(
        description="Type of recommendation request that produced the response.",
        examples=["title"],
    )
    source_label: str = Field(
        description="Human-readable label describing the recommendation source shown in the UI.",
        examples=["Similar to Fullmetal Alchemist: Brotherhood"],
    )
    anchor: AnimeSummary | None = Field(
        default=None,
        description="Anchor anime used for title-based recommendations. `null` for genre and highlight responses.",
    )
    results: list[AnimeSummary] = Field(
        description="Ordered list of recommended anime returned by the ranking pipeline.",
    )

    model_config = ConfigDict(json_schema_extra={"example": RECOMMENDATION_RESPONSE_EXAMPLE})


class SearchResponse(BaseModel):
    query: str = Field(
        description="Original search string supplied by the client.",
        examples=["fullmetal"],
    )
    results: list[AnimeSummary] = Field(
        description="Ranked list of fuzzy and exact title matches for the requested query.",
    )

    model_config = ConfigDict(json_schema_extra={"example": SEARCH_RESPONSE_EXAMPLE})


class HealthResponse(BaseModel):
    status: str = Field(
        description="Health indicator for the API process.",
        examples=["ok"],
    )
    total_anime: int = Field(
        description="Total number of catalog records loaded into memory, including filtered titles.",
        examples=[24905],
    )
    total_safe_anime: int = Field(
        description="Number of public-safe records available for search and recommendations.",
        examples=[24600],
    )

    model_config = ConfigDict(json_schema_extra={"example": HEALTH_RESPONSE_EXAMPLE})
