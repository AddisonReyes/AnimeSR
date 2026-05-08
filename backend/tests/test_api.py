from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.main import (
    anime_detail,
    featured_genres,
    health,
    recommendation_by_genre,
    recommendation_by_title,
    recommendation_highlights,
    root,
    search_anime,
)
from app.services.catalog import AnimeCatalog


def test_root_endpoint_returns_service_message() -> None:
    response = root()

    assert response.message == "Anime Recommendation API"


def test_health_endpoint_returns_catalog_counts(catalog: AnimeCatalog) -> None:
    response = health(catalog)

    assert response.status == "ok"
    assert response.total_anime >= response.total_safe_anime > 0


def test_title_recommendation_engine_loads_lazily() -> None:
    catalog = AnimeCatalog()

    assert not catalog.title_recommendation_engine_loaded

    recommendation_by_genre(genre="Shonen", limit=6, catalog=catalog)
    assert not catalog.title_recommendation_engine_loaded

    recommendation_by_title(title="Naruto", limit=6, catalog=catalog)
    assert catalog.title_recommendation_engine_loaded


def test_title_recommendation_engine_releases_after_idle() -> None:
    catalog = AnimeCatalog()
    catalog.feature_engine_idle_ttl_seconds = 1

    recommendation_by_title(title="Naruto", limit=6, catalog=catalog)
    assert catalog.title_recommendation_engine_loaded

    catalog._feature_engine_last_used_at -= 2
    catalog.perform_maintenance()

    assert not catalog.title_recommendation_engine_loaded


def test_featured_genres_respects_limit(catalog: AnimeCatalog) -> None:
    response = featured_genres(limit=5, catalog=catalog)

    assert len(response) == 5
    assert all(item.count > 0 for item in response)
    assert all(item.name for item in response)
    assert all(item.display_name for item in response)


def test_search_returns_expected_naruto_matches(catalog: AnimeCatalog) -> None:
    response = search_anime(q="Naruto", limit=5, catalog=catalog)

    assert response.query == "Naruto"
    assert response.results
    assert any("naruto" in anime.title.lower() for anime in response.results)


def test_anime_detail_returns_full_payload_for_search_result(catalog: AnimeCatalog) -> None:
    search_response = search_anime(q="Naruto", limit=1, catalog=catalog)
    anime_id = search_response.results[0].anime_id

    response = anime_detail(anime_id=anime_id, catalog=catalog)

    assert response.anime_id == anime_id
    assert response.title
    assert isinstance(response.tags, list)
    assert response.synopsis is not None


def test_anime_detail_returns_404_for_missing_id(catalog: AnimeCatalog) -> None:
    with pytest.raises(HTTPException) as error:
        anime_detail(anime_id=999999999, catalog=catalog)

    assert error.value.status_code == 404
    assert "No safe anime found" in error.value.detail


def test_highlights_return_ranked_results(catalog: AnimeCatalog) -> None:
    response = recommendation_highlights(limit=6, catalog=catalog)

    assert response.source_type == "highlights"
    assert response.anchor is None
    assert 1 <= len(response.results) <= 6


def test_recommendations_by_title_return_anchor_and_results(catalog: AnimeCatalog) -> None:
    response = recommendation_by_title(title="Naruto", limit=6, catalog=catalog)

    assert response.source_type == "title"
    assert response.anchor is not None
    assert response.results
    assert len(response.results) <= 6
    assert all(item.anime_id != response.anchor.anime_id for item in response.results)


def test_recommendations_by_genre_support_aliases(catalog: AnimeCatalog) -> None:
    response = recommendation_by_genre(genre="Shonen", limit=6, catalog=catalog)

    assert response.source_type == "genre"
    assert "Shonen" in response.source_label
    assert response.results
    assert len(response.results) <= 6


def test_recommendations_by_genre_return_404_for_unknown_tag(catalog: AnimeCatalog) -> None:
    with pytest.raises(HTTPException) as error:
        recommendation_by_genre(genre="Space Opera", catalog=catalog)

    assert error.value.status_code == 404
    assert 'No genre named "Space Opera"' in error.value.detail
