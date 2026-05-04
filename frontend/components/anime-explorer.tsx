"use client";

import { startTransition, useDeferredValue, useEffect, useRef, useState } from "react";

import { AnimeCard } from "@/components/anime-card";
import { AnimeModal } from "@/components/anime-modal";
import {
  API_BASE_URL,
  getAnimeDetail,
  getFeaturedGenres,
  getHighlights,
  getRecommendationsByGenre,
  getRecommendationsByTitle,
  searchAnime,
} from "@/lib/api";
import type { AnimeDetail, AnimeSummary, GenreOption, RecommendationResponse } from "@/lib/types";

export function AnimeExplorer() {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query.trim());
  const [genres, setGenres] = useState<GenreOption[]>([]);
  const [highlights, setHighlights] = useState<RecommendationResponse | null>(null);
  const [suggestions, setSuggestions] = useState<AnimeSummary[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [selectedAnime, setSelectedAnime] = useState<AnimeDetail | null>(null);
  const [activeGenre, setActiveGenre] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInputFocused, setIsInputFocused] = useState(false);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(0);
  const manualCommitRef = useRef<string | null>(null);
  const blurTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const [genresResponse, highlightResponse] = await Promise.all([getFeaturedGenres(), getHighlights()]);

        if (cancelled) {
          return;
        }

        startTransition(() => {
          setGenres(genresResponse);
          setHighlights(highlightResponse);
          setRecommendations(highlightResponse);
          setError(null);
        });
      } catch {
        if (!cancelled) {
          setError("Couldn't load the catalog. Make sure the backend is running.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void bootstrap();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    if (!deferredQuery) {
      manualCommitRef.current = null;
      setSuggestions([]);
      setActiveSuggestionIndex(0);
      setError(null);
      if (!activeGenre && highlights) {
        setRecommendations(highlights);
      }
      return () => {
        cancelled = true;
      };
    }

    if (manualCommitRef.current === deferredQuery) {
      manualCommitRef.current = null;
      return () => {
        cancelled = true;
      };
    }

    const timeoutId = window.setTimeout(async () => {
      setSearching(true);
      try {
        const searchResponse = await searchAnime(deferredQuery);

        if (!searchResponse.results.length) {
          if (!cancelled) {
            startTransition(() => {
              setSuggestions([]);
              setActiveSuggestionIndex(0);
              if (!activeGenre && highlights) {
                setRecommendations(highlights);
              }
              setError("No matching anime found for that search yet.");
            });
          }
          return;
        }

        const recommendationResponse = await getRecommendationsByTitle(searchResponse.results[0].title);

        if (cancelled) {
          return;
        }

        startTransition(() => {
          setSuggestions(searchResponse.results);
          setActiveSuggestionIndex(0);
          setRecommendations(recommendationResponse);
          setActiveGenre(null);
          setError(null);
        });
      } catch {
        if (!cancelled) {
          setSuggestions([]);
          setActiveSuggestionIndex(0);
          setError("Couldn't load recommendations for that search.");
        }
      } finally {
        if (!cancelled) {
          setSearching(false);
        }
      }
    }, 250);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [activeGenre, deferredQuery, highlights]);

  useEffect(() => {
    return () => {
      if (blurTimeoutRef.current) {
        window.clearTimeout(blurTimeoutRef.current);
      }
    };
  }, []);

  async function openAnimeDetails(animeId: number) {
    setDetailsLoading(true);
    try {
      const anime = await getAnimeDetail(animeId);
      setSelectedAnime(anime);
      setError(null);
    } catch {
      setError("Couldn't load the selected anime.");
    } finally {
      setDetailsLoading(false);
    }
  }

  function restoreHighlights() {
    manualCommitRef.current = null;
    setActiveGenre(null);
    setQuery("");
    setSuggestions([]);
    setActiveSuggestionIndex(0);
    setIsInputFocused(false);
    setError(null);
    if (highlights) {
      setRecommendations(highlights);
    }
  }

  async function loadRecommendationsForTitle(title: string, nextQuery: string = title) {
    manualCommitRef.current = nextQuery.trim();
    setQuery(nextQuery);
    setSuggestions([]);
    setActiveSuggestionIndex(0);
    setSearching(true);
    try {
      const response = await getRecommendationsByTitle(title);
      startTransition(() => {
        setRecommendations(response);
        setActiveGenre(null);
        setError(null);
      });
    } catch {
      setError("Couldn't load recommendations for that title.");
    } finally {
      setSearching(false);
    }
  }

  async function handleGenreClick(genre: GenreOption | string) {
    const genreName = typeof genre === "string" ? genre : genre.name;
    setSearching(true);
    setQuery("");
    setSuggestions([]);
    setActiveSuggestionIndex(0);
    setIsInputFocused(false);
    try {
      const response = await getRecommendationsByGenre(genreName);
      startTransition(() => {
        setRecommendations(response);
        setActiveGenre(genreName);
        setError(null);
      });
    } catch {
      setError("Couldn't load recommendations for that genre.");
    } finally {
      setSearching(false);
    }
  }

  async function handleSuggestionClick(anime: AnimeSummary) {
    setIsInputFocused(false);
    await loadRecommendationsForTitle(anime.title);
  }

  function handleInputKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (!suggestions.length && event.key === "Enter" && query.trim()) {
      event.preventDefault();
      void loadRecommendationsForTitle(query.trim());
      return;
    }

    if (!suggestions.length) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveSuggestionIndex((current) => (current + 1) % suggestions.length);
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveSuggestionIndex((current) => (current - 1 + suggestions.length) % suggestions.length);
      return;
    }

    if (event.key === "Enter") {
      event.preventDefault();
      const selectedSuggestion = suggestions[activeSuggestionIndex] ?? suggestions[0];
      if (selectedSuggestion) {
        void handleSuggestionClick(selectedSuggestion);
      }
      return;
    }

    if (event.key === "Escape") {
      setIsInputFocused(false);
      setSuggestions([]);
    }
  }

  function handleInputBlur() {
    blurTimeoutRef.current = window.setTimeout(() => {
      setIsInputFocused(false);
    }, 120);
  }

  function handleInputFocus() {
    if (blurTimeoutRef.current) {
      window.clearTimeout(blurTimeoutRef.current);
    }
    setIsInputFocused(true);
  }

  const resultsCount = recommendations?.results.length ?? 0;
  const resultsEyebrow = searching
    ? "Updating"
    : activeGenre
      ? "Genre browse"
      : recommendations?.anchor
        ? "Related picks"
        : "Highlights";
  const resultsCountLabel = resultsCount === 1 ? "1 recommendation" : `${resultsCount} recommendations`;
  const anchorAnime = recommendations?.anchor ?? null;
  const featuredTitles = highlights?.results.slice(0, 4) ?? [];
  const activeGenreDisplay =
    genres.find((genre) => genre.name === activeGenre)?.display_name ??
    (activeGenre ? activeGenre : null);
  const shouldShowSuggestions = isInputFocused && query.trim().length > 0 && suggestions.length > 0;
  const shouldShowSkeletons = loading && !recommendations && !error;
  const currentYear = new Date().getFullYear();
  const apiDocsUrl = `${API_BASE_URL.replace(/\/$/, "")}/docs`;

  function getRecommendationReason(anime: AnimeSummary) {
    if (recommendations?.source_type === "title" && recommendations.anchor) {
      const sharedTags = anime.tags.filter((tag) => recommendations.anchor?.tags.includes(tag)).slice(0, 2);
      return sharedTags.length > 0 ? sharedTags.join(" • ") : null;
    }

    if (recommendations?.source_type === "genre" && activeGenreDisplay) {
      const activeGenreLower = activeGenre?.toLowerCase();
      const matchingTag = anime.tags.find(
        (tag) => tag.toLowerCase() === activeGenreDisplay.toLowerCase() || tag.toLowerCase() === activeGenreLower,
      );
      return matchingTag ?? activeGenreDisplay;
    }

    return null;
  }

  return (
    <main className="page-shell">
      <header className="topbar">
        <div className="topbar__brand">AnimeSR</div>
        {query || activeGenre ? (
          <button className="topbar__reset" onClick={restoreHighlights} type="button">
            Reset
          </button>
        ) : null}
      </header>

      <section className="hero">
        <p className="hero__eyebrow">Anime recommendations</p>
        <div className="hero__header">
          <h1>Find your next anime.</h1>
          <p className="hero__lede">
            Search by title for similar picks, or browse by genre when you want a simpler way to explore.
          </p>
        </div>

        <div className="search-box">
          <div className="search-box__row">
            <input
              autoComplete="off"
              className="search-box__input"
              id="anime-search"
              onBlur={handleInputBlur}
              onChange={(event) => {
                setQuery(event.target.value);
                setActiveSuggestionIndex(0);
                setIsInputFocused(true);
              }}
              onFocus={handleInputFocus}
              onKeyDown={handleInputKeyDown}
              placeholder="Search for an anime"
              value={query}
            />
            {query || activeGenre ? (
              <button className="search-box__clear" onClick={restoreHighlights} type="button">
                Clear
              </button>
            ) : null}
          </div>

          {shouldShowSuggestions ? (
            <div className="search-box__suggestions">
              {suggestions.map((anime, index) => (
                <button
                  className={
                    index === activeSuggestionIndex
                      ? "search-box__suggestion search-box__suggestion--active"
                      : "search-box__suggestion"
                  }
                  key={anime.anime_id}
                  onClick={() => void handleSuggestionClick(anime)}
                  onMouseDown={(event) => event.preventDefault()}
                  type="button"
                >
                  <span>{anime.title}</span>
                  <small>{anime.tags.slice(0, 3).join(" • ")}</small>
                </button>
              ))}
            </div>
          ) : null}

          <div className="hero__genres">
            <p className="hero__section-label">Genres</p>
            <div className="genre-pills">
              {genres.map((genre) => (
                <button
                  className={activeGenre === genre.name ? "genre-pill genre-pill--active" : "genre-pill"}
                  key={genre.name}
                  onClick={() => void handleGenreClick(genre)}
                  type="button"
                >
                  {genre.display_name}
                </button>
              ))}
            </div>
          </div>

          {featuredTitles.length > 0 ? (
            <div className="hero__featured">
              <p className="hero__section-label">Suggested searches</p>
              <div className="hero__featured-list">
                {featuredTitles.map((anime) => (
                  <button
                    className="hero__featured-item"
                    key={anime.anime_id}
                    onClick={() => void loadRecommendationsForTitle(anime.title)}
                    type="button"
                  >
                    {anime.title}
                  </button>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </section>

      <section className="results">
        <div className="results__header">
          <div className="results__summary">
            <p className="results__eyebrow">{resultsEyebrow}</p>
            <h2>{recommendations?.source_label ?? "Loading recommendations..."}</h2>
            <p className="results__meta">
              {resultsCountLabel}
              {activeGenreDisplay ? ` • ${activeGenreDisplay}` : ""}
            </p>
          </div>

          <div className="results__actions">
            {anchorAnime ? (
              <button className="results__action" onClick={() => openAnimeDetails(anchorAnime.anime_id)} type="button">
                Open source anime
              </button>
            ) : null}
          </div>
        </div>

        {error ? <p className="results__notice">{error}</p> : null}
        {loading ? <p className="results__notice">Loading recommendations...</p> : null}
        {detailsLoading ? <p className="results__notice">Loading anime details...</p> : null}

        <div className="results__grid">
          {shouldShowSkeletons
            ? Array.from({ length: 6 }, (_, index) => (
                <div className="anime-card anime-card--skeleton" key={`skeleton-${index}`}>
                  <div className="anime-card__poster" />
                  <div className="anime-card__content">
                    <div className="anime-card__skeleton-line anime-card__skeleton-line--short" />
                    <div className="anime-card__skeleton-line anime-card__skeleton-line--title" />
                    <div className="anime-card__skeleton-line" />
                  </div>
                </div>
              ))
            : recommendations?.results.map((anime) => (
                <AnimeCard
                  anime={anime}
                  key={anime.anime_id}
                  onClick={openAnimeDetails}
                  reason={getRecommendationReason(anime) ?? undefined}
                />
              ))}
        </div>

        {!loading && !error && resultsCount === 0 ? (
          <div className="results__empty">
            <p>No recommendations to show yet.</p>
            <button className="results__action" onClick={restoreHighlights} type="button">
              Back to highlights
            </button>
          </div>
        ) : null}
      </section>

      <footer className="site-footer">
        <div className="site-footer__meta">
          <p className="site-footer__brand">AnimeSR</p>
          <p className="site-footer__copy">© {currentYear} AnimeSR. All rights reserved.</p>
        </div>
        <div className="site-footer__aside">
          <p className="site-footer__backend-line">
            <a href={apiDocsUrl} rel="noreferrer" target="_blank">
              API
            </a>{" "}
            /{" "}
            <a href="https://github.com/AddisonReyes/Anime-System-Recomendations" rel="noreferrer" target="_blank">
              Code
            </a>
          </p>
          <p className="site-footer__credit">
            Made by{" "}
            <a href="https://addisonreyes.com" rel="noreferrer" target="_blank">
              Addison Reyes
            </a>
          </p>
        </div>
      </footer>

      <AnimeModal
        anime={selectedAnime}
        onClose={() => setSelectedAnime(null)}
        onFindSimilar={(title) => {
          setSelectedAnime(null);
          void loadRecommendationsForTitle(title);
        }}
        onSelectGenre={(genre) => {
          setSelectedAnime(null);
          void handleGenreClick(genre);
        }}
      />
    </main>
  );
}
