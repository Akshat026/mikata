import pandas as pd
import pickle
import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

PROCESSED_PATH      = os.path.join("ml", "data", "processed", "anime_cleaned.csv")
ARTIFACTS_DIR       = os.path.join("ml", "artifacts")
ANIME_PKL_PATH      = os.path.join(ARTIFACTS_DIR, "anime_list.pkl")
VECTORS_PKL_PATH    = os.path.join(ARTIFACTS_DIR, "vectors.pkl")


def load_cleaned_data(path=PROCESSED_PATH):
    df = pd.read_csv(path)
    return df


def build_vectors(df):
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(df["tags"]).toarray()

    # Save as float32 to cut memory in half
    vectors = vectors.astype(np.float32)

    print(f"Vocabulary size : {len(cv.vocabulary_)}")
    print(f"Vectors shape   : {vectors.shape}")
    print(f"Vectors size    : {vectors.nbytes / 1024 / 1024:.2f} MB")

    return vectors


def save_artifacts(df, vectors):
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    with open(ANIME_PKL_PATH, "wb") as f:
        pickle.dump(df, f)

    with open(VECTORS_PKL_PATH, "wb") as f:
        pickle.dump(vectors, f)

    print(f"Saved anime_list.pkl -> {ANIME_PKL_PATH}")
    print(f"Saved vectors.pkl    -> {VECTORS_PKL_PATH}")


def vectorize():
    df = load_cleaned_data()
    vectors = build_vectors(df)
    save_artifacts(df, vectors)
    return df, vectors


if __name__ == "__main__":
    vectorize()