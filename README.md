# 味方 Mikata — Anime Recommendation Engine

> **Your ally in anime.** A full-stack ML-powered recommendation system that finds anime similar to what you love, using transformer-based semantic embeddings.

🌐 **Live Demo:** [mikata-anime-recommender.vercel.app](https://mikata-anime-recommender.vercel.app)

---

## Demo

| Search | Recommendations |
|--------|----------------|
| Search for any anime by title | Click a card to get 10 semantically similar recommendations |
| Trending picks on load | Posters fetched via AniList GraphQL API |

---

## How It Works

```
User searches "Naruto"
        ↓
Django REST API queries anime dataset
        ↓
MiniLM-L6-v2 sentence embeddings (384-dim vectors)
        ↓
Cosine similarity → top 10 matches
        ↓
React frontend renders results with AniList posters
```

### ML Pipeline

1. **Data Cleaning** — CooperUnion MyAnimeList dataset (12,232 anime), cleaned with Pandas/NumPy
2. **Feature Engineering** — Genre, type, and episode data transformed into natural language tag strings
3. **Sentence Embeddings** — `all-MiniLM-L6-v2` from Sentence Transformers encodes each anime into a 384-dimensional dense vector
4. **Cosine Similarity** — On-the-fly similarity computed between the queried anime and all others at inference time
5. **Memory Optimization** — Replaced precomputed 1.1GB similarity matrix with 18MB float32 vector store (~99% memory reduction)

---

## Tech Stack

### Machine Learning
| Component | Technology |
|-----------|-----------|
| Embeddings | `sentence-transformers` (MiniLM-L6-v2) |
| Vector dimensions | 384-dim dense vectors |
| Similarity | Cosine similarity (NumPy) |
| Data processing | Pandas, NumPy, Scikit-learn |
| Runtime | CPU-only PyTorch |

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | Django + Django REST Framework |
| API | REST (`/api/search/`, `/api/recommend/`) |
| Deployment | Render (Python 3) |
| Static files | WhiteNoise |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React + TanStack Router |
| Styling | Tailwind CSS |
| Poster images | AniList GraphQL API (batch fetched) |
| Trending data | Jikan API v4 |
| Deployment | Vercel |

---

## Project Structure

```
mikata/
├── backend/
│   ├── anime_backend/          # Django project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── recommender/            # Django app
│   │   ├── views.py            # /search/ and /recommend/ endpoints
│   │   ├── utils.py            # loads artifacts, cosine similarity logic
│   │   └── serializers.py
│   ├── ml/
│   │   ├── data/raw/           # CooperUnion anime.csv
│   │   ├── artifacts/          # anime_list.pkl + vectors.pkl (generated)
│   │   ├── preprocess.py       # cleaning + feature engineering
│   │   ├── vectorize.py        # MiniLM encoding → vectors.pkl
│   │   └── build_pipeline.py   # orchestrates full ML pipeline
│   ├── build.sh                # Render build script
│   └── requirements.txt
└── frontend/
    └── src/
        └── routes/
            └── index.tsx       # entire app — search, grid, recommendations
```

---

## API Endpoints

### Search
```
GET /api/search/?q=naruto
```
```json
{
  "results": [
    {
      "anime_id": 20,
      "name": "Naruto",
      "genre": "Action, Adventure, Comedy",
      "type": "TV",
      "episodes": 220,
      "rating": 7.94
    }
  ]
}
```

### Recommend
```
GET /api/recommend/?name=Naruto
```
```json
{
  "recommendations": [
    {
      "anime_id": 1735,
      "name": "Naruto: Shippuuden",
      "genre": "Action, Adventure, Comedy",
      "type": "TV",
      "episodes": 500,
      "rating": 8.17
    }
  ]
}
```

---

## Running Locally

### Prerequisites
- Python 3.12+
- Node.js 18+
- [CooperUnion anime dataset](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database) — place `anime.csv` in `backend/ml/data/raw/`

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Build ML artifacts (downloads MiniLM model ~90MB, takes ~3 mins)
python -m ml.build_pipeline

# Start Django server
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`

---

## ML Model Details

**Model:** `sentence-transformers/all-MiniLM-L6-v2`
- Lightweight transformer model (22M parameters)
- Produces 384-dimensional sentence embeddings
- Trained on 1B+ sentence pairs
- Maps semantically similar content to nearby vectors in embedding space

**Why sentence embeddings over Bag-of-Words?**

| Approach | Vocabulary | Understanding | Memory |
|----------|-----------|---------------|--------|
| Bag-of-Words | 55 tokens | Keyword matching | 2.5MB vectors + 1.1GB similarity matrix |
| MiniLM Embeddings | Unlimited | Semantic meaning | 18MB vectors, no matrix needed |

Sentence embeddings understand that "action adventure shounen" and "battle fantasy youth" are semantically similar, even with no shared keywords.

---

## Deployment

| Service | Purpose | URL |
|---------|---------|-----|
| **Render** | Django backend + ML inference | Auto-deploys on push to `main` |
| **Vercel** | React frontend | Auto-deploys on push to `main` |

The Render build script (`build.sh`) automatically:
1. Installs CPU-only PyTorch to minimize build size
2. Runs the full ML pipeline to regenerate embeddings
3. Runs Django migrations

---

## Dataset

**Source:** [CooperUnion Anime Recommendations Database](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database)

- 12,232 anime titles after cleaning
- Features used: genre, type (TV/Movie/OVA), episode count
- Transformed into natural language tags for semantic encoding

---

## Author

**Akshat** — [github.com/Akshat026](https://github.com/Akshat026)

---

*Built with Django, React, and Sentence Transformers. Deployed on Render + Vercel.*
