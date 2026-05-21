import httpx
from app.schemas.protein import ProteinRecord, ProteinSearchResult

UNIPROT_JSON_URL = "https://rest.uniprot.org/uniprotkb/{accession}.json"

async def fetch_uniprot_record(accession: str) -> ProteinRecord:
    accession = accession.strip()
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(UNIPROT_JSON_URL.format(accession=accession))
        if response.status_code == 404:
            raise ValueError(f"UniProt accession not found: {accession}")
        response.raise_for_status()
        payload = response.json()

    sequence = payload.get("sequence", {}).get("value")
    if not sequence:
        raise ValueError(f"No protein sequence found for accession: {accession}")

    protein_desc = payload.get("proteinDescription", {})
    recommended = protein_desc.get("recommendedName", {})
    protein_name = recommended.get("fullName", {}).get("value")

    organism = payload.get("organism", {}).get("scientificName")
    genes = [g.get("geneName", {}).get("value") for g in payload.get("genes", [])]
    genes = [g for g in genes if g]

    go_terms = []
    for ref in payload.get("uniProtKBCrossReferences", []):
        if ref.get("database") == "GO" and ref.get("id"):
            go_terms.append(ref["id"])

    return ProteinRecord(
        accession=accession,
        protein_name=protein_name,
        organism=organism,
        sequence=sequence,
        sequence_length=len(sequence),
        gene_names=genes,
        go_terms=go_terms,
        source_url=f"https://www.uniprot.org/uniprotkb/{accession}/entry",
    )

SEARCH_URL = "https://rest.uniprot.org/uniprotkb/search"

async def search_uniprot_records(query: str, limit: int = 10) -> list[ProteinSearchResult]:
    if not query:
        raise ValueError("Search query cannot be empty")
    
    query = query.strip()
    params = {
        "query": query,
        "format": "json",
        "size": limit,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(SEARCH_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    results = payload.get("results", [])
    records = []
    for hit in results:
        accession = hit.get("primaryAccession")
        sequence = hit.get("sequence", {}).get("value")
        if not accession or not sequence:
            continue

        protein_desc = hit.get("proteinDescription", {})
        recommended = protein_desc.get("recommendedName", {})
        protein_name = recommended.get("fullName", {}).get("value")

        organism = hit.get("organism", {}).get("scientificName")
        genes = [
            gene.get("geneName", {}).get("value")
            for gene in hit.get("genes", [])
            if gene.get("geneName", {}).get("value")
        ]

        records.append(
            ProteinSearchResult(
                accession=accession,
                protein_name=protein_name,
                organism=organism,
                sequence_length=len(sequence) if sequence else None,
                gene_names=genes,
                reviewed=hit.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
                source_url=f"https://www.uniprot.org/uniprotkb/{accession}/entry",
            )
        )

    return records
