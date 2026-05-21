# Protein Embedding Workbench

Protein Embedding Workbench is an open-source computational biology web app for retrieving protein records, generating protein embeddings, comparing protein similarity, and searching cached embeddings.

The project is designed as a deployable full-stack bio-AI product: a Next.js frontend, a FastAPI backend, UniProt integration, deterministic demo embeddings for free hosting, optional ESM embeddings for biologically meaningful runs, and a SQLite-backed embedding cache.

## Features

- Retrieve protein metadata and sequences from UniProt.
- Generate protein embeddings from UniProt accessions, protein names, or raw amino-acid sequences.
- Compare two proteins with cosine similarity.
- Search cached embeddings for nearest neighbors.
- Run cheaply in `hash` mode for public demos.
- Enable real ESM embeddings locally or on ML-friendly infrastructure.

## Architecture

```txt
Next.js frontend  --->  FastAPI backend  --->  UniProt API
                           |
                           +--> embedding service
                           +--> SQLite cache
                           +--> similarity search
```

## Monorepo Layout

```txt
protein-embedding-workbench/
  backend/        # FastAPI API: retrieval, embeddings, comparison, search
  frontend/       # Next.js product UI
  worker/         # Placeholder for background embedding jobs
  data/           # Local dev cache only; do not commit generated data
  docs/           # Product, architecture, and deployment notes
```

## Quick Start

Run the backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Run the frontend in another terminal:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open:

```txt
Frontend: http://localhost:3000
API docs: http://127.0.0.1:8000/docs
```

## Useful Endpoints

```txt
GET  /health
GET  /api/proteins/{accession}
GET  /api/proteins/search?query=insulin
POST /api/embeddings
POST /api/compare
POST /api/search/similar
GET  /api/cache/stats
```

## Embedding Modes

`EMBEDDING_BACKEND=hash` is the default. It is deterministic, cheap, and suitable for free public demos, but it is not biologically meaningful.

For real protein language model embeddings:

```bash
cd backend
pip install -r requirements-ml.txt
EMBEDDING_BACKEND=esm uvicorn app.main:app --reload
```

The default ESM model is `facebook/esm2_t6_8M_UR50D`. Local ESM mode currently limits sequences to 1022 amino acids.

## Free Hosting Plan

Recommended public demo:

- Frontend: Vercel Hobby, deployed from `frontend/`.
- Backend: Render free web service, deployed from `backend/`.
- Backend mode: `EMBEDDING_BACKEND=hash`.
- Cache: ephemeral SQLite at `/tmp/protein-cache/embedding_cache.sqlite`.

ML-friendly alternative:

- Frontend: Vercel.
- Backend: Hugging Face Spaces Docker.
- Backend mode: `EMBEDDING_BACKEND=esm` when CPU/RAM limits allow it.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for step-by-step deployment notes.

## Environment Variables

Backend:

```txt
APP_NAME=Protein Embedding Workbench API
ENV=local
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
CACHE_DIR=../data/cache
EMBEDDING_CACHE_PATH=../data/cache/embedding_cache.sqlite
EMBEDDING_BACKEND=hash
EMBEDDING_MODEL_NAME=facebook/esm2_t6_8M_UR50D
ENABLE_EMBEDDING_CACHE=true
```

Frontend:

```txt
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Open Source

This project is licensed under the MIT License. Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
