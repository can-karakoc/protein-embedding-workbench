# Project Spec: Protein Embedding Workbench

## Goal

Build a web-accessible computational biology tool where users can enter a UniProt accession or raw protein sequence, retrieve biological metadata, generate protein embeddings, and compare proteins by embedding similarity.

## Why this is hireable

This project demonstrates the rare intersection of:

- backend/API engineering,
- biological database integration,
- protein language models,
- ML inference systems,
- vector similarity search,
- product-oriented scientific tooling.

## MVP scope

### User stories

1. User enters a UniProt accession and retrieves protein name, organism, sequence, and annotations.
2. User enters a sequence/accession and receives a pooled embedding summary.
3. User compares two proteins and gets cosine similarity.
4. User can later view comparisons in a polished web UI.

## Architecture

```txt
Next.js frontend  --->  FastAPI backend  ---> UniProt API
                           |
                           +--> embedding service
                           +--> cache layer
                           +--> comparison service
                           +--> vector index later
```

## Model strategy

Use pretrained models first. Recommended:

- ESM2 small for local development.
- ProtT5/ESM2 larger models later if compute allows.

Do not train a model from scratch for v1. The stronger portfolio signal is production-grade infrastructure, reliable retrieval, evaluation, caching, and biological interpretation.

## Stretch features

- FAISS nearest-neighbor search.
- UMAP visualization.
- GO-term/AlphaFold/PDB enrichment.
- Background worker for long sequences.
- Model benchmarking: ESM2 vs ProtT5 vs simple baseline.
- Mutation embedding-shift analysis.

## Success metric

A recruiter or hiring manager can run the backend, query a real UniProt accession, generate or mock embeddings locally, compare proteins, and understand your engineering decisions from the docs.
