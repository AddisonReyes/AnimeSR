export type AnimeSummary = {
  anime_id: number;
  title: string;
  english_name: string | null;
  image_url: string | null;
  score: number | null;
  episodes: number | null;
  type: string | null;
  tags: string[];
  short_synopsis: string | null;
};

export type AnimeDetail = AnimeSummary & {
  other_name: string | null;
  synopsis: string | null;
  aired: string | null;
  premiered: string | null;
  status: string | null;
  producers: string[];
  licensors: string[];
  studios: string[];
  source: string | null;
  duration: string | null;
  rating_label: string | null;
  rank: number | null;
  popularity: number | null;
  favorites: number | null;
  scored_by: number | null;
  members: number | null;
};

export type GenreOption = {
  name: string;
  display_name: string;
  count: number;
};

export type RecommendationResponse = {
  source_type: "title" | "genre" | "highlights";
  source_label: string;
  anchor: AnimeSummary | null;
  results: AnimeSummary[];
};

export type SearchResponse = {
  query: string;
  results: AnimeSummary[];
};

export type HealthResponse = {
  status: string;
  total_anime: number;
  total_safe_anime: number;
};
