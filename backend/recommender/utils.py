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

        # Precompute normalized score and popularity once at startup
        global _norm_score, _norm_popularity
        scores = _anime_df["score"].fillna(0).values.astype(np.float32)
        members = _anime_df["members"].fillna(0).values.astype(np.float32)

        _norm_score      = (scores - scores.min()) / (scores.max() - scores.min() + 1e-8)
        _norm_popularity = (members - members.min()) / (members.max() - members.min() + 1e-8)

        print(f"Loaded {len(_anime_df)} anime. Vectors: {_vectors.shape}")
    return _anime_df, _vectors


_norm_score      = None
_norm_popularity = None


def cosine_sim_one_vs_all(vectors, idx):
    query_vec  = vectors[idx]
    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0:
        return np.zeros(len(vectors))
    all_norms = np.linalg.norm(vectors, axis=1)
    all_norms[all_norms == 0] = 1e-10
    dot_products = vectors.dot(query_vec)
    return dot_products / (all_norms * query_norm)


def hybrid_score(sim_scores, weights=(0.6, 0.25, 0.15)):
    """
    Combine three signals into a single ranking score:
      - semantic similarity (MiniLM cosine sim)  → 60%
      - normalized MAL score                     → 25%
      - normalized popularity (members count)    → 15%
    """
    w_sim, w_score, w_pop = weights
    return (
        w_sim   * sim_scores      +
        w_score * _norm_score     +
        w_pop   * _norm_popularity
    )


def _serialize(df_slice):
    records = []
    for _, row in df_slice.iterrows():
        records.append({
            "anime_id":     int(row["anime_id"]),
            "name":         row["name"],
            "english_name": row.get("english_name", None),
            "genre":        row["genre"],
            "type":         row["type"],
            "episodes":     float(row["episodes"]) if row["episodes"] else 0,
            "score":        float(row["score"]) if row["score"] else 0,
            "image_url":    row.get("image_url", None),
        })
    return records


def search_anime(query, top_n=10):
    df, _ = get_artifacts()
    query_lower = query.lower()
    mask = (
        df["name"].str.lower().str.contains(query_lower, na=False) |
        df["english_name"].str.lower().str.contains(query_lower, na=False)
    )
    results = df[mask].head(top_n)
    return _serialize(results)


def get_recommendations(anime_name, top_n=10):
    df, vectors = get_artifacts()

    # Match anime by name
    match = df[df["name"].str.lower() == anime_name.lower()]
    if match.empty:
        match = df[df["english_name"].str.lower() == anime_name.lower()]
    if match.empty:
        match = df[df["name"].str.lower().str.contains(anime_name.lower(), na=False)]
    if match.empty:
        return []

    idx = match.index[0]

    # Step 1 — semantic similarity via MiniLM embeddings
    sim_scores = cosine_sim_one_vs_all(vectors, idx)
    sim_scores[idx] = -1   # exclude the anime itself

    # Step 2 — hybrid scoring: semantic + rating + popularity
    final_scores = hybrid_score(sim_scores)
    final_scores[idx] = -1

    # Step 3 — return top N
    top_indices = np.argsort(final_scores)[::-1][:top_n]
    return _serialize(df.iloc[top_indices])