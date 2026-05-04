"use client";

import Image from "next/image";
import { useEffect } from "react";

import type { AnimeDetail } from "@/lib/types";

type AnimeModalProps = {
  anime: AnimeDetail | null;
  onClose: () => void;
};

function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "N/D";
  }
  return new Intl.NumberFormat("es-DO").format(value);
}

export function AnimeModal({ anime, onClose }: AnimeModalProps) {
  useEffect(() => {
    if (!anime) {
      return undefined;
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [anime, onClose]);

  if (!anime) {
    return null;
  }

  return (
    <div className="anime-modal__backdrop" onClick={onClose} role="presentation">
      <div
        aria-modal="true"
        className="anime-modal"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
      >
        <button className="anime-modal__close" onClick={onClose} type="button">
          Cerrar
        </button>

        <div className="anime-modal__hero">
          <div className="anime-modal__poster">
            {anime.image_url ? (
              <Image
                alt={`Poster de ${anime.title}`}
                className="anime-modal__image"
                fill
                sizes="(max-width: 768px) 100vw, 320px"
                src={anime.image_url}
              />
            ) : (
              <div className="anime-modal__fallback">Sin imagen</div>
            )}
          </div>

          <div className="anime-modal__copy">
            <p className="anime-modal__kicker">{anime.type ?? "Anime"}</p>
            <h2>{anime.title}</h2>
            {anime.english_name ? <p className="anime-modal__subtitle">{anime.english_name}</p> : null}
            {anime.other_name ? <p className="anime-modal__subtitle">{anime.other_name}</p> : null}

            <div className="anime-modal__pill-row">
              {anime.tags.map((tag) => (
                <span key={tag}>{tag}</span>
              ))}
            </div>

            <p className="anime-modal__synopsis">{anime.synopsis ?? anime.short_synopsis ?? "Sin sinopsis disponible."}</p>
          </div>
        </div>

        <div className="anime-modal__meta-grid">
          <div>
            <span>Score</span>
            <strong>{anime.score?.toFixed(2) ?? "N/D"}</strong>
          </div>
          <div>
            <span>Episodios</span>
            <strong>{anime.episodes ?? "N/D"}</strong>
          </div>
          <div>
            <span>Rank</span>
            <strong>{anime.rank ?? "N/D"}</strong>
          </div>
          <div>
            <span>Popularidad</span>
            <strong>{anime.popularity ?? "N/D"}</strong>
          </div>
          <div>
            <span>Miembros</span>
            <strong>{formatNumber(anime.members)}</strong>
          </div>
          <div>
            <span>Favoritos</span>
            <strong>{formatNumber(anime.favorites)}</strong>
          </div>
          <div>
            <span>Votos</span>
            <strong>{formatNumber(anime.scored_by)}</strong>
          </div>
          <div>
            <span>Clasificacion</span>
            <strong>{anime.rating_label ?? "N/D"}</strong>
          </div>
        </div>

        <div className="anime-modal__details">
          <p>
            <span>Estado</span>
            <strong>{anime.status ?? "N/D"}</strong>
          </p>
          <p>
            <span>Emitido</span>
            <strong>{anime.aired ?? "N/D"}</strong>
          </p>
          <p>
            <span>Temporada</span>
            <strong>{anime.premiered ?? "N/D"}</strong>
          </p>
          <p>
            <span>Duracion</span>
            <strong>{anime.duration ?? "N/D"}</strong>
          </p>
          <p>
            <span>Estudios</span>
            <strong>{anime.studios.join(", ") || "N/D"}</strong>
          </p>
          <p>
            <span>Productores</span>
            <strong>{anime.producers.join(", ") || "N/D"}</strong>
          </p>
          <p>
            <span>Licencias</span>
            <strong>{anime.licensors.join(", ") || "N/D"}</strong>
          </p>
          <p>
            <span>Origen</span>
            <strong>{anime.source ?? "N/D"}</strong>
          </p>
        </div>
      </div>
    </div>
  );
}
