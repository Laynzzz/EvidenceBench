"""Transactional PostgreSQL/pgvector storage. Exact search suits the pilot corpus."""

from typing import Any

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from evidencebench.retrieval import validate_request
from evidencebench.schemas import ContentUnit, RankedEvidence


class VectorStore:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def import_index(self, fingerprint: str, units: list[ContentUnit], vectors: Any) -> None:
        values = np.asarray(vectors, dtype=np.float32)
        if values.ndim != 2 or len(values) != len(units) or not np.isfinite(values).all():
            raise ValueError("invalid vectors")
        norms = np.linalg.norm(values, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError("zero document embedding")
        values = values / norms
        with psycopg.connect(self.dsn, connect_timeout=5) as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            register_vector(conn)
            conn.execute("""CREATE TABLE IF NOT EXISTS eb_indexes (
                fingerprint text PRIMARY KEY, dimension integer NOT NULL,
                unit_count integer NOT NULL)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS eb_evidence (
                index_id text NOT NULL REFERENCES eb_indexes(fingerprint),
                element_id text NOT NULL, document_id text NOT NULL, family_id text NOT NULL,
                split text NOT NULL, page integer NOT NULL, text text NOT NULL,
                embedding vector NOT NULL, PRIMARY KEY (index_id, element_id))""")
            if conn.execute(
                "SELECT 1 FROM eb_indexes WHERE fingerprint=%s", (fingerprint,)
            ).fetchone():
                raise ValueError("index already exists; immutable imports cannot overwrite")
            conn.execute(
                "INSERT INTO eb_indexes VALUES (%s,%s,%s)",
                (fingerprint, values.shape[1], len(units)),
            )
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO eb_evidence VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    [
                        (
                            fingerprint,
                            u.element_id,
                            u.document_id,
                            u.family_id,
                            u.split,
                            u.page,
                            u.text,
                            vector,
                        )
                        for u, vector in zip(units, values, strict=True)
                    ],
                )

    def search(
        self, fingerprint: str, vector: Any, filters: dict[str, str], k: int
    ) -> list[RankedEvidence]:
        validate_request("", filters, k)
        value = np.asarray(vector, dtype=np.float32)
        if value.ndim != 1 or not np.isfinite(value).all() or np.linalg.norm(value) == 0:
            raise ValueError("invalid query vector")
        with psycopg.connect(
            self.dsn, connect_timeout=5, options="-c statement_timeout=5000"
        ) as conn:
            register_vector(conn)
            row = conn.execute(
                "SELECT dimension FROM eb_indexes WHERE fingerprint=%s", (fingerprint,)
            ).fetchone()
            if not row:
                raise ValueError("missing index")
            if row[0] != value.shape[0]:
                raise ValueError("query dimension mismatch")
            conditions = ["index_id=%s"]
            params: list[Any] = [value, fingerprint]
            for column, expected in sorted(filters.items()):
                # Column is one of the three names validated above; values remain parameters.
                conditions.append(f"{column}=%s")
                params.append(expected)
            params.append(k)
            rows = conn.execute(
                "SELECT element_id, document_id, page, 1 - (embedding <=> %s) AS score "
                "FROM eb_evidence WHERE "
                + " AND ".join(conditions)
                + " ORDER BY score DESC, element_id ASC LIMIT %s",
                params,
            ).fetchall()
        return [
            RankedEvidence(
                element_id=r[0], document_id=r[1], page=r[2], retrieval_score=r[3], rank=i + 1
            )
            for i, r in enumerate(rows)
        ]
