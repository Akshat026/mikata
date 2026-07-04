"""
ml/preprocess.py
Cleans CooperUnion's anime.csv and builds a combined 'tags' feature
for content-based filtering.

Dataset columns expected (anime.csv):
anime_id, name, genre, type, episodes, rating, members
"""

import pandas as pd
import numpy as np
import os

RAW_PATH = os.path.join("ml", "data", "raw", "anime.csv")
PROCESSED_PATH = os.path.join("ml", "data", "processed", "anime_cleaned.csv")


def load_raw_data(path=RAW_PATH):
    df = pd.read_csv(path)
    return df


def clean_data(df):
    # Drop rows with no name or no genre — can't recommend on these
    df = df.dropna(subset=["name", "genre"]).copy()

    # Fill missing type / episodes / rating with safe defaults
    df["type"] = df["type"].fillna("Unknown")
    df["episodes"] = df["episodes"].replace("Unknown", np.nan)
    df["episodes"] = pd.to_numeric(df["episodes"], errors="coerce")
    df["episodes"] = df["episodes"].fillna(df["episodes"].median())
    df["rating"] = df["rating"].fillna(df["rating"].mean())

    # Remove duplicate anime entries by anime_id
    df = df.drop_duplicates(subset="anime_id").reset_index(drop=True)

    return df


def bucket_episodes(ep):
    """Turn episode count into a readable tag instead of a raw number."""
    if ep <= 1:
        return "movie_length"
    elif ep <= 13:
        return "short_series"
    elif ep <= 26:
        return "standard_series"
    elif ep <= 100:
        return "long_series"
    else:
        return "very_long_series"


def build_tags(df):
    # genre column looks like: "Action, Adventure, Comedy"
    df["genre_list"] = df["genre"].apply(
        lambda g: [x.strip().replace(" ", "") for x in g.split(",")]
    )

    df["type_tag"] = df["type"].apply(lambda t: t.replace(" ", ""))
    df["episode_tag"] = df["episodes"].apply(bucket_episodes)

    # Combine everything into one space-separated tag string per anime
    df["tags"] = df.apply(
        lambda row: " ".join(row["genre_list"])
        + " "
        + row["type_tag"]
        + " "
        + row["episode_tag"],
        axis=1,
    )

    df["tags"] = df["tags"].str.lower()

    return df


def preprocess():
    df = load_raw_data()
    df = clean_data(df)
    df = build_tags(df)

    final_df = df[["anime_id", "name", "genre", "type", "episodes", "rating", "members", "tags"]]

    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
    final_df.to_csv(PROCESSED_PATH, index=False)
    print(f"Saved cleaned data to {PROCESSED_PATH} ({len(final_df)} rows)")

    return final_df


if __name__ == "__main__":
    preprocess()