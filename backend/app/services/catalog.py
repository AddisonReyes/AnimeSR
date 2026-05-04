from __future__ import annotations

import csv
import math
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas import AnimeDetail, AnimeSummary, GenreOption, RecommendationResponse

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "backend"
DATASET_PATH = BACKEND_DIR / "anime-dataset-2023.csv"
LEGACY_DATASET_PATH = REPO_ROOT / "deprecated" / "anime.csv"
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


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", value).strip()
    if not text or text in UNKNOWN_VALUES:
        return None
    return text


def _normalize_text(value: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    collapsed = re.sub(r"[^a-zA-Z0-9]+", " ", ascii_text).strip().lower()
    return re.sub(r"\s+", " ", collapsed)


def _parse_float(value: str | None) -> float | None:
    text = _clean_text(value)
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_int(value: str | None) -> int | None:
    text = _clean_text(value)
    if text is None:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _parse_list(value: str | None) -> list[str]:
    text = _clean_text(value)
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


def _truncate(text: str | None, limit: int = 180) -> str | None:
    if not text:
        return None
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}..."


class AnimeCatalog:
    def __init__(
        self,
        dataset_path: Path = DATASET_PATH,
        legacy_dataset_path: Path = LEGACY_DATASET_PATH,
    ) -> None:
        self.dataset_path = dataset_path
        self.legacy_dataset_path = legacy_dataset_path
        self.legacy_tags_by_id = self._load_legacy_tags()
        self.records = self._load_records()
        self.records_by_id = {record.anime_id: record for record in self.records}
        self.record_indices_by_id = {record.anime_id: index for index, record in enumerate(self.records)}
        self.safe_records = [record for record in self.records if not record.is_adult]
        self.safe_titles = [record.normalized_title for record in self.safe_records]
        self.safe_title_lookup = self._build_title_lookup()
        self.genre_lookup = self._build_genre_lookup()
        self.genre_to_records = self._build_genre_to_records()
        self.featured_genres = self._build_featured_genres()
        self._assign_catalog_scores()
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=14000, ngram_range=(1, 2))
        self.feature_matrix = self.vectorizer.fit_transform([record.feature_text for record in self.records])
        self.recommendation_cache: dict[int, list[int]] = {}
        self.genre_cache: dict[str, list[int]] = {}
        self.highlights = self._build_highlights(limit=24)

    def _load_legacy_tags(self) -> dict[int, list[str]]:
        legacy_tags: dict[int, list[str]] = {}
        with self.legacy_dataset_path.open(encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                anime_id = _parse_int(row.get("anime_id"))
                if anime_id is None:
                    continue
                legacy_tags[anime_id] = _parse_list(row.get("genre"))
        return legacy_tags

    def _load_records(self) -> list[AnimeRecord]:
        records: list[AnimeRecord] = []
        with self.dataset_path.open(encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                anime_id = _parse_int(row.get("anime_id"))
                title = _clean_text(row.get("Name"))
                if anime_id is None or title is None:
                    continue

                genres = _parse_list(row.get("Genres"))
                legacy_tags = self.legacy_tags_by_id.get(anime_id, [])
                tags = list(dict.fromkeys([*genres, *legacy_tags]))
                synopsis = _clean_text(row.get("Synopsis"))
                english_name = _clean_text(row.get("English name"))
                other_name = _clean_text(row.get("Other name"))
                producers = _parse_list(row.get("Producers"))
                licensors = _parse_list(row.get("Licensors"))
                studios = _parse_list(row.get("Studios"))
                type_name = _clean_text(row.get("Type"))
                source = _clean_text(row.get("Source"))
                rating_label = _clean_text(row.get("Rating"))
                is_adult = any(tag in ADULT_TAGS for tag in tags) or bool(rating_label and rating_label.startswith("Rx"))
                normalized_title = _normalize_text(title)
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

                records.append(
                    AnimeRecord(
                        anime_id=anime_id,
                        title=title,
                        english_name=english_name if english_name != title else None,
                        other_name=other_name if other_name != title else None,
                        score=_parse_float(row.get("Score")),
                        genres=genres,
                        legacy_tags=legacy_tags,
                        tags=tags,
                        tag_set=frozenset(tags),
                        synopsis=synopsis,
                        type=type_name,
                        episodes=_parse_int(row.get("Episodes")),
                        aired=_clean_text(row.get("Aired")),
                        premiered=_clean_text(row.get("Premiered")),
                        status=_clean_text(row.get("Status")),
                        producers=producers,
                        licensors=licensors,
                        studios=studios,
                        source=source,
                        duration=_clean_text(row.get("Duration")),
                        rating_label=rating_label,
                        rank=_parse_int(row.get("Rank")),
                        popularity=_parse_int(row.get("Popularity")),
                        favorites=_parse_int(row.get("Favorites")),
                        scored_by=_parse_int(row.get("Scored By")),
                        members=_parse_int(row.get("Members")),
                        image_url=_clean_text(row.get("Image URL")),
                        is_adult=is_adult,
                        normalized_title=normalized_title,
                        normalized_search_text=_normalize_text(" ".join(search_bits)),
                        feature_text=" ".join(feature_bits),
                    )
                )
        return records

    def _assign_catalog_scores(self) -> None:
        max_members = max((record.members or 0) for record in self.records) or 1
        max_favorites = max((record.favorites or 0) for record in self.records) or 1
        max_scored_by = max((record.scored_by or 0) for record in self.records) or 1
        max_members_log = math.log10(max_members + 1)
        max_favorites_log = math.log10(max_favorites + 1)
        max_scored_by_log = math.log10(max_scored_by + 1)

        for record in self.records:
            quality = (record.score or 0.0) / 10
            members = math.log10((record.members or 0) + 1) / max_members_log
            favorites = math.log10((record.favorites or 0) + 1) / max_favorites_log
            scored_by = math.log10((record.scored_by or 0) + 1) / max_scored_by_log
            popularity = 0.0
            if record.popularity:
                popularity = max(0.0, 1 - min(record.popularity, 5000) / 5000)
            record.catalog_score = round(
                0.45 * quality + 0.2 * members + 0.15 * favorites + 0.1 * scored_by + 0.1 * popularity,
                4,
            )

    def _build_title_lookup(self) -> dict[str, list[AnimeRecord]]:
        lookup: dict[str, list[AnimeRecord]] = defaultdict(list)
        for record in self.safe_records:
            lookup[record.normalized_title].append(record)
        return lookup

    def _build_genre_lookup(self) -> dict[str, str]:
        lookup: dict[str, str] = {}
        for record in self.safe_records:
            for tag in record.tags:
                lookup[_normalize_text(tag)] = tag
        return lookup

    def _build_genre_to_records(self) -> dict[str, list[AnimeRecord]]:
        mapping: dict[str, list[AnimeRecord]] = defaultdict(list)
        for record in self.safe_records:
            for tag in record.tags:
                mapping[tag].append(record)
        return mapping

    def _build_featured_genres(self) -> list[GenreOption]:
        counts = Counter()
        for record in self.safe_records:
            for tag in record.tags:
                counts[tag] += 1

        featured: list[GenreOption] = []
        added: set[str] = set()

        for tag in FEATURED_GENRE_ORDER:
            count = counts.get(tag)
            if count:
                featured.append(GenreOption(name=tag, display_name=DISPLAY_ALIASES.get(tag, tag), count=count))
                added.add(tag)

        for tag, count in counts.most_common():
            if tag in added or tag in ADULT_TAGS:
                continue
            featured.append(GenreOption(name=tag, display_name=DISPLAY_ALIASES.get(tag, tag), count=count))
            if len(featured) >= 20:
                break

        return featured

    def _build_highlights(self, limit: int) -> list[AnimeRecord]:
        candidates = [record for record in self.safe_records if record.score and record.image_url and record.synopsis]
        return sorted(candidates, key=lambda record: (record.catalog_score, record.score or 0), reverse=True)[:limit]

    def _title_score(self, query: str, record: AnimeRecord) -> float:
        title = record.normalized_title
        haystack = record.normalized_search_text
        if query == title:
            return 3000 + record.catalog_score * 100
        if title.startswith(query):
            return 2200 - len(title) + record.catalog_score * 100
        spaced = f" {query}"
        if spaced in f" {title}":
            return 1800 + record.catalog_score * 100
        if query in haystack:
            return 1400 - haystack.find(query) + record.catalog_score * 100
        return 0.0

    def _resolve_genre(self, genre: str) -> str | None:
        normalized = _normalize_text(genre)
        normalized = QUERY_ALIASES.get(normalized, normalized)
        return self.genre_lookup.get(normalized)

    def _find_by_title(self, title: str) -> AnimeRecord:
        matches = self.search(title, limit=1)
        if not matches:
            raise LookupError(f'No anime matched "{title}".')
        return self.records_by_id[matches[0].anime_id]

    def _summary(self, record: AnimeRecord) -> AnimeSummary:
        return AnimeSummary(
            anime_id=record.anime_id,
            title=record.title,
            english_name=record.english_name,
            image_url=record.image_url,
            score=record.score,
            episodes=record.episodes,
            type=record.type,
            tags=record.tags,
            short_synopsis=_truncate(record.synopsis),
        )

    def _detail(self, record: AnimeRecord) -> AnimeDetail:
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
            short_synopsis=_truncate(record.synopsis),
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

    def _is_same_franchise(self, anchor: AnimeRecord, candidate: AnimeRecord) -> bool:
        anchor_title = anchor.normalized_title
        candidate_title = candidate.normalized_title
        if len(anchor_title.replace(" ", "")) < 5:
            return False
        padded_anchor = f" {anchor_title} "
        padded_candidate = f" {candidate_title} "
        if padded_anchor in padded_candidate or padded_candidate in padded_anchor:
            return True

        anchor_tokens = anchor_title.split()
        candidate_tokens = candidate_title.split()
        if len(anchor_tokens) >= 2 and len(candidate_tokens) >= 2:
            anchor_prefix = " ".join(anchor_tokens[:2])
            candidate_prefix = " ".join(candidate_tokens[:2])
            if len(anchor_prefix.replace(" ", "")) >= 6 and anchor_prefix == candidate_prefix:
                return True

        return False

    def _diversify_records(self, ranked_records: list[AnimeRecord], limit: int) -> list[AnimeRecord]:
        diversified: list[AnimeRecord] = []

        for candidate in ranked_records:
            if any(self._is_same_franchise(candidate, chosen) for chosen in diversified):
                continue
            diversified.append(candidate)
            if len(diversified) >= limit:
                return diversified

        for candidate in ranked_records:
            if candidate in diversified:
                continue
            diversified.append(candidate)
            if len(diversified) >= limit:
                return diversified

        return diversified

    def search(self, query: str, limit: int = 8) -> list[AnimeSummary]:
        normalized_query = _normalize_text(query)
        if not normalized_query:
            return []

        scored_results: list[tuple[float, AnimeRecord]] = []
        for record in self.safe_records:
            score = self._title_score(normalized_query, record)
            if score > 0:
                scored_results.append((score, record))

        scored_results.sort(key=lambda item: item[0], reverse=True)
        results: list[AnimeRecord] = []
        seen_ids: set[int] = set()

        for _, record in scored_results[: limit * 3]:
            if record.anime_id in seen_ids:
                continue
            seen_ids.add(record.anime_id)
            results.append(record)
            if len(results) >= limit:
                return [self._summary(record) for record in results]

        for close_match in get_close_matches(normalized_query, self.safe_titles, n=limit * 3, cutoff=0.72):
            for record in self.safe_title_lookup.get(close_match, []):
                if record.anime_id in seen_ids:
                    continue
                seen_ids.add(record.anime_id)
                results.append(record)
                if len(results) >= limit:
                    return [self._summary(record) for record in results]

        return [self._summary(record) for record in results]

    def get_anime_detail(self, anime_id: int) -> AnimeDetail:
        record = self.records_by_id.get(anime_id)
        if record is None or record.is_adult:
            raise LookupError(f"No safe anime found with id {anime_id}.")
        return self._detail(record)

    def get_featured_genres(self, limit: int = 18) -> list[GenreOption]:
        return self.featured_genres[:limit]

    def get_highlights(self, limit: int = 12) -> RecommendationResponse:
        return RecommendationResponse(
            source_type="highlights",
            source_label="Editor's picks from across the catalog",
            results=[self._summary(record) for record in self.highlights[:limit]],
        )

    def _recommend_for_record(self, record: AnimeRecord, limit: int) -> list[AnimeSummary]:
        cached_ids = self.recommendation_cache.get(record.anime_id)
        if cached_ids is None:
            anchor_index = self.record_indices_by_id[record.anime_id]
            similarities = cosine_similarity(self.feature_matrix[anchor_index], self.feature_matrix).ravel()
            ranked: list[tuple[float, AnimeRecord]] = []
            for index, similarity in enumerate(similarities):
                candidate = self.records[index]
                if candidate.anime_id == record.anime_id or candidate.is_adult:
                    continue
                if self._is_same_franchise(record, candidate):
                    continue
                overlap = len(record.tag_set & candidate.tag_set) / max(len(record.tag_set), 1)
                same_type = 0.03 if record.type and record.type == candidate.type else 0.0
                final_score = 0.72 * float(similarity) + 0.2 * candidate.catalog_score + 0.08 * overlap + same_type
                ranked.append((final_score, candidate))

            ranked.sort(key=lambda item: item[0], reverse=True)
            diversified = self._diversify_records([candidate for _, candidate in ranked], limit=60)
            cached_ids = [candidate.anime_id for candidate in diversified]
            self.recommendation_cache[record.anime_id] = cached_ids

        return [self._summary(self.records_by_id[anime_id]) for anime_id in cached_ids[:limit]]

    def recommend_by_title(self, title: str, limit: int = 12) -> RecommendationResponse:
        anchor = self._find_by_title(title)
        return RecommendationResponse(
            source_type="title",
            source_label=f"Similar to {anchor.title}",
            anchor=self._summary(anchor),
            results=self._recommend_for_record(anchor, limit),
        )

    def recommend_by_genre(self, genre: str, limit: int = 12) -> RecommendationResponse:
        canonical_genre = self._resolve_genre(genre)
        if canonical_genre is None:
            raise LookupError(f'No genre named "{genre}" was found in the dataset.')

        cached_ids = self.genre_cache.get(canonical_genre)
        if cached_ids is None:
            candidates = self.genre_to_records.get(canonical_genre, [])
            ranked = sorted(
                candidates,
                key=lambda record: (
                    record.catalog_score,
                    record.score or 0,
                    record.members or 0,
                    record.favorites or 0,
                ),
                reverse=True,
            )
            diversified = self._diversify_records(ranked, limit=60)
            cached_ids = [record.anime_id for record in diversified]
            self.genre_cache[canonical_genre] = cached_ids

        return RecommendationResponse(
            source_type="genre",
            source_label=f"Best of {DISPLAY_ALIASES.get(canonical_genre, canonical_genre)}",
            results=[self._summary(self.records_by_id[anime_id]) for anime_id in cached_ids[:limit]],
        )
