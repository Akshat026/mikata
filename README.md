# 味方 Mikata — Anime Recommendation Engine

> **Your ally in anime.** A full-stack ML-powered recommendation system that finds anime similar to what you love, using transformer-based semantic embeddings and hybrid scoring.

🌐 **Live Demo:** [mikata-anime-recommender.vercel.app](https://mikata-anime-recommender.vercel.app)  
👤 **Author:** [github.com/Akshat026](https://github.com/Akshat026)

---

## How It Works

```
User searches "Frieren"
        ↓
Django REST API queries 24,900+ anime dataset
        ↓
User clicks an anime card
        ↓
MiniLM-L6-v2 computes 384-dim semantic embedding
        ↓
Cosine similarity across all anime vectors
        ↓
Hybrid scoring: 60% semantic + 25% MAL rating + 15% popularity
        ↓
Top 10 recommendations returned
        ↓
React frontend fetches posters via AniList GraphQL API
```

---

## ML Pipeline

### 1. Data Collection
- **Dataset:** [dbdmobile's MyAnimeList Dataset 2023](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset)
- **Size:** 24,905 anime after cleaning (up from 12,232 in CooperUnion's 2017 dataset)
- **Coverage:** Includes modern anime like Frieren, Vinland Saga, Attack on Titan, and all titles up to 2023

### 2. Feature Engineering
Each anime is converted into a rich natural language description combining multiple signals:

```python
tags = f"""
{synopsis}
Genre: {genres}.
Type: {type}.
Length: {episode_bucket}.
"""
```

Synopses are cleaned (removing MAL editorial tags), and episode counts are bucketed into semantic labels (`short series`, `standard series`, `long running series`) rather than raw numbers.

### 3. Sentence Embeddings (MiniLM-L6-v2)
Each tag string is encoded by `sentence-transformers/all-MiniLM-L6-v2`:

- **22M parameter** transformer model
- Produces **384-dimensional dense vectors**
- Trained on **1B+ sentence pairs**
- Understands semantic meaning — "battle" and "fight" are treated as similar even with no shared keywords
- Total vector store: **~36MB** (float32)

### 4. Hybrid Recommendation Scoring
When a user selects an anime, the system computes a hybrid score combining three signals:

```python
final_score = (
    0.60 * cosine_similarity(query_vec, all_vecs) +  # semantic match
    0.25 * normalized_mal_score                     +  # community rating
    0.15 * normalized_popularity                       # member count
)
```

This balances **relevance** (semantic similarity) with **quality** (MAL rating) and **popularity** (member count), ensuring well-known high-quality anime rank above obscure but technically similar ones.

### 5. Memory Optimization
Instead of precomputing a full similarity matrix (which would be 24,905 × 24,905 × 4 bytes = **~2.5GB**), similarity is computed on-the-fly for only the queried anime at inference time. This keeps the server well within Render's free tier memory limits.

---

## Tech Stack

### Machine Learning
| Component | Technology |
|-----------|-----------|
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) |
| Vector dimensions | 384-dim dense vectors |
| Similarity | Cosine similarity (NumPy) |
| Scoring | Hybrid: semantic + rating + popularity |
| Data processing | Pandas, NumPy, Scikit-learn |
| Runtime | CPU-only PyTorch |

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | Django + Django REST Framework |
| Endpoints | `GET /api/search/`, `GET /api/recommend/` |
| Deployment | Render (Python 3, Singapore region) |
| Static files | WhiteNoise |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React + TanStack Router (Vite) |
| Styling | Tailwind CSS |
| Poster images | AniList GraphQL API (batch fetched, 50 IDs/request) |
| Trending data | Jikan API v4 (with 3-retry fallback) |
| Deployment | Vercel |

---

## Project Structure

```
mikata/
├── backend/
│   ├── anime_backend/              # Django project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── recommender/                # Django REST app
│   │   ├── views.py                # /search/ and /recommend/ endpoints
│   │   ├── utils.py                # ML inference + hybrid scoring
│   │   └── serializers.py
│   ├── ml/
│   │   ├── data/
│   │   │   ├── raw/                # anime-dataset-2023.csv (Kaggle)
│   │   │   └── processed/          # anime_cleaned.csv (generated)
│   │   ├── artifacts/              # anime_list.pkl + vectors.pkl (generated)
│   │   ├── preprocess.py           # cleaning + feature engineering
│   │   ├── vectorize.py            # MiniLM encoding → vectors.pkl
│   │   └── build_pipeline.py       # orchestrates full ML pipeline
│   ├── build.sh                    # Render build script
│   └── requirements.txt
└── frontend/
    └── src/
        └── routes/
            └── index.tsx           # search, grid, recommendations, trending
```

---

## API Reference

### Search
```
GET /api/search/?q=frieren
```
```json
{
  "results": [
    {
      "anime_id": 52991,
      "name": "Sousou no Frieren",
      "english_name": "Frieren: Beyond Journey's End",
      "genre": "Adventure, Drama, Fantasy",
      "type": "TV",
      "episodes": 28,
      "score": 9.09
    }
  ]
}
```

### Recommend
```
GET /api/recommend/?name=Sousou no Frieren
```
```json
{
  "recommendations": [
    {
      "anime_id": 38000,
      "name": "Mushishi Zoku Shou",
      "english_name": "Mushishi: Next Passage",
      "genre": "Adventure, Fantasy, Mystery",
      "type": "TV",
      "episodes": 10,
      "score": 8.73
    }
  ]
}
```

---

## Running Locally

### Prerequisites
- Python 3.12+
- Node.js 18+
- [dbdmobile's MyAnimeList Dataset 2023](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset) — place `anime-dataset-2023.csv` in `backend/ml/data/raw/`

### Backend

```bash
cd backend

# Install dependencies (CPU-only torch to save space)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Build ML artifacts
# Downloads MiniLM model (~90MB), encodes 24,905 anime (~3 mins)
python -m ml.build_pipeline

# Start server
python manage.py migrate
python manage.py runserver
```

API available at `http://localhost:8000/api/`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:3000`

---

## Deployment

| Service | Hosts | Auto-deploys on |
|---------|-------|----------------|
| **Render** | Django backend + ML inference | Push to `main` |
| **Vercel** | React frontend | Push to `main` |

The Render `build.sh` script automatically installs CPU-only PyTorch, runs the full ML pipeline (downloading and encoding all anime), and runs Django migrations on every deploy.

---

## ML Design Decisions

### Why MiniLM over Bag-of-Words?

| | Bag-of-Words (old) | MiniLM Embeddings (current) |
|--|--|--|
| Vocabulary | 55 genre tokens | Unlimited — full synopsis text |
| Understanding | Keyword overlap | Semantic meaning |
| "battle" ≈ "fight"? | No | Yes |
| Vector size | 2.5MB | 36MB |
| Precomputed matrix | 1.1GB | Not needed |
| Dataset coverage | 12,232 anime (2017) | 24,905 anime (2023) |

### Why hybrid scoring?
Pure cosine similarity sometimes surfaces obscure but technically similar anime over well-known quality titles. By blending in MAL community scores and member counts, recommendations feel more curated and trustworthy — similar to how Netflix balances personalization with editorial quality signals.

### Why on-the-fly similarity?
Precomputing a full 24,905 × 24,905 similarity matrix would require ~2.5GB of memory, far exceeding Render's free tier limit of 512MB. Computing similarity only for the queried anime at request time keeps memory usage under 100MB with sub-100ms response times.

---

## External APIs Used

| API | Purpose | Auth |
|-----|---------|------|
| [Jikan v4](https://jikan.moe/) | Trending anime on homepage | None |
| [AniList GraphQL](https://anilist.gitbook.io/anilist-apiv2-docs/) | Batch poster image fetching | None |
| Your Django API | Search + recommendations | None |

All APIs are free with no keys required.

---

## Dataset

**Source:** [dbdmobile — MyAnimeList Dataset 2023](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset)

| Field | Used for |
|-------|---------|
| `Synopsis` | Primary embedding input — semantic meaning |
| `Genres` | Secondary embedding input + display |
| `Type` | Tertiary embedding input (TV/Movie/OVA) |
| `Episodes` | Episode bucket tag + display |
| `Score` | Hybrid scoring — quality signal |
| `Members` | Hybrid scoring — popularity signal |
| `anime_id` | MAL ID for AniList poster lookup |

---

*Built with Django, React, Sentence Transformers, and deployed on Render + Vercel.*
