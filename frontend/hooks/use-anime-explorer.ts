"use client";

import { startTransition, useDeferredValue, useEffect, useRef, useState, type KeyboardEvent } from "react";

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

const FEATURED_TITLE_LIMIT = 4;
const SEARCH_DEBOUNCE_MS = 250;

function buildResultsEyebrow(recommendations: RecommendationResponse | null, activeGenre: string | null, searching: boolean) {
  if (searching) {
    return "Updating";
  }

  if (activeGenre) {
    return "Genre browse";
  }

  if (recommendations?.anchor) {
    return "Related picks";
  }

  return "Highlights";
}

function buildResultsCountLabel(resultsCount: number) {
  return resultsCount === 1 ? "1 recommendation" : `${resultsCount} recommendations`;
}

function findActiveGenreDisplay(genres: GenreOption[], activeGenre: string | null) {
  return genres.find((genre) => genre.name === activeGenre)?.display_name ?? activeGenre;
}

export function useAnimeExplorer() {
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
    }, SEARCH_DEBOUNCE_MS);

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

  function resetSuggestions() {
    setSuggestions([]);
    setActiveSuggestionIndex(0);
  }

  function restoreHighlights() {
    manualCommitRef.current = null;
    setActiveGenre(null);
    setQuery("");
    resetSuggestions();
    setIsInputFocused(false);
    setError(null);
    if (highlights) {
      setRecommendations(highlights);
    }
  }

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

  async function loadRecommendationsForTitle(title: string, nextQuery: string = title) {
    manualCommitRef.current = nextQuery.trim();
    setQuery(nextQuery);
    resetSuggestions();
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
    manualCommitRef.current = null;
    setSearching(true);
    setQuery("");
    resetSuggestions();
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

  function handleInputKeyDown(event: KeyboardEvent<HTMLInputElement>) {
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

  function updateQuery(nextQuery: string) {
    setQuery(nextQuery);
    setActiveSuggestionIndex(0);
    setIsInputFocused(true);
  }

  function closeSelectedAnime() {
    setSelectedAnime(null);
  }

  function handleFindSimilarFromModal(title: string) {
    setSelectedAnime(null);
    void loadRecommendationsForTitle(title);
  }

  function handleFeaturedTitleClick(title: string) {
    void loadRecommendationsForTitle(title);
  }

  function handleGenreSelectFromModal(genre: string) {
    setSelectedAnime(null);
    void handleGenreClick(genre);
  }

  const resultsCount = recommendations?.results.length ?? 0;
  const resultsEyebrow = buildResultsEyebrow(recommendations, activeGenre, searching);
  const resultsCountLabel = buildResultsCountLabel(resultsCount);
  const anchorAnime = recommendations?.anchor ?? null;
  const featuredTitles = highlights?.results.slice(0, FEATURED_TITLE_LIMIT) ?? [];
  const activeGenreDisplay = findActiveGenreDisplay(genres, activeGenre);
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

  return {
    activeGenre,
    activeGenreDisplay,
    activeSuggestionIndex,
    anchorAnime,
    apiDocsUrl,
    closeSelectedAnime,
    currentYear,
    detailsLoading,
    error,
    featuredTitles,
    genres,
    getRecommendationReason,
    handleFeaturedTitleClick,
    handleFindSimilarFromModal,
    handleGenreClick,
    handleGenreSelectFromModal,
    handleInputBlur,
    handleInputFocus,
    handleInputKeyDown,
    handleSuggestionClick,
    loading,
    openAnimeDetails,
    query,
    recommendations,
    restoreHighlights,
    resultsCount,
    resultsCountLabel,
    resultsEyebrow,
    searching,
    selectedAnime,
    shouldShowSkeletons,
    shouldShowSuggestions,
    suggestions,
    updateQuery,
  };
}
