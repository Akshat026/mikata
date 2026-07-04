import { useState } from "react";
import SearchBar from "../components/SearchBar";
import RecommendationGrid from "../components/RecommendationGrid";
import Loader from "../components/Loader";
import { searchAnime, getRecommendations } from "../api/animeApi";

function Home() {
  const [searchResults, setSearchResults]       = useState([]);
  const [recommendations, setRecommendations]   = useState([]);
  const [selectedAnime, setSelectedAnime]       = useState(null);
  const [searchLoading, setSearchLoading]       = useState(false);
  const [recLoading, setRecLoading]             = useState(false);
  const [error, setError]                       = useState("");

  const handleSearch = async (query) => {
    setError("");
    setSearchLoading(true);
    setRecommendations([]);
    setSelectedAnime(null);
    try {
      const results = await searchAnime(query);
      setSearchResults(results);
      if (results.length === 0) setError("No anime found for that search.");
    } catch (err) {
      setError("Search failed. Is the backend running?");
    } finally {
      setSearchLoading(false);
    }
  };

  const handleSelectAnime = async (anime) => {
    setError("");
    setSelectedAnime(anime);
    setRecLoading(true);
    try {
      const recs = await getRecommendations(anime.name);
      setRecommendations(recs);
    } catch (err) {
      setError("Could not fetch recommendations.");
    } finally {
      setRecLoading(false);
    }
  };

  return (
    <div className="home">
      <header className="hero">
  <h1 className="hero-title">味方 Mikata</h1>
  <p className="hero-subtitle">
    Your anime ally — search for an anime you love and discover your next obsession.
  </p>
  <SearchBar onSearch={handleSearch} loading={searchLoading} />
</header>

      <main className="main-content">
        {error && <p className="error-msg">{error}</p>}

        {searchLoading && <Loader message="Searching anime..." />}

        {!searchLoading && searchResults.length > 0 && (
          <RecommendationGrid
            title="Search Results — click one to get recommendations"
            anime={searchResults}
            onSelect={handleSelectAnime}
            selectedName={selectedAnime?.name}
          />
        )}

        {recLoading && <Loader message={`Finding anime similar to ${selectedAnime?.name}...`} />}

        {!recLoading && recommendations.length > 0 && (
          <RecommendationGrid
            title={`Because you liked "${selectedAnime?.name}"`}
            anime={recommendations}
            onSelect={handleSelectAnime}
            selectedName={null}
          />
        )}
      </main>
    </div>
  );
}

export default Home;