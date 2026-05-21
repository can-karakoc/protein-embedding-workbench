from app.schemas.embedding import EmbeddingRequest, ResolvedProteinInput
from app.services.sequence_validation import validate_protein_sequence
from app.services.uniprot_client import fetch_uniprot_record, search_uniprot_records


async def _metadata_from_record(record, source: str):
    return ResolvedProteinInput(
        source=source,
        accession=record.accession,
        protein_name=record.protein_name,
        organism=record.organism,
        sequence_length=record.sequence_length,
    )


async def _resolve_by_protein_name(query: str):
    matches = await search_uniprot_records(query=query, limit=1)
    if not matches:
        raise ValueError(f"No UniProt protein found for name: {query}")

    match = matches[0]
    record = await fetch_uniprot_record(match.accession)
    metadata = await _metadata_from_record(record, source=query)
    return record.sequence, metadata

async def resolve_sequence(input_data):
    if input_data.accession:
        try:
            record = await fetch_uniprot_record(input_data.accession)
            metadata = await _metadata_from_record(record, source=input_data.accession)
            return record.sequence, metadata
        except Exception:
            return await _resolve_by_protein_name(input_data.accession)

    if input_data.protein_name:
        return await _resolve_by_protein_name(input_data.protein_name)

    if input_data.sequence:
        sequence = validate_protein_sequence(input_data.sequence)
        metadata = ResolvedProteinInput(
            source="raw_sequence",
            accession=None,
            protein_name=None,
            organism=None,
            sequence_length=len(sequence),
        )
        return sequence, metadata

    raise ValueError("Provide an accession, protein_name, or raw sequence.")
