from app.core.config import settings
from fastapi import APIRouter, HTTPException
from app.schemas.embedding import CompareRequest, CompareResponse
from app.services.embedding_service import embedding_service
from app.services.input_resolver import resolve_sequence
from app.services.comparison_service import cosine_similarity, interpret_similarity

router = APIRouter()

@router.post("", response_model=CompareResponse)
async def compare(req: CompareRequest):
    try:
        left_seq, left_metadata = await resolve_sequence(req.left)
        right_seq, right_metadata = await resolve_sequence(req.right)

        left_vec, left_cache_status = embedding_service.embed(left_seq, metadata=left_metadata)
        right_vec, right_cache_status = embedding_service.embed(right_seq, metadata=right_metadata)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    score = cosine_similarity(left_vec, right_vec)
    backend = settings.embedding_backend

    base_interpretation = interpret_similarity(score)
    is_biologically_meaningful = backend != "hash"

    warning = None
    interpretation = base_interpretation

    if backend == "hash":
        warning = (
            "Hash embeddings are deterministic placeholders for testing API flow only. "
            "Use ESM embeddings for biologically meaningful similarity."
        )
        interpretation = (
            f"{base_interpretation} This result is based on placeholder hash embeddings "
            "and should not be interpreted biologically."
        )

    return CompareResponse(
        left=left_metadata,
        right=right_metadata,
        cosine_similarity=round(score, 6),
        left_cache_status=left_cache_status,
        right_cache_status=right_cache_status,
        interpretation=interpretation,
        embedding_backend=backend,
        warning=warning,
        is_biologically_meaningful=is_biologically_meaningful,
    )
