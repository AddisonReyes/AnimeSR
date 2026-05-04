import type { AnimeDetail, GenreOption, HealthResponse, RecommendationResponse, SearchResponse } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

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
  return fetchJson<GenreOption[]>(`/api/genres?limit=${limit}`);
}

export async function getHealth() {
  return fetchJson<HealthResponse>("/api/health");
}

export async function searchAnime(query: string, limit = 6) {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  return fetchJson<SearchResponse>(`/api/anime/search?${params.toString()}`);
}

export async function getAnimeDetail(animeId: number) {
  return fetchJson<AnimeDetail>(`/api/anime/${animeId}`);
}

export async function getHighlights(limit = 12) {
  return fetchJson<RecommendationResponse>(`/api/recommendations/highlights?limit=${limit}`);
}

export async function getRecommendationsByTitle(title: string, limit = 12) {
  const params = new URLSearchParams({ title, limit: String(limit) });
  return fetchJson<RecommendationResponse>(`/api/recommendations/by-title?${params.toString()}`);
}

export async function getRecommendationsByGenre(genre: string, limit = 12) {
  const params = new URLSearchParams({ genre, limit: String(limit) });
  return fetchJson<RecommendationResponse>(`/api/recommendations/by-genre?${params.toString()}`);
}
