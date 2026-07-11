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
        print(f"Loaded {len(_anime_df)} anime. Vectors: {_vectors.shape}")
    return _anime_df, _vectors


def cosine_sim_one_vs_all(vectors, idx):
    query_vec  = vectors[idx]
    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0:
        return np.zeros(len(vectors))
    all_norms = np.linalg.norm(vectors, axis=1)
    all_norms[all_norms == 0] = 1e-10
    dot_products = vectors.dot(query_vec)
    return dot_products / (all_norms * query_norm)


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

    match = df[df["name"].str.lower() == anime_name.lower()]
    if match.empty:
        match = df[df["english_name"].str.lower() == anime_name.lower()]
    if match.empty:
        match = df[df["name"].str.lower().str.contains(anime_name.lower(), na=False)]
    if match.empty:
        return []

    idx = match.index[0]
    sim_scores = cosine_sim_one_vs_all(vectors, idx)
    sim_scores[idx] = -1
    top_indices = np.argsort(sim_scores)[::-1][:top_n]
    return _serialize(df.iloc[top_indices])