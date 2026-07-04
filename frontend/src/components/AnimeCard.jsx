import { useState, useEffect } from "react";

function AnimeCard({ anime, onClick, isSelected }) {
  const [imageUrl, setImageUrl] = useState(null);
  const [imgLoading, setImgLoading] = useState(true);

  const rating   = anime.rating   ? Number(anime.rating).toFixed(1) : "N/A";
  const episodes = anime.episodes ? Math.round(anime.episodes)       : "?";

  useEffect(() => {
    if (!anime.anime_id) return;

    let cancelled = false;

    const fetchImage = async () => {
      try {
        const res  = await fetch(
          `https://api.jikan.moe/v4/anime/${anime.anime_id}`
        );
        const data = await res.json();
        if (!cancelled) {
          setImageUrl(data?.data?.images?.jpg?.image_url || null);
        }
      } catch {
        if (!cancelled) setImageUrl(null);
      } finally {
        if (!cancelled) setImgLoading(false);
      }
    };

    fetchImage();
    return () => { cancelled = true; };
  }, [anime.anime_id]);

  return (
    <div
      className={`anime-card ${isSelected ? "selected" : ""}`}
      onClick={() => onClick(anime)}
    >
      {/* Poster */}
      <div className="anime-poster">
        {imgLoading ? (
          <div className="poster-skeleton" />
        ) : imageUrl ? (
          <img src={imageUrl} alt={anime.name} className="poster-img" />
        ) : (
          <div className="poster-fallback">🎌</div>
        )}
      </div>

      {/* Info */}
      <div className="anime-info">
        <div className="anime-card-header">
          <h3 className="anime-title">{anime.name}</h3>
          <span className={`anime-type type-${anime.type?.toLowerCase()}`}>
            {anime.type || "Unknown"}
          </span>
        </div>
        <p className="anime-genre">{anime.genre}</p>
        <div className="anime-meta">
          <span>⭐ {rating}</span>
          <span>📺 {episodes} eps</span>
        </div>
      </div>
    </div>
  );
}

export default AnimeCard;