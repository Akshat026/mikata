import pandas as pd
import numpy as np
import os

RAW_PATH = os.path.join("ml", "data", "raw", "anime.csv")
PROCESSED_PATH = os.path.join("ml", "data", "processed", "anime_cleaned.csv")


def load_raw_data(path=RAW_PATH):
    df = pd.read_csv(path)
    return df


def clean_data(df):
    df = df.dropna(subset=["name", "genre"]).copy()
    df["type"] = df["type"].fillna("Unknown")
    df["episodes"] = df["episodes"].replace("Unknown", np.nan)
    df["episodes"] = pd.to_numeric(df["episodes"], errors="coerce")
    df["episodes"] = df["episodes"].fillna(df["episodes"].median())
    df["rating"] = df["rating"].fillna(df["rating"].mean())
    df = df.drop_duplicates(subset="anime_id").reset_index(drop=True)
    return df


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
        lambda g: [x.strip() for x in g.split(",")]
    )
    df["type_tag"] = df["type"]
    df["episode_tag"] = df["episodes"].apply(bucket_episodes)

    # Richer natural language tags — sentence transformers understand phrases
    # Repeat genres twice so they carry more semantic weight
    df["tags"] = df.apply(
        lambda row: (
            f"{' '.join(row['genre_list'])}. "
            f"This is a {row['type_tag']} anime. "
            f"It is a {row['episode_tag']}. "
            f"Genres include {', '.join(row['genre_list'])}."
        ),
        axis=1,
    )

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