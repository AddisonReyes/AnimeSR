"use client";

import Image from "next/image";
import { useEffect } from "react";

import type { AnimeDetail } from "@/lib/types";

type AnimeModalProps = {
  anime: AnimeDetail | null;
  onClose: () => void;
  onFindSimilar: (title: string) => void;
  onSelectGenre: (genre: string) => void;
};

function compactList(items: string[], limit = 2) {
  if (!items.length) {
    return null;
  }

  if (items.length <= limit) {
    return items.join(", ");
  }

  return `${items.slice(0, limit).join(", ")} +${items.length - limit} more`;
}

export function AnimeModal({ anime, onClose, onFindSimilar, onSelectGenre }: AnimeModalProps) {
  useEffect(() => {
    if (!anime) {
      return undefined;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleEscape);
    };
  }, [anime, onClose]);

  if (!anime) {
    return null;
  }

  const primaryGenre = anime.tags[0] ?? null;
  const alternateTitle = anime.english_name || anime.other_name || null;
  const metaFacts = [
    { label: "Season", value: anime.premiered },
    { label: "Studio", value: compactList(anime.studios) },
    { label: "Source", value: anime.source },
    { label: "Duration", value: anime.duration },
  ].filter((item) => item.value);

  return (
    <div className="anime-modal__backdrop" onClick={onClose} role="presentation">
      <div
        aria-modal="true"
        aria-label={`Details for ${anime.title}`}
        className="anime-modal"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
      >
        <button className="anime-modal__close" onClick={onClose} type="button">
          Close
        </button>

        <div className="anime-modal__hero">
          <div className="anime-modal__poster">
            {anime.image_url ? (
              <Image
                alt={`Cover art for ${anime.title}`}
                className="anime-modal__image"
                fill
                sizes="(max-width: 768px) 100vw, 320px"
                src={anime.image_url}
              />
            ) : (
              <div className="anime-modal__fallback">No image available</div>
            )}
          </div>

          <div className="anime-modal__copy">
            <p className="anime-modal__kicker">{anime.type ?? "Anime"}</p>
            <h2>{anime.title}</h2>
            {alternateTitle ? <p className="anime-modal__subtitle">{alternateTitle}</p> : null}

            <div className="anime-modal__pill-row">
              {anime.tags.map((tag) => (
                <button className="anime-modal__tag" key={tag} onClick={() => onSelectGenre(tag)} type="button">
                  {tag}
                </button>
              ))}
            </div>

            <div className="anime-modal__stats">
              <div>
                <span>Score</span>
                <strong>{anime.score?.toFixed(2) ?? "N/A"}</strong>
              </div>
              <div>
                <span>Episodes</span>
                <strong>{anime.episodes ?? "N/A"}</strong>
              </div>
              <div>
                <span>Status</span>
                <strong>{anime.status ?? "N/A"}</strong>
              </div>
            </div>

            <p className="anime-modal__synopsis">
              {anime.synopsis ?? anime.short_synopsis ?? "No synopsis available."}
            </p>

            <div className="anime-modal__actions">
              <button
                className="anime-modal__action anime-modal__action--primary"
                onClick={() => onFindSimilar(anime.title)}
                type="button"
              >
                Find similar titles
              </button>
              {primaryGenre ? (
                <button className="anime-modal__action" onClick={() => onSelectGenre(primaryGenre)} type="button">
                  Explore {primaryGenre}
                </button>
              ) : null}
            </div>
            {metaFacts.length ? (
              <div className="anime-modal__facts">
                {metaFacts.map((fact) => (
                  <p key={fact.label}>
                    <span>{fact.label}</span>
                    <strong>{fact.value}</strong>
                  </p>
                ))}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
