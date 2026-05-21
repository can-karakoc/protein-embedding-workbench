from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_proteins import router as proteins_router
from app.api.routes_embeddings import router as embeddings_router
from app.api.routes_compare import router as compare_router
from app.api.routes_cache import router as cache_router
from app.api.routes_search import router as search_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name, "embedding_backend": settings.embedding_backend}

app.include_router(proteins_router, prefix="/api/proteins", tags=["proteins"])
app.include_router(embeddings_router, prefix="/api/embeddings", tags=["embeddings"])
app.include_router(compare_router, prefix="/api/compare", tags=["compare"])
app.include_router(cache_router, prefix="/api/cache", tags=["cache"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
