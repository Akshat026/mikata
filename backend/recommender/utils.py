"""
Loads the two pickle files exactly once when Django starts up.
All views call get_artifacts() which returns the cached objects —
no disk I/O on every request.
"""

import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANIME_PKL  = os.path.join(BASE_DIR, "ml", "artifacts", "anime_list.pkl")
SIM_PKL    = os.path.join(BASE_DIR, "ml", "artifacts", "similarity.pkl")

_anime_df   = None
_similarity = None


def get_artifacts():
    global _anime_df, _similarity

    if _anime_df is None or _similarity is None:
        print("Loading ML artifacts into memory...")
        with open(ANIME_PKL, "rb") as f:
            _anime_df = pickle.load(f)
        with open(SIM_PKL, "rb") as f:
            _similarity = pickle.load(f)
        print(f"Loaded {len(_anime_df)} anime + similarity matrix.")

    return _anime_df, _similarity


def search_anime(query, top_n=10):
    df, _ = get_artifacts()
    query_lower = query.lower()
    mask = df["name"].str.lower().str.contains(query_lower, na=False)
    results = df[mask][["anime_id", "name", "genre", "type", "episodes", "rating"]].head(top_n)
    return results.to_dict(orient="records")


def get_recommendations(anime_name, top_n=10):
    df, similarity = get_artifacts()

    # Find index of the anime (case-insensitive exact match first)
    match = df[df["name"].str.lower() == anime_name.lower()]
    if match.empty:
        # Fall back to partial match
        match = df[df["name"].str.lower().str.contains(anime_name.lower(), na=False)]
    if match.empty:
        return []

    idx = match.index[0]

    # Get similarity scores for this anime against all others
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Skip index 0 (the anime itself), take next top_n
    top_indices = [i for i, _ in sim_scores[1: top_n + 1]]

    results = df.iloc[top_indices][["anime_id", "name", "genre", "type", "episodes", "rating"]]
    return results.to_dict(orient="records")