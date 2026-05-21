from fastapi import APIRouter, HTTPException
from app.schemas.protein import ProteinRecord, ProteinSearchResult
from app.services.uniprot_client import fetch_uniprot_record, search_uniprot_records

router = APIRouter()

# Endpoint to search for proteins based on a query string
@router.get("/search", response_model=list[ProteinSearchResult])
async def search_proteins(query: str, limit: int = 10):
    try:
        return await search_uniprot_records(query=query, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

# Endpoint to retrieve a full protein record by accession number
@router.get("/{accession}")
async def get_protein(accession: str):
    try:
        return await fetch_uniprot_record(accession)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc