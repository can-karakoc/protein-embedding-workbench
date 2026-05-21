from pydantic import BaseModel, Field

# Full protein record with all details
class ProteinRecord(BaseModel):
    accession: str
    protein_name: str | None = None
    organism: str | None = None
    sequence: str
    sequence_length: int
    gene_names: list[str] = Field(default_factory=list)
    go_terms: list[str] = Field(default_factory=list)
    source_url: str | None = None

# Simplified search result without sequence
class ProteinSearchResult(BaseModel):
    accession: str
    protein_name: str | None = None
    organism: str | None = None
    sequence_length: int | None = None
    gene_names: list[str] = Field(default_factory=list)
    reviewed: bool | None = None
    source_url: str | None = None