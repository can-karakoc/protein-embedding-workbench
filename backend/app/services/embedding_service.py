import hashlib
import numpy as np
from app.core.config import settings
from app.services.sequence_validation import validate_protein_sequence
from app.services.embedding_cache import embedding_cache

class EmbeddingService:
    def __init__(self):
        self.backend = settings.embedding_backend
        self.model_name = settings.embedding_model_name
        self._model = None
        self._tokenizer = None

    def embed(self, sequence: str, metadata=None) -> tuple[np.ndarray, str]:
        sequence = validate_protein_sequence(sequence, allow_ambiguous=True)
        cache_status = "disabled"

        if settings.enable_embedding_cache:
            cached = embedding_cache.get(
                sequence=sequence,
                backend=self.backend,
                model_name=self.model_name,
            )
            if cached is not None:
                print("[CACHE HIT] Returning cached embedding")
                if metadata is not None:
                    sequence_length = getattr(metadata, "sequence_length", None) or len(sequence)
                    embedding_cache.update_metadata(
                        sequence=sequence,
                        backend=self.backend,
                        model_name=self.model_name,
                        source=getattr(metadata, "source", None),
                        accession=getattr(metadata, "accession", None),
                        protein_name=getattr(metadata, "protein_name", None),
                        organism=getattr(metadata, "organism", None),
                        sequence_length=sequence_length,
                    )
                return cached, "hit"
            cache_status = "miss"
        
        print("[CACHE MISS] Generating new embedding")
        
        if self.backend == "esm":
            vector = self._embed_with_transformers(sequence)
        else:
            vector = self._embed_with_hash_baseline(sequence)

        if settings.enable_embedding_cache:
            sequence_length = getattr(metadata, "sequence_length", None) or len(sequence)
            embedding_cache.set(
                sequence=sequence,
                backend=self.backend,
                model_name=self.model_name,
                vector=vector,
                source=getattr(metadata, "source", None),
                accession=getattr(metadata, "accession", None),
                protein_name=getattr(metadata, "protein_name", None),
                organism=getattr(metadata, "organism", None),
                sequence_length=sequence_length,
            )
        
        return vector, cache_status

    def _embed_with_hash_baseline(self, sequence: str, dim: int = 128) -> np.ndarray:
        """Cheap deterministic placeholder for API/dev/deployment tests.

        This is NOT biologically meaningful. It lets you deploy and test the API
        before paying the compute cost of a real protein language model.
        """
        vector = np.zeros(dim, dtype=np.float32)
        for i, aa in enumerate(sequence):
            digest = hashlib.sha256(f"{i}:{aa}".encode()).digest()
            idx = digest[0] % dim
            sign = 1 if digest[1] % 2 == 0 else -1
            vector[idx] += sign
        norm = np.linalg.norm(vector)
        return vector / norm if norm else vector

    def _embed_with_transformers(self, sequence: str) -> np.ndarray:
        try:
            import torch
            from transformers import AutoTokenizer, AutoModel
        except ImportError as exc:
            raise RuntimeError(
                "Install torch and transformers to use EMBEDDING_BACKEND=esm"
            ) from exc

        if len(sequence) > 1022:
            raise ValueError(
                "Sequence too long for local ESM embedding mode. "
                "Please use a sequence with <= 1022 amino acids for now."
            )

        if self._model is None or self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModel.from_pretrained(self.model_name)
            self._model.eval()

        inputs = self._tokenizer(sequence, return_tensors="pt", truncation=True)

        with torch.no_grad():
            outputs = self._model(**inputs)

        attention_mask = inputs["attention_mask"].squeeze(0)
        token_embeddings = outputs.last_hidden_state.squeeze(0)

        valid_embeddings = token_embeddings[attention_mask == 1]

        if valid_embeddings.shape[0] > 2:
            valid_embeddings = valid_embeddings[1:-1]

        pooled = valid_embeddings.mean(dim=0)

        return pooled.detach().cpu().numpy().astype(np.float32)

embedding_service = EmbeddingService()
