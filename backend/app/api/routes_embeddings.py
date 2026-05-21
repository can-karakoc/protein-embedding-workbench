from fastapi import APIRouter, HTTPException
from app.schemas.embedding import EmbeddingRequest, EmbeddingResponse
from app.services.embedding_service import embedding_service
from app.services.input_resolver import resolve_sequence

router = APIRouter()

@router.post("", response_model=EmbeddingResponse)
async def create_embedding(req: EmbeddingRequest):
    try:
        sequence, metadata = await resolve_sequence(req)
        vector, cache_status = embedding_service.embed(sequence, metadata=metadata)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return EmbeddingResponse(
        source=metadata.source,
        sequence_length=len(sequence),
        embedding_dim=len(vector),
        cache_status=cache_status,
        embedding_preview=[round(float(x), 6) for x in vector[:8]],
        vector=[float(x) for x in vector] if req.include_vector else None,
        model_name=embedding_service.model_name,
        backend=embedding_service.backend,
    )
