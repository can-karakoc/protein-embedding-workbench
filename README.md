# Protein Embedding Workbench

Protein Embedding Workbench is a personal portfolio project that turns protein language model embeddings into an interactive web product. The app lets users retrieve UniProt proteins, generate ESM2 embeddings, compare proteins by vector similarity, search cached embeddings, and inspect the cache that powers the experience.

This project was built to demonstrate full-stack product engineering at the intersection of computational biology, machine learning infrastructure, and modern web UX.

## Live App

- Hosted app: https://frontend-five-dusky-60.vercel.app
- ESM2 API: https://cankarakoc-protein-embedding-workbench-api.hf.space
- API docs: https://cankarakoc-protein-embedding-workbench-api.hf.space/docs
- GitHub: https://github.com/can-karakoc/protein-embedding-workbench

The hosted API runs on free Hugging Face Space infrastructure, so the first request can be slower while the Space wakes up.

## What Users Can Do

- Generate a protein embedding from a UniProt accession, protein name, or raw amino-acid sequence.
- Use biologically meaningful ESM2 embeddings from `facebook/esm2_t6_8M_UR50D`.
- Compare two proteins and get cosine similarity plus an interpretation of the result.
- Search for nearest neighbors among embeddings already stored in the cache.
- Inspect cache state, including total stored embeddings, backend, and model name.
- Choose whether to return a compact preview or the full embedding vector.
- Try examples such as `P69905`, `P68871`, `insulin`, `hemoglobin`, or a valid protein sequence.

## What's Implemented

### Product Interface

- Next.js single-page workbench with four core workflows: Embed, Compare, Search, and Cache.
- Responsive futuristic light UI with a serif/sans typography system, status strip, model/API/cache pills, and tabbed workspace navigation.
- Client-side API integration against the live FastAPI backend.
- Clear cache hit/miss states and embedding metadata previews.

### Backend API

- FastAPI service with OpenAPI docs.
- UniProt lookup by accession and text search by protein name.
- Input resolver that accepts accessions, protein names, or raw sequences.
- Protein sequence validation before embedding generation.
- Embedding endpoint for vector generation.
- Compare endpoint for cosine similarity between two proteins.
- Similarity search endpoint over cached vectors.
- Cache stats endpoint for observability.

### Embeddings and Search

- ESM2 embedding backend using Hugging Face Transformers.
- Mean-pooled protein embeddings from `facebook/esm2_t6_8M_UR50D`.
- Deterministic hash backend for cheap local or fallback demos.
- SQLite embedding cache keyed by sequence, backend, and model name.
- FAISS-backed nearest-neighbor search when FAISS is available, with NumPy fallback.

### Deployment

- Frontend deployed on Vercel.
- Biologically meaningful backend deployed as a Docker Hugging Face Space.
- Lightweight hash-mode backend also deployable on Vercel as a fallback.
- GitHub Actions CI for frontend and backend checks.

## How Everything Connects

```txt
User
  |
  v
Next.js frontend on Vercel
  |
  |  HTTPS requests
  v
FastAPI backend on Hugging Face Spaces
  |
  +--> UniProt API
  |      resolves accessions, protein names, metadata, and sequences
  |
  +--> ESM2 embedding service
  |      loads facebook/esm2_t6_8M_UR50D with Transformers
  |      validates sequences and returns pooled embedding vectors
  |
  +--> SQLite embedding cache
  |      stores vectors, metadata, model name, backend, and cache status
  |
  +--> FAISS / NumPy similarity search
         searches cached vectors for nearest protein neighbors
```

The frontend is intentionally thin: it manages the workbench UI and sends structured requests to the API. The backend owns biological data retrieval, sequence validation, embedding generation, caching, and vector similarity logic.

## Using the Hosted App

1. Open https://frontend-five-dusky-60.vercel.app.
2. In `Embed`, enter a UniProt accession such as `P69905`, a protein name such as `hemoglobin`, or switch to sequence mode and paste an amino-acid sequence.
3. Click `Generate embedding` to retrieve the protein, run ESM2 inference, and cache the vector.
4. In `Compare`, enter two proteins to calculate cosine similarity between their embeddings.
5. In `Search`, query a protein against the cached embedding store to find nearest neighbors.
6. In `Cache`, inspect how many embeddings are currently stored by the backend.

For the most meaningful results, seed or generate several related proteins first, then use Search against that cached set.

## Tech Stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS v4, lucide-react
- Backend: FastAPI, Pydantic, Uvicorn
- ML: PyTorch, Hugging Face Transformers, ESM2
- Biology data: UniProt REST API
- Vector storage: SQLite
- Similarity search: FAISS with NumPy fallback
- Deployment: Vercel for frontend, Hugging Face Docker Space for ESM2 backend
- Tooling: GitHub Actions, ESLint, pytest, Docker

## Monorepo Layout

```txt
protein-embedding-workbench/
  backend/        FastAPI API, UniProt client, embeddings, cache, search
  frontend/       Next.js workbench UI
  worker/         Placeholder for future background embedding jobs
  data/           Local development cache only
  docs/           Deployment and architecture notes
```

## Local Development

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

To run biologically meaningful ESM2 embeddings locally:

```bash
cd backend
pip install -r requirements-ml.txt
EMBEDDING_BACKEND=esm uvicorn app.main:app --reload
```

The default local backend mode is `hash`, which is deterministic and cheap but not biologically meaningful. Use `EMBEDDING_BACKEND=esm` for real protein language model embeddings.

## Useful API Endpoints

```txt
GET  /health
GET  /api/proteins/{accession}
GET  /api/proteins/search?query=insulin
POST /api/embeddings
POST /api/compare
POST /api/search/similar
GET  /api/cache/stats
```

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

## Limitations and Next Steps

- Free Hugging Face CPU hosting can cold start and may be slow for first ESM2 requests.
- Current ESM mode limits sequences to 1022 amino acids.
- The hosted cache is SQLite on free infrastructure, which is useful for demos but not a durable production vector database.
- Search currently operates over cached/generated proteins rather than a pre-indexed proteome-scale corpus.
- Good next steps would be persistent storage, background embedding jobs, curated protein datasets, richer biological annotations, and a managed vector database.

## License

This project is open source under the MIT License.
