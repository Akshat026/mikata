import { useState } from "react";

function SearchBar({ onSearch, loading }) {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) onSearch(input.trim());
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Search anime e.g. Naruto, Death Note..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={loading}
      />
      <button type="submit" disabled={loading || !input.trim()}>
        {loading ? "Searching..." : "Search"}
      </button>
    </form>
  );
}

export default SearchBar;