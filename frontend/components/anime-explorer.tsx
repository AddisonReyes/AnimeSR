"use client";

import { startTransition, useDeferredValue, useEffect, useState } from "react";

import { AnimeCard } from "@/components/anime-card";
import { AnimeModal } from "@/components/anime-modal";
import {
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
  const [suggestions, setSuggestions] = useState<AnimeSummary[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [selectedAnime, setSelectedAnime] = useState<AnimeDetail | null>(null);
  const [activeGenre, setActiveGenre] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
          setRecommendations(highlightResponse);
          setError(null);
        });
      } catch (bootstrapError) {
        if (!cancelled) {
          setError("No pude cargar el catalogo inicial. Revisa que el backend este corriendo.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    if (!deferredQuery) {
      setSuggestions([]);
      return () => {
        cancelled = true;
      };
    }

    const timeoutId = window.setTimeout(async () => {
      setSearching(true);
      try {
        const [searchResponse, recommendationResponse] = await Promise.all([
          searchAnime(deferredQuery),
          getRecommendationsByTitle(deferredQuery),
        ]);

        if (cancelled) {
          return;
        }

        startTransition(() => {
          setSuggestions(searchResponse.results);
          setRecommendations(recommendationResponse);
          setActiveGenre(null);
          setError(null);
        });
      } catch (searchError) {
        if (!cancelled) {
          setSuggestions([]);
          setError("No encontre recomendaciones para esa busqueda todavia.");
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
  }, [deferredQuery]);

  async function openAnimeDetails(animeId: number) {
    setDetailsLoading(true);
    try {
      const anime = await getAnimeDetail(animeId);
      setSelectedAnime(anime);
      setError(null);
    } catch (detailError) {
      setError("No pude cargar el detalle del anime seleccionado.");
    } finally {
      setDetailsLoading(false);
    }
  }

  async function handleGenreClick(genre: GenreOption) {
    setSearching(true);
    setQuery("");
    setSuggestions([]);
    try {
      const response = await getRecommendationsByGenre(genre.name);
      startTransition(() => {
        setRecommendations(response);
        setActiveGenre(genre.name);
        setError(null);
      });
    } catch (genreError) {
      setError("No pude cargar recomendaciones para ese genero.");
    } finally {
      setSearching(false);
    }
  }

  async function handleSuggestionClick(anime: AnimeSummary) {
    setQuery(anime.title);
    setSearching(true);
    try {
      const response = await getRecommendationsByTitle(anime.title);
      startTransition(() => {
        setRecommendations(response);
        setActiveGenre(null);
        setError(null);
      });
    } catch (recommendationError) {
      setError("No pude cargar recomendaciones para ese anime.");
    } finally {
      setSearching(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <div className="hero__grid" />
        <div className="hero__content">
          <p className="hero__eyebrow">Anime Recommendation System</p>
          <h1>Busca un anime, toca un genero y descubre que ver despues.</h1>
          <p className="hero__lede">
            Tomamos la idea del notebook original y la convertimos en una experiencia visual, inmediata y mucho mas
            util para web.
          </p>

          <div className="search-panel">
            <label className="search-panel__label" htmlFor="anime-search">
              Escribe el nombre de un anime
            </label>
            <input
              autoComplete="off"
              className="search-panel__input"
              id="anime-search"
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Naruto, Death Note, One Piece..."
              value={query}
            />

            {query && suggestions.length > 0 ? (
              <div className="search-panel__suggestions">
                {suggestions.map((anime) => (
                  <button
                    className="search-panel__suggestion"
                    key={anime.anime_id}
                    onClick={() => handleSuggestionClick(anime)}
                    type="button"
                  >
                    <span>{anime.title}</span>
                    <small>{anime.tags.slice(0, 3).join(" • ")}</small>
                  </button>
                ))}
              </div>
            ) : null}

            <div className="genre-pills">
              {genres.map((genre) => (
                <button
                  className={activeGenre === genre.name ? "genre-pill genre-pill--active" : "genre-pill"}
                  key={genre.name}
                  onClick={() => handleGenreClick(genre)}
                  type="button"
                >
                  {genre.display_name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="results">
        <div className="results__header">
          <div>
            <p className="results__eyebrow">
              {searching ? "Actualizando recomendaciones..." : "Recomendaciones en tiempo real"}
            </p>
            <h2>{recommendations?.source_label ?? "Cargando catalogo..."}</h2>
          </div>
          {recommendations?.anchor ? (
            <button className="results__anchor" onClick={() => openAnimeDetails(recommendations.anchor!.anime_id)} type="button">
              Ver anime base
            </button>
          ) : null}
        </div>

        {error ? <p className="results__notice">{error}</p> : null}
        {loading ? <p className="results__notice">Preparando el recomendador y leyendo el dataset...</p> : null}
        {detailsLoading ? <p className="results__notice">Cargando ficha completa del anime...</p> : null}

        <div className="results__grid">
          {recommendations?.results.map((anime) => (
            <AnimeCard anime={anime} key={anime.anime_id} onClick={openAnimeDetails} />
          ))}
        </div>
      </section>

      <AnimeModal anime={selectedAnime} onClose={() => setSelectedAnime(null)} />
    </main>
  );
}
