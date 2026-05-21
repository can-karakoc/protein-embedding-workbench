from pydantic import BaseModel, Field

class EmbeddingRequest(BaseModel):
    accession: str | None = Field(default=None, description="UniProt accession, e.g. P69905")
    protein_name: str | None = Field(default=None, description="Protein name search term, e.g. insulin")
    sequence: str | None = Field(default=None, description="Raw amino-acid sequence")
    include_vector: bool = Field(default=False, description="Return full embedding vector. Keep false for UI responses.")

class EmbeddingResponse(BaseModel):
    source: str
    sequence_length: int
    embedding_dim: int
    cache_status: str
    embedding_preview: list[float]
    vector: list[float] | None = None
    model_name: str
    backend: str

class CompareRequest(BaseModel):
    left: EmbeddingRequest
    right: EmbeddingRequest

class ResolvedProteinInput(BaseModel):
    source: str
    accession: str | None = None
    protein_name: str | None = None
    organism: str | None = None
    sequence_length: int

class CompareResponse(BaseModel):
    left: ResolvedProteinInput
    right: ResolvedProteinInput
    cosine_similarity: float
    left_cache_status: str
    right_cache_status: str
    interpretation: str
    embedding_backend: str
    is_biologically_meaningful: bool
    warning: str | None = None

class CacheStatsResponse(BaseModel):
    total_embeddings: int
    backend: str
    model_name: str

class SimilarSearchRequest(BaseModel):
    accession: str | None = Field(default=None, description="UniProt accession, e.g. P69905")
    protein_name: str | None = Field(default=None, description="Protein name search term, e.g. insulin")
    sequence: str | None = Field(default=None, description="Raw amino-acid sequence")
    top_k: int = Field(default=5, ge=1, le=100)

class SimilarSearchMatch(BaseModel):
    source: str | None = None
    accession: str | None = None
    protein_name: str | None = None
    organism: str | None = None
    sequence_length: int | None = None
    similarity: float
    created_at: str | None = None

class SimilarSearchResponse(BaseModel):
    query: ResolvedProteinInput
    query_cache_status: str
    backend: str
    model_name: str
    matches: list[SimilarSearchMatch]
