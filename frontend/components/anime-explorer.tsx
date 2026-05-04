"use client";

import { AnimeFooter } from "@/components/anime-footer";
import { AnimeModal } from "@/components/anime-modal";
import { AnimeResultsSection } from "@/components/anime-results-section";
import { AnimeSearchPanel } from "@/components/anime-search-panel";
import { useAnimeExplorer } from "@/hooks/use-anime-explorer";

export function AnimeExplorer() {
  const {
    activeGenre,
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
    selectedAnime,
    shouldShowSkeletons,
    shouldShowSuggestions,
    suggestions,
    updateQuery,
    activeGenreDisplay,
  } = useAnimeExplorer();

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

        <AnimeSearchPanel
          activeGenre={activeGenre}
          activeSuggestionIndex={activeSuggestionIndex}
          featuredTitles={featuredTitles}
          genres={genres}
          onClear={restoreHighlights}
          onFeaturedTitleClick={handleFeaturedTitleClick}
          onGenreClick={(genre) => void handleGenreClick(genre)}
          onInputBlur={handleInputBlur}
          onInputFocus={handleInputFocus}
          onInputKeyDown={handleInputKeyDown}
          onQueryChange={updateQuery}
          onSuggestionClick={(anime) => void handleSuggestionClick(anime)}
          query={query}
          shouldShowSuggestions={shouldShowSuggestions}
          suggestions={suggestions}
        />
      </section>

      <AnimeResultsSection
        activeGenreDisplay={activeGenreDisplay}
        anchorAnime={anchorAnime}
        detailsLoading={detailsLoading}
        error={error}
        getRecommendationReason={getRecommendationReason}
        loading={loading}
        onAnimeClick={openAnimeDetails}
        onRestoreHighlights={restoreHighlights}
        recommendations={recommendations}
        resultsCount={resultsCount}
        resultsCountLabel={resultsCountLabel}
        resultsEyebrow={resultsEyebrow}
        shouldShowSkeletons={shouldShowSkeletons}
      />

      <AnimeFooter apiDocsUrl={apiDocsUrl} currentYear={currentYear} />

      <AnimeModal
        anime={selectedAnime}
        onClose={closeSelectedAnime}
        onFindSimilar={handleFindSimilarFromModal}
        onSelectGenre={handleGenreSelectFromModal}
      />
    </main>
  );
}
