from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass

from app.schemas import AnimeDetail, AnimeSummary

UNKNOWN_VALUES = {"", "UNKNOWN", "Unknown", "None", "nan"}
ADULT_TAGS = {"Hentai", "Erotica"}
DISPLAY_ALIASES = {
    "Shounen": "Shonen",
    "Shoujo": "Shojo",
    "Sci-Fi": "Sci-Fi",
    "Slice of Life": "Slice of Life",
    "Super Power": "Super Power",
}
QUERY_ALIASES = {
    "shonen": "shounen",
    "shojo": "shoujo",
}
FEATURED_GENRE_ORDER = [
    "Action",
    "Adventure",
    "Fantasy",
    "Comedy",
    "Drama",
    "Romance",
    "Sci-Fi",
    "Slice of Life",
    "Sports",
    "Mystery",
    "Supernatural",
    "Shounen",
    "Seinen",
    "Shoujo",
    "School",
    "Magic",
    "Psychological",
]


@dataclass(slots=True)
class AnimeRecord:
    anime_id: int
    title: str
    english_name: str | None
    other_name: str | None
    score: float | None
    genres: list[str]
    legacy_tags: list[str]
    tags: list[str]
    tag_set: frozenset[str]
    synopsis: str | None
    type: str | None
    episodes: int | None
    aired: str | None
    premiered: str | None
    status: str | None
    producers: list[str]
    licensors: list[str]
    studios: list[str]
    source: str | None
    duration: str | None
    rating_label: str | None
    rank: int | None
    popularity: int | None
    favorites: int | None
    scored_by: int | None
    members: int | None
    image_url: str | None
    is_adult: bool
    normalized_title: str
    normalized_search_text: str
    feature_text: str
    catalog_score: float = 0.0


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", value).strip()
    if not text or text in UNKNOWN_VALUES:
        return None
    return text


def normalize_text(value: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    collapsed = re.sub(r"[^a-zA-Z0-9]+", " ", ascii_text).strip().lower()
    return re.sub(r"\s+", " ", collapsed)


def parse_float(value: str | None) -> float | None:
    text = clean_text(value)
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_int(value: str | None) -> int | None:
    text = clean_text(value)
    if text is None:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def parse_list(value: str | None) -> list[str]:
    text = clean_text(value)
    if text is None:
        return []

    items: list[str] = []
    seen: set[str] = set()
    for part in text.split(","):
        item = part.strip()
        if not item or item in UNKNOWN_VALUES or item in seen:
            continue
        seen.add(item)
        items.append(item)
    return items


def truncate_text(text: str | None, limit: int = 180) -> str | None:
    if not text:
        return None
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}..."


def merge_tags(*tag_groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()

    for group in tag_groups:
        for tag in group:
            if tag in seen:
                continue
            seen.add(tag)
            merged.append(tag)

    return merged


def is_adult_record(tags: list[str], rating_label: str | None) -> bool:
    return any(tag in ADULT_TAGS for tag in tags) or bool(rating_label and rating_label.startswith("Rx"))


def build_anime_record(row: Mapping[str, str | None], legacy_tags: list[str]) -> AnimeRecord | None:
    anime_id = parse_int(row.get("anime_id"))
    title = clean_text(row.get("Name"))
    if anime_id is None or title is None:
        return None

    genres = parse_list(row.get("Genres"))
    tags = merge_tags(genres, legacy_tags)
    synopsis = clean_text(row.get("Synopsis"))
    english_name = clean_text(row.get("English name"))
    other_name = clean_text(row.get("Other name"))
    producers = parse_list(row.get("Producers"))
    licensors = parse_list(row.get("Licensors"))
    studios = parse_list(row.get("Studios"))
    type_name = clean_text(row.get("Type"))
    source = clean_text(row.get("Source"))
    rating_label = clean_text(row.get("Rating"))
    normalized_title = normalize_text(title)
    search_bits = [title, english_name or "", other_name or "", " ".join(tags)]
    feature_bits = [
        title,
        english_name or "",
        other_name or "",
        " ".join(tags),
        type_name or "",
        source or "",
        " ".join(studios),
        synopsis or "",
    ]

    return AnimeRecord(
        anime_id=anime_id,
        title=title,
        english_name=english_name if english_name != title else None,
        other_name=other_name if other_name != title else None,
        score=parse_float(row.get("Score")),
        genres=genres,
        legacy_tags=legacy_tags,
        tags=tags,
        tag_set=frozenset(tags),
        synopsis=synopsis,
        type=type_name,
        episodes=parse_int(row.get("Episodes")),
        aired=clean_text(row.get("Aired")),
        premiered=clean_text(row.get("Premiered")),
        status=clean_text(row.get("Status")),
        producers=producers,
        licensors=licensors,
        studios=studios,
        source=source,
        duration=clean_text(row.get("Duration")),
        rating_label=rating_label,
        rank=parse_int(row.get("Rank")),
        popularity=parse_int(row.get("Popularity")),
        favorites=parse_int(row.get("Favorites")),
        scored_by=parse_int(row.get("Scored By")),
        members=parse_int(row.get("Members")),
        image_url=clean_text(row.get("Image URL")),
        is_adult=is_adult_record(tags, rating_label),
        normalized_title=normalized_title,
        normalized_search_text=normalize_text(" ".join(search_bits)),
        feature_text=" ".join(feature_bits),
    )


def to_summary(record: AnimeRecord) -> AnimeSummary:
    return AnimeSummary(
        anime_id=record.anime_id,
        title=record.title,
        english_name=record.english_name,
        image_url=record.image_url,
        score=record.score,
        episodes=record.episodes,
        type=record.type,
        tags=record.tags,
        short_synopsis=truncate_text(record.synopsis),
    )


def to_detail(record: AnimeRecord) -> AnimeDetail:
    return AnimeDetail(
        anime_id=record.anime_id,
        title=record.title,
        english_name=record.english_name,
        other_name=record.other_name,
        image_url=record.image_url,
        score=record.score,
        episodes=record.episodes,
        type=record.type,
        tags=record.tags,
        short_synopsis=truncate_text(record.synopsis),
        synopsis=record.synopsis,
        aired=record.aired,
        premiered=record.premiered,
        status=record.status,
        producers=record.producers,
        licensors=record.licensors,
        studios=record.studios,
        source=record.source,
        duration=record.duration,
        rating_label=record.rating_label,
        rank=record.rank,
        popularity=record.popularity,
        favorites=record.favorites,
        scored_by=record.scored_by,
        members=record.members,
    )
