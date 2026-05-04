import { AnimeCard } from "@/components/anime-card";
import type { AnimeSummary, RecommendationResponse } from "@/lib/types";

const SKELETON_CARD_COUNT = 6;

type AnimeResultsSectionProps = {
  activeGenreDisplay: string | null;
  anchorAnime: AnimeSummary | null;
  detailsLoading: boolean;
  error: string | null;
  getRecommendationReason: (anime: AnimeSummary) => string | null;
  loading: boolean;
  onAnimeClick: (animeId: number) => void;
  onRestoreHighlights: () => void;
  recommendations: RecommendationResponse | null;
  resultsCount: number;
  resultsCountLabel: string;
  resultsEyebrow: string;
  shouldShowSkeletons: boolean;
};

export function AnimeResultsSection({
  activeGenreDisplay,
  anchorAnime,
  detailsLoading,
  error,
  getRecommendationReason,
  loading,
  onAnimeClick,
  onRestoreHighlights,
  recommendations,
  resultsCount,
  resultsCountLabel,
  resultsEyebrow,
  shouldShowSkeletons,
}: AnimeResultsSectionProps) {
  return (
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
            <button className="results__action" onClick={() => onAnimeClick(anchorAnime.anime_id)} type="button">
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
          ? Array.from({ length: SKELETON_CARD_COUNT }, (_, index) => (
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
                onClick={onAnimeClick}
                reason={getRecommendationReason(anime) ?? undefined}
              />
            ))}
      </div>

      {!loading && !error && resultsCount === 0 ? (
        <div className="results__empty">
          <p>No recommendations to show yet.</p>
          <button className="results__action" onClick={onRestoreHighlights} type="button">
            Back to highlights
          </button>
        </div>
      ) : null}
    </section>
  );
}
