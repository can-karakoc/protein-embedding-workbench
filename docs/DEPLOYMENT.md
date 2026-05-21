# Deployment Notes

## Recommended Free Architecture

```txt
Frontend: Vercel Hobby, Next.js from frontend/
Backend: Render free web service from backend/
ML mode: hash backend for public demo
Cache: SQLite file in /tmp, accepted as ephemeral on free hosting
Real embeddings: Hugging Face Spaces or a paid/larger backend later
```

The key design choice is to keep Python inference out of Vercel serverless functions. Vercel hosts the interface; the FastAPI service handles UniProt calls, embeddings, caching, and similarity search.

## Option A: Vercel + Render Free

Use this for the first public demo.

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

## Option B: Vercel + Hugging Face Spaces

Use this when the demo needs biologically meaningful ESM embeddings.

Backend setup:

```bash
cd backend
pip install -r requirements-ml.txt
EMBEDDING_BACKEND=esm uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Recommended environment variables:

```txt
ENV=production
CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
CACHE_DIR=/tmp/protein-cache
EMBEDDING_CACHE_PATH=/tmp/protein-cache/embedding_cache.sqlite
EMBEDDING_BACKEND=esm
EMBEDDING_MODEL_NAME=facebook/esm2_t6_8M_UR50D
ENABLE_EMBEDDING_CACHE=true
```

Notes:

- Free CPU Spaces can sleep and may be slow for first model load.
- Keep sequence-length limits visible in the UI/API.
- If ESM inference becomes central, add a background worker and persistent database.

## Option C: Low-Cost Production Upgrade

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
