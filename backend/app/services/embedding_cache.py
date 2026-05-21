import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np

from app.core.config import settings


class EmbeddingCache:
    def __init__(self):
        self.db_path = Path(settings.embedding_cache_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS embedding_cache (
                    sequence_hash TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    source TEXT,
                    accession TEXT,
                    protein_name TEXT,
                    organism TEXT,
                    sequence_length INTEGER,
                    embedding_dim INTEGER NOT NULL,
                    vector_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (sequence_hash, backend, model_name)
                )
                """
            )
            existing_columns = {
                row[1] for row in conn.execute("PRAGMA table_info(embedding_cache)")
            }
            for column, definition in {
                "source": "TEXT",
                "accession": "TEXT",
                "protein_name": "TEXT",
                "organism": "TEXT",
                "sequence_length": "INTEGER",
                "created_at": "TIMESTAMP",
            }.items():
                if column not in existing_columns:
                    conn.execute(
                        f"ALTER TABLE embedding_cache ADD COLUMN {column} {definition}"
                    )

    def sequence_hash(self, sequence: str) -> str:
        normalized = sequence.strip().upper()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def get(self, sequence: str, backend: str, model_name: str) -> np.ndarray | None:
        seq_hash = self.sequence_hash(sequence)

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT vector_json
                FROM embedding_cache
                WHERE sequence_hash = ? AND backend = ? AND model_name = ?
                """,
                (seq_hash, backend, model_name),
            ).fetchone()

        if row is None:
            return None

        return np.array(json.loads(row[0]), dtype=np.float32)

    def count(self, backend: str, model_name: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT COUNT(*)
                FROM embedding_cache
                WHERE backend = ? AND model_name = ?
                """,
                (backend, model_name),
            ).fetchone()

        return int(row[0])

    def list_embeddings(self, backend: str, model_name: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT
                    sequence_hash,
                    source,
                    accession,
                    protein_name,
                    organism,
                    sequence_length,
                    embedding_dim,
                    vector_json,
                    created_at
                FROM embedding_cache
                WHERE backend = ? AND model_name = ?
                """,
                (backend, model_name),
            ).fetchall()

        return [
            {
                "sequence_hash": row[0],
                "source": row[1],
                "accession": row[2],
                "protein_name": row[3],
                "organism": row[4],
                "sequence_length": row[5],
                "embedding_dim": row[6],
                "vector": np.array(json.loads(row[7]), dtype=np.float32),
                "created_at": row[8],
            }
            for row in rows
        ]

    def set(
        self,
        sequence: str,
        backend: str,
        model_name: str,
        vector: np.ndarray,
        source: str | None = None,
        accession: str | None = None,
        protein_name: str | None = None,
        organism: str | None = None,
        sequence_length: int | None = None,
    ) -> None:
        seq_hash = self.sequence_hash(sequence)
        vector_json = json.dumps(vector.astype(float).tolist())

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO embedding_cache
                (
                    sequence_hash,
                    backend,
                    model_name,
                    source,
                    accession,
                    protein_name,
                    organism,
                    sequence_length,
                    embedding_dim,
                    vector_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    seq_hash,
                    backend,
                    model_name,
                    source,
                    accession,
                    protein_name,
                    organism,
                    sequence_length,
                    int(vector.shape[0]),
                    vector_json,
                ),
            )

    def update_metadata(
        self,
        sequence: str,
        backend: str,
        model_name: str,
        source: str | None = None,
        accession: str | None = None,
        protein_name: str | None = None,
        organism: str | None = None,
        sequence_length: int | None = None,
    ) -> None:
        seq_hash = self.sequence_hash(sequence)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE embedding_cache
                SET
                    source = COALESCE(source, ?),
                    accession = COALESCE(accession, ?),
                    protein_name = COALESCE(protein_name, ?),
                    organism = COALESCE(organism, ?),
                    sequence_length = COALESCE(sequence_length, ?)
                WHERE sequence_hash = ? AND backend = ? AND model_name = ?
                """,
                (
                    source,
                    accession,
                    protein_name,
                    organism,
                    sequence_length,
                    seq_hash,
                    backend,
                    model_name,
                ),
            )

embedding_cache = EmbeddingCache()
