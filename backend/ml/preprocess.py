import pandas as pd
import numpy as np
import os
import re

RAW_PATH = os.path.join("ml", "data", "raw", "anime-dataset-2023.csv")
PROCESSED_PATH = os.path.join("ml", "data", "processed", "anime_cleaned.csv")


def load_raw_data(path=RAW_PATH):
    df = pd.read_csv(path)
    return df


def clean_data(df):
    # Rename columns to lowercase for consistency
    df = df.rename(columns={
        "Name": "name",
        "English name": "english_name",
        "Score": "score",
        "Genres": "genre",
        "Synopsis": "synopsis",
        "Type": "type",
        "Episodes": "episodes",
        "Members": "members",
        "Image URL": "image_url",
        "Rank": "rank",
        "Popularity": "popularity",
    })

    # Drop rows with no name or genre
    df = df.dropna(subset=["name", "genre"]).copy()

    # Drop rows with Unknown genre
    df = df[df["genre"] != "Unknown"].copy()

    # Clean synopsis — fill missing with empty string
    df["synopsis"] = df["synopsis"].fillna("")
    df["synopsis"] = df["synopsis"].replace("No synopsis information has been added to this title.", "")

    # Clean type
    df["type"] = df["type"].fillna("Unknown")
    df["type"] = df["type"].replace("Unknown", "Unknown")

    # Clean episodes
    df["episodes"] = df["episodes"].replace("Unknown", np.nan)
    df["episodes"] = pd.to_numeric(df["episodes"], errors="coerce")
    df["episodes"] = df["episodes"].fillna(df["episodes"].median())

    # Clean score
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["score"] = df["score"].fillna(df["score"].mean())

    # Clean members
    df["members"] = pd.to_numeric(df["members"], errors="coerce").fillna(0)

    # Remove duplicates
    df = df.drop_duplicates(subset="anime_id").reset_index(drop=True)

    return df


def clean_synopsis(text: str) -> str:
    """Remove source tags like [Written by MAL Rewrite] from synopsis."""
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(Source:.*?\)", "", text)
    return text.strip()


def bucket_episodes(ep):
    if ep <= 1:
        return "movie length"
    elif ep <= 13:
        return "short series"
    elif ep <= 26:
        return "standard series"
    elif ep <= 100:
        return "long running series"
    else:
        return "very long running series"


def build_tags(df):
    df["genre_list"] = df["genre"].apply(
        lambda g: [x.strip() for x in str(g).split(",")]
    )
    df["episode_tag"] = df["episodes"].apply(bucket_episodes)
    df["synopsis_clean"] = df["synopsis"].apply(clean_synopsis)

    # Rich natural language tags combining synopsis + genre + type + episodes
    # Synopsis gives semantic depth, genres give structure
    df["tags"] = df.apply(
        lambda row: (
            f"{row['synopsis_clean']} "
            f"Genre: {', '.join(row['genre_list'])}. "
            f"Type: {row['type']}. "
            f"Length: {row['episode_tag']}."
        ),
        axis=1,
    )

    # Trim tags to 512 chars — MiniLM max token limit
    df["tags"] = df["tags"].str[:512]

    return df


def preprocess():
    print("Loading dataset...")
    df = load_raw_data()
    print(f"Raw data: {len(df)} rows")

    df = clean_data(df)
    print(f"After cleaning: {len(df)} rows")

    df = build_tags(df)

    final_df = df[[
        "anime_id", "name", "english_name", "genre", "type",
        "episodes", "score", "members", "image_url", "tags"
    ]]

    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
    final_df.to_csv(PROCESSED_PATH, index=False)
    print(f"Saved cleaned data to {PROCESSED_PATH} ({len(final_df)} rows)")

    return final_df


if __name__ == "__main__":
    preprocess()