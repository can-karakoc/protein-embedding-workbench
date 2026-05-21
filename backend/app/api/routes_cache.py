from fastapi import APIRouter

from app.schemas.embedding import CacheStatsResponse
from app.services.embedding_cache import embedding_cache
from app.services.embedding_service import embedding_service

router = APIRouter()


@router.get("/stats", response_model=CacheStatsResponse)
async def cache_stats():
    return CacheStatsResponse(
        total_embeddings=embedding_cache.count(
            backend=embedding_service.backend,
            model_name=embedding_service.model_name,
        ),
        backend=embedding_service.backend,
        model_name=embedding_service.model_name,
    )
