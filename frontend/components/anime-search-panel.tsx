import type { KeyboardEvent } from "react";

import type { AnimeSummary, GenreOption } from "@/lib/types";

type AnimeSearchPanelProps = {
  activeGenre: string | null;
  activeSuggestionIndex: number;
  featuredTitles: AnimeSummary[];
  genres: GenreOption[];
  onClear: () => void;
  onFeaturedTitleClick: (title: string) => void;
  onGenreClick: (genre: GenreOption | string) => void;
  onInputBlur: () => void;
  onInputFocus: () => void;
  onInputKeyDown: (event: KeyboardEvent<HTMLInputElement>) => void;
  onQueryChange: (value: string) => void;
  onSuggestionClick: (anime: AnimeSummary) => void;
  query: string;
  shouldShowSuggestions: boolean;
  suggestions: AnimeSummary[];
};

export function AnimeSearchPanel({
  activeGenre,
  activeSuggestionIndex,
  featuredTitles,
  genres,
  onClear,
  onFeaturedTitleClick,
  onGenreClick,
  onInputBlur,
  onInputFocus,
  onInputKeyDown,
  onQueryChange,
  onSuggestionClick,
  query,
  shouldShowSuggestions,
  suggestions,
}: AnimeSearchPanelProps) {
  return (
    <div className="search-box">
      <div className="search-box__row">
        <input
          autoComplete="off"
          className="search-box__input"
          id="anime-search"
          onBlur={onInputBlur}
          onChange={(event) => onQueryChange(event.target.value)}
          onFocus={onInputFocus}
          onKeyDown={onInputKeyDown}
          placeholder="Search for an anime"
          value={query}
        />
        {query || activeGenre ? (
          <button className="search-box__clear" onClick={onClear} type="button">
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
              onClick={() => onSuggestionClick(anime)}
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
              onClick={() => onGenreClick(genre)}
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
                onClick={() => onFeaturedTitleClick(anime.title)}
                type="button"
              >
                {anime.title}
              </button>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
