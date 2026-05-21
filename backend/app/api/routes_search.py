from fastapi import APIRouter, HTTPException

from app.schemas.embedding import (
    EmbeddingRequest,
    SimilarSearchMatch,
    SimilarSearchRequest,
    SimilarSearchResponse,
)
from app.services.embedding_cache import embedding_cache
from app.services.embedding_service import embedding_service
from app.services.faiss_search import search_faiss
from app.services.input_resolver import resolve_sequence

router = APIRouter()


@router.post("/similar", response_model=SimilarSearchResponse)
async def search_similar(req: SimilarSearchRequest):
    try:
        sequence, metadata = await resolve_sequence(
            EmbeddingRequest(
                accession=req.accession,
                protein_name=req.protein_name,
                sequence=req.sequence,
            )
        )
        query_vector, cache_status = embedding_service.embed(sequence, metadata=metadata)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    query_hash = embedding_cache.sequence_hash(sequence)
    cached_embeddings = embedding_cache.list_embeddings(
        backend=embedding_service.backend,
        model_name=embedding_service.model_name,
    )
    candidates = [
        item
        for item in cached_embeddings
        if item["sequence_hash"] != query_hash
        and item["embedding_dim"] == int(query_vector.shape[0])
    ]

    if not candidates:
        return SimilarSearchResponse(
            query=metadata,
            query_cache_status=cache_status,
            backend=embedding_service.backend,
            model_name=embedding_service.model_name,
            matches=[],
        )

    nearest = search_faiss(
        query_vector=query_vector,
        candidates=candidates,
        top_k=req.top_k,
    )

    matches = [
        SimilarSearchMatch(
            source=item["source"],
            accession=item["accession"],
            protein_name=item["protein_name"],
            organism=item["organism"],
            sequence_length=item["sequence_length"],
            similarity=round(score, 6),
            created_at=item["created_at"],
        )
        for item, score in nearest
    ]

    return SimilarSearchResponse(
        query=metadata,
        query_cache_status=cache_status,
        backend=embedding_service.backend,
        model_name=embedding_service.model_name,
        matches=matches,
    )
