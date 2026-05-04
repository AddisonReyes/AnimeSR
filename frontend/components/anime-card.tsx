"use client";

import Image from "next/image";

import type { AnimeSummary } from "@/lib/types";

type AnimeCardProps = {
  anime: AnimeSummary;
  reason?: string;
  onClick: (animeId: number) => void;
};

export function AnimeCard({ anime, reason, onClick }: AnimeCardProps) {
  return (
    <button className="anime-card" onClick={() => onClick(anime.anime_id)} type="button">
      <div className="anime-card__poster">
        {anime.image_url ? (
          <Image
            alt={`Cover art for ${anime.title}`}
            className="anime-card__image"
            fill
            sizes="(max-width: 768px) 100vw, 33vw"
            src={anime.image_url}
          />
        ) : (
          <div className="anime-card__fallback">No image available</div>
        )}
      </div>

      <div className="anime-card__content">
        <div className="anime-card__meta">
          <span>{anime.type ?? "Anime"}</span>
          <span>{anime.episodes ? `${anime.episodes} episodes` : "Episodes N/A"}</span>
        </div>

        <h3>{anime.title}</h3>
        {anime.english_name ? <p className="anime-card__subtitle">{anime.english_name}</p> : null}
        {reason ? <p className="anime-card__reason">{reason}</p> : null}
        {anime.short_synopsis ? <p className="anime-card__synopsis">{anime.short_synopsis}</p> : null}

        <div className="anime-card__footer">
          <span className="anime-card__score">{anime.score?.toFixed(2) ?? "N/A"}</span>
          <div className="anime-card__tags">
            {anime.tags.slice(0, 3).map((tag) => (
              <span key={tag}>{tag}</span>
            ))}
          </div>
        </div>
      </div>
    </button>
  );
}
