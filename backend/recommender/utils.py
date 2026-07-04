"""
Loads vectors once at startup.
Computes cosine similarity on-the-fly for only the queried anime
instead of loading a full 1.1GB precomputed matrix.
"""

import pickle
import os
import numpy as np

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANIME_PKL    = os.path.join(BASE_DIR, "ml", "artifacts", "anime_list.pkl")
VECTORS_PKL  = os.path.join(BASE_DIR, "ml", "artifacts", "vectors.pkl")

_anime_df = None
_vectors  = None


def get_artifacts():
    global _anime_df, _vectors

    if _anime_df is None or _vectors is None:
        print("Loading ML artifacts into memory...")
        with open(ANIME_PKL, "rb") as f:
            _anime_df = pickle.load(f)
        with open(VECTORS_PKL, "rb") as f:
            _vectors = pickle.load(f)
        print(f"Loaded {len(_anime_df)} anime. Vectors shape: {_vectors.shape}")

    return _anime_df, _vectors


def cosine_sim_one_vs_all(vectors, idx):
    """Compute cosine similarity between one anime and all others."""
    query_vec = vectors[idx]                          # shape (55,)
    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0:
        return np.zeros(len(vectors))

    all_norms = np.linalg.norm(vectors, axis=1)       # shape (N,)
    all_norms[all_norms == 0] = 1e-10                 # avoid division by zero

    dot_products = vectors.dot(query_vec)             # shape (N,)
    similarities = dot_products / (all_norms * query_norm)

    return similarities


def search_anime(query, top_n=10):
    df, _ = get_artifacts()
    query_lower = query.lower()
    mask = df["name"].str.lower().str.contains(query_lower, na=False)
    results = df[mask][["anime_id", "name", "genre", "type", "episodes", "rating"]].head(top_n)
    return results.to_dict(orient="records")


def get_recommendations(anime_name, top_n=10):
    df, vectors = get_artifacts()

    match = df[df["name"].str.lower() == anime_name.lower()]
    if match.empty:
        match = df[df["name"].str.lower().str.contains(anime_name.lower(), na=False)]
    if match.empty:
        return []

    idx = match.index[0]

    sim_scores = cosine_sim_one_vs_all(vectors, idx)
    sim_scores[idx] = -1                              # exclude itself

    top_indices = np.argsort(sim_scores)[::-1][:top_n]

    results = df.iloc[top_indices][["anime_id", "name", "genre", "type", "episodes", "rating"]]
    return results.to_dict(orient="records")