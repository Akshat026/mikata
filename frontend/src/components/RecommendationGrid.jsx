import AnimeCard from "./AnimeCard";

function RecommendationGrid({ title, anime, onSelect, selectedName }) {
  if (!anime || anime.length === 0) return null;

  return (
    <div className="grid-section">
      <h2 className="grid-title">{title}</h2>
      <div className="anime-grid">
        {anime.map((a) => (
          <AnimeCard
            key={a.anime_id}
            anime={a}
            onClick={onSelect}
            isSelected={a.name === selectedName}
          />
        ))}
      </div>
    </div>
  );
}

export default RecommendationGrid;