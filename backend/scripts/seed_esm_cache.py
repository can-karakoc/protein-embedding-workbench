import argparse
import asyncio
from dataclasses import dataclass

from app.schemas.embedding import EmbeddingRequest
from app.services.embedding_service import embedding_service
from app.services.input_resolver import resolve_sequence


@dataclass(frozen=True)
class SeedProtein:
    accession: str
    label: str


DEFAULT_PROTEINS = [
    SeedProtein("P69905", "Hemoglobin subunit alpha"),
    SeedProtein("P68871", "Hemoglobin subunit beta"),
    SeedProtein("P01308", "Insulin"),
    SeedProtein("P02144", "Myoglobin"),
    SeedProtein("P01112", "KRAS"),
    SeedProtein("P04637", "Cellular tumor antigen p53"),
    SeedProtein("P00734", "Prothrombin"),
    SeedProtein("P0A7V8", "50S ribosomal protein L11"),
]


async def seed_accession(accession: str) -> None:
    sequence, metadata = await resolve_sequence(EmbeddingRequest(accession=accession))
    vector, cache_status = embedding_service.embed(sequence, metadata=metadata)
    print(
        f"{accession}\t{metadata.protein_name or 'unknown'}\t"
        f"{len(sequence)} aa\t{len(vector)} dims\tcache={cache_status}"
    )


async def main(accessions: list[str]) -> None:
    for accession in accessions:
        try:
            await seed_accession(accession)
        except Exception as exc:
            print(f"{accession}\tfailed\t{exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch curated proteins from UniProt and seed the embedding cache."
    )
    parser.add_argument(
        "accessions",
        nargs="*",
        default=[protein.accession for protein in DEFAULT_PROTEINS],
        help="UniProt accessions to embed. Uses a curated demo set by default.",
    )
    args = parser.parse_args()

    asyncio.run(main(args.accessions))
