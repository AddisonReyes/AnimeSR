from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from difflib import get_close_matches
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas import AnimeDetail, AnimeSummary, GenreOption, RecommendationResponse
from app.services.catalog_support import (
    DISPLAY_ALIASES,
    FEATURED_GENRE_ORDER,
    QUERY_ALIASES,
    AnimeRecord,
    build_anime_record,
    normalize_text,
    parse_int,
    parse_list,
    to_detail,
    to_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "backend"
DATASET_PATH = BACKEND_DIR / "anime-dataset-2023.csv"
LEGACY_DATASET_PATH = REPO_ROOT / "deprecated" / "anime.csv"
MAX_FEATURES = 14_000
FEATURE_NGRAM_RANGE = (1, 2)
SEARCH_CANDIDATE_MULTIPLIER = 3
FUZZY_MATCH_CUTOFF = 0.72
HIGHLIGHT_CACHE_LIMIT = 24
RECOMMENDATION_CACHE_LIMIT = 60
POPULARITY_CAP = 5_000
SAME_TYPE_BONUS = 0.03

CATALOG_SCORE_WEIGHTS = {
    "quality": 0.45,
    "members": 0.2,
    "favorites": 0.15,
    "scored_by": 0.1,
    "popularity": 0.1,
}

RECOMMENDATION_SCORE_WEIGHTS = {
    "similarity": 0.72,
    "catalog_score": 0.2,
    "tag_overlap": 0.08,
}


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
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=MAX_FEATURES,
            ngram_range=FEATURE_NGRAM_RANGE,
        )
        self.feature_matrix = self.vectorizer.fit_transform([record.feature_text for record in self.records])
        self.recommendation_cache: dict[int, list[int]] = {}
        self.genre_cache: dict[str, list[int]] = {}
        self.highlights = self._build_highlights(limit=HIGHLIGHT_CACHE_LIMIT)

    def _load_legacy_tags(self) -> dict[int, list[str]]:
        legacy_tags: dict[int, list[str]] = {}
        with self.legacy_dataset_path.open(encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                anime_id = parse_int(row.get("anime_id"))
                if anime_id is None:
                    continue
                legacy_tags[anime_id] = parse_list(row.get("genre"))
        return legacy_tags

    def _load_records(self) -> list[AnimeRecord]:
        records: list[AnimeRecord] = []
        with self.dataset_path.open(encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                anime_id = parse_int(row.get("anime_id"))
                if anime_id is None:
                    continue
                legacy_tags = self.legacy_tags_by_id.get(anime_id, [])
                record = build_anime_record(row, legacy_tags)
                if record is not None:
                    records.append(record)
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
                popularity = max(0.0, 1 - min(record.popularity, POPULARITY_CAP) / POPULARITY_CAP)
            record.catalog_score = round(
                CATALOG_SCORE_WEIGHTS["quality"] * quality
                + CATALOG_SCORE_WEIGHTS["members"] * members
                + CATALOG_SCORE_WEIGHTS["favorites"] * favorites
                + CATALOG_SCORE_WEIGHTS["scored_by"] * scored_by
                + CATALOG_SCORE_WEIGHTS["popularity"] * popularity,
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
                lookup[normalize_text(tag)] = tag
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
            if tag in added:
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
        normalized = normalize_text(genre)
        normalized = QUERY_ALIASES.get(normalized, normalized)
        return self.genre_lookup.get(normalized)

    def _find_by_title(self, title: str) -> AnimeRecord:
        matches = self.search(title, limit=1)
        if not matches:
            raise LookupError(f'No anime matched "{title}".')
        return self.records_by_id[matches[0].anime_id]

    def _summary(self, record: AnimeRecord) -> AnimeSummary:
        return to_summary(record)

    def _detail(self, record: AnimeRecord) -> AnimeDetail:
        return to_detail(record)

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

    def _append_unique_records(
        self,
        results: list[AnimeRecord],
        seen_ids: set[int],
        candidates: list[AnimeRecord],
        limit: int,
    ) -> bool:
        for record in candidates:
            if record.anime_id in seen_ids:
                continue
            seen_ids.add(record.anime_id)
            results.append(record)
            if len(results) >= limit:
                return True
        return False

    def _summaries_from_records(self, records: list[AnimeRecord]) -> list[AnimeSummary]:
        return [self._summary(record) for record in records]

    def _summaries_from_ids(self, anime_ids: list[int], limit: int) -> list[AnimeSummary]:
        return [self._summary(self.records_by_id[anime_id]) for anime_id in anime_ids[:limit]]

    def search(self, query: str, limit: int = 8) -> list[AnimeSummary]:
        normalized_query = normalize_text(query)
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
        direct_matches = [record for _, record in scored_results[: limit * SEARCH_CANDIDATE_MULTIPLIER]]

        if self._append_unique_records(results, seen_ids, direct_matches, limit):
            return self._summaries_from_records(results)

        fuzzy_matches: list[AnimeRecord] = []
        for close_match in get_close_matches(
            normalized_query,
            self.safe_titles,
            n=limit * SEARCH_CANDIDATE_MULTIPLIER,
            cutoff=FUZZY_MATCH_CUTOFF,
        ):
            for record in self.safe_title_lookup.get(close_match, []):
                fuzzy_matches.append(record)

        self._append_unique_records(results, seen_ids, fuzzy_matches, limit)
        return self._summaries_from_records(results)

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
            results=self._summaries_from_records(self.highlights[:limit]),
        )

    def _score_recommendation_candidate(self, anchor: AnimeRecord, candidate: AnimeRecord, similarity: float) -> float:
        overlap = len(anchor.tag_set & candidate.tag_set) / max(len(anchor.tag_set), 1)
        same_type = SAME_TYPE_BONUS if anchor.type and anchor.type == candidate.type else 0.0
        return (
            RECOMMENDATION_SCORE_WEIGHTS["similarity"] * float(similarity)
            + RECOMMENDATION_SCORE_WEIGHTS["catalog_score"] * candidate.catalog_score
            + RECOMMENDATION_SCORE_WEIGHTS["tag_overlap"] * overlap
            + same_type
        )

    def _build_recommendation_ids(self, record: AnimeRecord) -> list[int]:
        anchor_index = self.record_indices_by_id[record.anime_id]
        similarities = cosine_similarity(self.feature_matrix[anchor_index], self.feature_matrix).ravel()
        ranked: list[tuple[float, AnimeRecord]] = []

        for index, similarity in enumerate(similarities):
            candidate = self.records[index]
            if candidate.anime_id == record.anime_id or candidate.is_adult:
                continue
            if self._is_same_franchise(record, candidate):
                continue
            ranked.append((self._score_recommendation_candidate(record, candidate, float(similarity)), candidate))

        ranked.sort(key=lambda item: item[0], reverse=True)
        diversified = self._diversify_records([candidate for _, candidate in ranked], limit=RECOMMENDATION_CACHE_LIMIT)
        return [candidate.anime_id for candidate in diversified]

    def _get_recommendation_ids(self, record: AnimeRecord) -> list[int]:
        cached_ids = self.recommendation_cache.get(record.anime_id)
        if cached_ids is None:
            cached_ids = self._build_recommendation_ids(record)
            self.recommendation_cache[record.anime_id] = cached_ids
        return cached_ids

    def _build_genre_recommendation_ids(self, canonical_genre: str) -> list[int]:
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
        diversified = self._diversify_records(ranked, limit=RECOMMENDATION_CACHE_LIMIT)
        return [record.anime_id for record in diversified]

    def _get_genre_recommendation_ids(self, canonical_genre: str) -> list[int]:
        cached_ids = self.genre_cache.get(canonical_genre)
        if cached_ids is None:
            cached_ids = self._build_genre_recommendation_ids(canonical_genre)
            self.genre_cache[canonical_genre] = cached_ids
        return cached_ids

    def _recommend_for_record(self, record: AnimeRecord, limit: int) -> list[AnimeSummary]:
        return self._summaries_from_ids(self._get_recommendation_ids(record), limit)

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

        return RecommendationResponse(
            source_type="genre",
            source_label=f"Best of {DISPLAY_ALIASES.get(canonical_genre, canonical_genre)}",
            results=self._summaries_from_ids(self._get_genre_recommendation_ids(canonical_genre), limit),
        )
