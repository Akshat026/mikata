"""
ml/vectorize.py
Reads the cleaned CSV, builds a Bag-of-Words matrix from the 'tags'
column, computes cosine similarity between all anime, and saves both
the anime dataframe and similarity matrix as pickle files.
"""

import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROCESSED_PATH = os.path.join("ml", "data", "processed", "anime_cleaned.csv")
ARTIFACTS_DIR  = os.path.join("ml", "artifacts")

ANIME_PKL_PATH      = os.path.join(ARTIFACTS_DIR, "anime_list.pkl")
SIMILARITY_PKL_PATH = os.path.join(ARTIFACTS_DIR, "similarity.pkl")


def load_cleaned_data(path=PROCESSED_PATH):
    df = pd.read_csv(path)
    return df


def build_similarity_matrix(df):
    """
    CountVectorizer tokenizes the 'tags' string into individual words
    and builds a word-count matrix of shape (num_anime, vocab_size).
    cosine_similarity then gives us an (num_anime, num_anime) matrix
    where entry [i][j] is how similar anime i is to anime j.
    """
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(df["tags"]).toarray()

    print(f"Vocabulary size  : {len(cv.vocabulary_)}")
    print(f"Vectors shape    : {vectors.shape}")

    similarity = cosine_similarity(vectors)
    print(f"Similarity matrix: {similarity.shape}")

    return similarity


def save_artifacts(df, similarity):
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    with open(ANIME_PKL_PATH, "wb") as f:
        pickle.dump(df, f)

    with open(SIMILARITY_PKL_PATH, "wb") as f:
        pickle.dump(similarity, f)

    print(f"Saved anime_list.pkl   -> {ANIME_PKL_PATH}")
    print(f"Saved similarity.pkl   -> {SIMILARITY_PKL_PATH}")


def vectorize():
    df = load_cleaned_data()
    similarity = build_similarity_matrix(df)
    save_artifacts(df, similarity)
    return df, similarity


if __name__ == "__main__":
    vectorize()