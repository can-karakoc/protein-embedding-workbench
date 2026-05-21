# Contributing

Thanks for contributing to Protein Embedding Workbench.

## Development Setup

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Before Opening a Pull Request

- Keep default backend behavior compatible with free hosting.
- Use `EMBEDDING_BACKEND=hash` for lightweight CI and demo flows.
- Put ML-only dependencies in `backend/requirements-ml.txt`.
- Run backend tests from a clean Python 3.11 or 3.12 environment.
- Run `npm run build` in `frontend/`.
- Update docs when changing API behavior, env vars, or deployment assumptions.

## Scope Guidelines

Good first contributions:

- More sequence validation tests.
- Better API error messages.
- UI polish that preserves the scientific workflow.
- Additional UniProt metadata in responses.
- Persistent cache or vector-store adapters behind a clear interface.

Avoid:

- Training models from scratch in this repo.
- Making heavyweight ML dependencies required for the default free demo.
- Committing generated cache files, databases, model weights, or secrets.
