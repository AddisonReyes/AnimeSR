import type { AnimeDetail, GenreOption, HealthResponse, RecommendationResponse, SearchResponse } from "@/lib/types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

type QueryParams = Record<string, string | number | undefined>;

function buildApiPath(path: string, params?: QueryParams) {
  if (!params) {
    return path;
  }

  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) {
      searchParams.set(key, String(value));
    }
  }

  const queryString = searchParams.toString();
  return queryString ? `${path}?${queryString}` : path;
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function getFeaturedGenres(limit = 18) {
  return fetchJson<GenreOption[]>(buildApiPath("/api/genres", { limit }));
}

export async function getHealth() {
  return fetchJson<HealthResponse>("/api/health");
}

export async function searchAnime(query: string, limit = 6) {
  return fetchJson<SearchResponse>(buildApiPath("/api/anime/search", { q: query, limit }));
}

export async function getAnimeDetail(animeId: number) {
  return fetchJson<AnimeDetail>(`/api/anime/${animeId}`);
}

export async function getHighlights(limit = 12) {
  return fetchJson<RecommendationResponse>(buildApiPath("/api/recommendations/highlights", { limit }));
}

export async function getRecommendationsByTitle(title: string, limit = 12) {
  return fetchJson<RecommendationResponse>(buildApiPath("/api/recommendations/by-title", { title, limit }));
}

export async function getRecommendationsByGenre(genre: string, limit = 12) {
  return fetchJson<RecommendationResponse>(buildApiPath("/api/recommendations/by-genre", { genre, limit }));
}
