# Deployment Notes

## Recommended Free Architecture

```txt
Frontend: Vercel Hobby, Next.js from frontend/
Backend: Vercel FastAPI function or Render free web service from backend/
ML mode: hash backend for public demo
Cache: SQLite file in /tmp, accepted as ephemeral on free hosting
Real embeddings: Hugging Face Spaces or a paid/larger backend later
```

The key design choice is to keep Python inference out of Vercel serverless functions. Vercel hosts the interface; the FastAPI service handles UniProt calls, embeddings, caching, and similarity search.

## Current Deployment

```txt
Frontend: https://frontend-five-dusky-60.vercel.app
Backend:  https://backend-ochre-five-13.vercel.app
Health:   https://backend-ochre-five-13.vercel.app/health
Docs:     https://backend-ochre-five-13.vercel.app/docs
```

The current backend uses `EMBEDDING_BACKEND=hash`, so similarity scores demonstrate product flow and API behavior, not biological meaning.

## Option A: Vercel Frontend + Vercel FastAPI Backend

This is the fastest no-extra-account free deployment path.

Deploy backend from `backend/`:

```bash
vercel deploy --prod --yes \
  --env APP_NAME="Protein Embedding Workbench API" \
  --env ENV=production \
  --env EMBEDDING_BACKEND=hash \
  --env EMBEDDING_MODEL_NAME=facebook/esm2_t6_8M_UR50D \
  --env CACHE_DIR=/tmp/protein-cache \
  --env EMBEDDING_CACHE_PATH=/tmp/protein-cache/embedding_cache.sqlite \
  --env ENABLE_EMBEDDING_CACHE=true \
  --env CORS_ORIGINS='["https://your-frontend.vercel.app"]'
```

Deploy frontend from `frontend/`:

```bash
vercel deploy --prod --yes \
  --build-env NEXT_PUBLIC_API_BASE_URL=https://your-backend.vercel.app \
  --env NEXT_PUBLIC_API_BASE_URL=https://your-backend.vercel.app
```

Notes:

- Vercel reads `backend/pyproject.toml` to locate `app.main:app` and install lightweight dependencies.
- Do not use this path for heavyweight ESM inference.
- `/tmp` storage is ephemeral.

## Option B: Vercel + Render Free

Use this if you want the Python API on a separate backend host.

### Backend on Render

Deploy `backend/` as a Python web service.

Render settings:

```txt
Root directory: backend
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Plan: Free
```

Environment variables:

```txt
APP_NAME=Protein Embedding Workbench API
ENV=production
CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
CACHE_DIR=/tmp/protein-cache
EMBEDDING_CACHE_PATH=/tmp/protein-cache/embedding_cache.sqlite
EMBEDDING_BACKEND=hash
EMBEDDING_MODEL_NAME=facebook/esm2_t6_8M_UR50D
ENABLE_EMBEDDING_CACHE=true
```

Notes:

- Free Render services can cold start after inactivity.
- `/tmp` storage is not durable. Cached embeddings may disappear after restarts.
- The default `requirements.txt` intentionally excludes `torch`, `transformers`, and `faiss-cpu` to keep deploys lightweight.

### Frontend on Vercel

Deploy `frontend/` as the Vercel project root.

Environment variable:

```txt
NEXT_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com
```

After deployment, update backend `CORS_ORIGINS` to include the final Vercel production URL.

## Option C: Vercel + Hugging Face Spaces

Use this when the demo needs biologically meaningful ESM embeddings.

Hugging Face Docker Spaces use the `sdk: docker` README metadata and expose the app on `app_port`, commonly `7860`. The backend includes `Dockerfile.hf` and `README.hf.md` for this path.

### Create the Space

1. Create a new Hugging Face Space.
2. Choose Docker as the SDK.
3. Put the contents of `backend/` at the root of the Space repository.
4. Rename `Dockerfile.hf` to `Dockerfile`.
5. Rename `README.hf.md` to `README.md`.

Required Space secrets/environment variables:

```txt
ENV=production
CORS_ORIGINS=["https://frontend-five-dusky-60.vercel.app"]
CACHE_DIR=/data/protein-cache
EMBEDDING_CACHE_PATH=/data/protein-cache/embedding_cache.sqlite
EMBEDDING_BACKEND=esm
EMBEDDING_MODEL_NAME=facebook/esm2_t6_8M_UR50D
ENABLE_EMBEDDING_CACHE=true
```

Local backend setup:

```bash
cd backend
pip install -r requirements-ml.txt
EMBEDDING_BACKEND=esm uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Seed a curated ESM cache before demos:

```bash
cd backend
EMBEDDING_BACKEND=esm python scripts/seed_esm_cache.py
```

Point the Vercel frontend at the Space:

```bash
cd frontend
vercel deploy --prod --yes \
  --build-env NEXT_PUBLIC_API_BASE_URL=https://your-space.hf.space \
  --env NEXT_PUBLIC_API_BASE_URL=https://your-space.hf.space
```

Notes:

- Free CPU Spaces can sleep and may be slow for first model load.
- The first ESM request downloads and loads the model, so expect a slow cold start.
- Keep sequence-length limits visible in the UI/API.
- If ESM inference becomes central, add a background worker and persistent database.

## Option D: Low-Cost Production Upgrade

When the demo grows beyond free-tier limits:

- Move the cache from SQLite to Postgres.
- Add a background worker for long embedding jobs.
- Persist vectors in Postgres with pgvector, Qdrant, or another hosted vector store.
- Keep Vercel for the frontend and deploy the backend on a service with stable RAM.

## Preflight Checklist

- `npm run build` passes in `frontend/`.
- Backend tests pass with a clean Python 3.11 or 3.12 virtualenv.
- `/health` returns `status: ok`.
- `/api/embeddings` works with `P69905`.
- `/api/compare` works with `P69905` and `P68871`.
- Frontend `NEXT_PUBLIC_API_BASE_URL` points to the deployed API.
- Backend `CORS_ORIGINS` includes the deployed frontend URL.
