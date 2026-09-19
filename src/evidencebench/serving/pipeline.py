"""Shared fixed inference pipeline; release configuration is validated at startup."""

import os
import time
from pathlib import Path

import yaml
from dotenv import load_dotenv

from evidencebench.generation import PROMPT_VERSION, LocalGenerator
from evidencebench.pipelines import load_retrievers
from evidencebench.reranking import RerankingRetriever, load_cross_encoder
from evidencebench.retrieval import HybridRetriever
from evidencebench.storage import VectorStore


class FixedPipeline:
    def __init__(self, units, retriever, generator, config, versions, healthcheck=lambda: True):
        self.lookup = {u.element_id: u for u in units}
        self.retriever, self.generator = retriever, generator
        self.config, self.versions, self.healthcheck = config, versions, healthcheck

    def ready(self):
        return self.healthcheck()

    def retrieve(self, query, filters, k):
        started = time.perf_counter()
        hits = self.retriever.retrieve(query, filters, k)
        evidence = [
            {
                **h.model_dump(mode="json"),
                "text": self.lookup[h.element_id].text,
                "page_end": self.lookup[h.element_id].page_end,
                "source_url": str(self.lookup[h.element_id].source_url),
            }
            for h in hits
        ]
        return {
            "status": "ok",
            "evidence": evidence,
            "versions": self.versions,
            "timings": {"retrieval_rerank_ms": (time.perf_counter() - started) * 1000},
        }

    def ask(self, query, filters):
        self.last_trace = {}
        started = time.perf_counter()
        retrieved = self.retrieve(query, filters, self.config["context_passages"])
        evidence = retrieved["evidence"]
        timings = retrieved["timings"]
        if (
            not evidence
            or (
                evidence[0]["reranker_score"]
                if evidence[0]["reranker_score"] is not None
                else evidence[0]["retrieval_score"]
            )
            < self.config["refusal_threshold"]
        ):
            return {
                "status": "refused",
                "reason": "insufficient_evidence",
                "answer": "",
                "citations": [],
                "versions": self.versions,
                "timings": timings,
            }
        packed = {
            f"E{i + 1}": h["text"][: self.config["passage_characters"]]
            for i, h in enumerate(evidence)
        }
        tick = time.perf_counter()
        answer = self.generator.generate(query, packed)
        self.last_trace = {
            "packed_evidence": packed,
            "raw_generation": getattr(self.generator, "last_output", None),
        }
        timings["generation_ms"] = (time.perf_counter() - tick) * 1000
        citations = []
        for key in answer.pop("evidence_ids", []):
            hit = evidence[int(key[1:]) - 1]
            unit = self.lookup[hit["element_id"]]
            citations.append(
                {
                    "element_id": unit.element_id,
                    "document_id": unit.document_id,
                    "page": unit.page,
                    "page_end": unit.page_end or unit.page,
                    "source_url": str(unit.source_url),
                    "bbox": unit.bbox,
                    "section": unit.section,
                    "reranker_score": hit["reranker_score"],
                }
            )
        timings["total_ms"] = (time.perf_counter() - started) * 1000
        return {**answer, "citations": citations, "versions": self.versions, "timings": timings}


def load_runtime(path: Path, database: bool = True):
    release = yaml.safe_load(path.read_text("utf-8"))
    retrieval, reranker, generation = (
        release["retrieval"],
        release["reranker"],
        release["generation"],
    )
    if generation["prompt_version"] != PROMPT_VERSION:
        raise ValueError("release prompt version mismatch")
    units, retrievers, metadata = load_retrievers(retrieval)
    if (
        metadata["fingerprint"] != release["corpus_fingerprint"]
        or metadata["index_fingerprint"] != release["index_fingerprint"]
    ):
        raise ValueError("release data/index fingerprint mismatch")
    hybrid = retrievers["hybrid"]

    def healthcheck():
        return True

    if database:
        load_dotenv()
        dsn = os.environ[retrieval["database_url_env"]]
        store = VectorStore(dsn)
        encode = retrievers["dense"].encode_query

        class DatabaseRetriever:
            def retrieve(self, query, filters, k):
                return store.search(metadata["index_fingerprint"], encode(query), filters, k)

        hybrid = HybridRetriever(retrievers["bm25"], DatabaseRetriever(), retrieval["candidate_k"])

        def healthcheck():
            return store.ready(metadata["index_fingerprint"], len(units))

        if not healthcheck():
            raise ValueError("database index is missing or incomplete")

    ranker = RerankingRetriever(
        hybrid, units, load_cross_encoder(reranker), retrieval["candidate_k"]
    )
    return FixedPipeline(
        units,
        ranker,
        LocalGenerator(generation),
        generation,
        {
            "release": release["release_id"],
            "corpus": metadata["fingerprint"],
            "index": metadata["index_fingerprint"],
            "reranker": reranker,
            "generator": generation["revision"],
            "prompt": PROMPT_VERSION,
        },
        healthcheck,
    )
