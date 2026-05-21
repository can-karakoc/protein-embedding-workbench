---
title: Protein Embedding Workbench API
sdk: docker
app_port: 7860
---

# Protein Embedding Workbench API

FastAPI backend for Protein Embedding Workbench running with ESM2 embeddings.

Expected environment variables:

```txt
ENV=production
CORS_ORIGINS=["https://frontend-five-dusky-60.vercel.app"]
CACHE_DIR=/data/protein-cache
EMBEDDING_CACHE_PATH=/data/protein-cache/embedding_cache.sqlite
EMBEDDING_BACKEND=esm
EMBEDDING_MODEL_NAME=facebook/esm2_t6_8M_UR50D
ENABLE_EMBEDDING_CACHE=true
```

Health check:

```txt
/health
```

API docs:

```txt
/docs
```
