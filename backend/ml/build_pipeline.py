"""
ml/build_pipeline.py
Orchestrates the full ML pipeline:
  1. preprocess.py  -> cleans anime.csv, builds tags
  2. vectorize.py   -> BoW + cosine similarity -> saves .pkl files

Run this once from the backend/ directory:
  python -m ml.build_pipeline
"""

from ml.preprocess import preprocess
from ml.vectorize  import vectorize


def build():
    print("=" * 50)
    print("STEP 1: Preprocessing")
    print("=" * 50)
    preprocess()

    print()
    print("=" * 50)
    print("STEP 2: Vectorizing + Similarity")
    print("=" * 50)
    vectorize()

    print()
    print("Pipeline complete. Artifacts are ready in ml/artifacts/")


if __name__ == "__main__":
    build()