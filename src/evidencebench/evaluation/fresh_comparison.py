"""Paired validation comparison and durable resource counters; no models loaded here."""

import time

from evidencebench.evaluation.answers import answer_metrics
from evidencebench.ingestion import canonical


class BudgetExceeded(RuntimeError):
    pass


class Budget:
    def __init__(self, path, limits):
        self.path, self.limits = path, dict(limits)
        self.used = {key: 0 for key in limits}
        with path.open("xb") as stream:
            stream.write(canonical({"limits": self.limits, "used": self.used}))

    def charge(self, key, count=1):
        if key not in self.limits or count < 0 or self.used[key] + count > self.limits[key]:
            raise BudgetExceeded("resource budget exceeded")
        self.used[key] += count
        temporary = self.path.with_suffix(".tmp")
        temporary.write_bytes(canonical({"limits": self.limits, "used": self.used}))
        temporary.replace(self.path)


class MeteredModel:
    def __init__(self, model, budget, variant, max_tokens):
        self.model, self.budget, self.variant, self.max_tokens = model, budget, variant, max_tokens

    def generate(self, **kwargs):
        tokens = kwargs["max_new_tokens"]
        if not 0 < tokens <= self.max_tokens:
            raise BudgetExceeded("generation token budget exceeded")
        self.budget.charge(f"{self.variant}_calls")
        self.budget.charge("reserved_tokens", tokens)
        return self.model.generate(**kwargs)


def compare_queries(queries, units, retriever, generators, charge, root, threshold):
    if not queries or any(q.split != "dev" for q in queries):
        raise ValueError("development queries only")
    if len({q.query_id for q in queries}) != len(queries):
        raise ValueError("duplicate development query")
    if set(generators) != {"control", "constrained"}:
        raise ValueError("fixed comparison requires both generators")
    lookup = {u.element_id: u for u in units}
    root.mkdir(parents=True, exist_ok=True)
    # Exclusive files preserve partial runs and prevent an accidental replay.
    for variant in generators:
        with (root / f"{variant}.jsonl").open("xb"):
            pass
    rows = {key: [] for key in generators}
    for query in queries:
        started = time.perf_counter()
        packed, aliases, pre, post, retrieval_error = {}, {}, [], [], None
        try:
            hits = retriever.retrieve(query.text, {}, 50)
            pre = [h.model_dump(mode="json") for h in retriever.pre]
            post = [h.model_dump(mode="json") for h in hits]
            if hits and hits[0].reranker_score >= threshold:
                for index, hit in enumerate(hits[:3], 1):
                    aliases[f"E{index}"] = hit.element_id
                    packed[f"E{index}"] = lookup[hit.element_id].text[:1000]
        except BudgetExceeded:
            raise
        except Exception as exc:
            retrieval_error = type(exc).__name__
            pre = [h.model_dump(mode="json") for h in retriever.pre]
        retrieval_ms = (time.perf_counter() - started) * 1000
        trace = {
            "pre_ranking": pre,
            "post_ranking": post,
            "pre_ids": [h["element_id"] for h in pre],
            "post_ids": [h["element_id"] for h in post],
            "packed_ids": list(aliases.values()),
            "packed_evidence": packed,
        }
        for variant, generator in generators.items():
            tick = time.perf_counter()
            result = {
                "status": "refused",
                "reason": "insufficient_evidence",
                "answer": "",
                "evidence_ids": [],
            }
            raw = ""
            if retrieval_error:
                result.update(status="failure", reason="retrieval_" + retrieval_error)
            elif packed:
                charge(f"{variant}_invocations")
                try:
                    # The only model inputs are question text and retrieved passages.
                    result = generator.generate(query.text, dict(packed))
                    if result["status"] not in {"answered", "refused", "failure"} or any(
                        key not in aliases for key in result.get("evidence_ids", [])
                    ):
                        raise ValueError("invalid generator result")
                except BudgetExceeded:
                    raise
                except Exception as exc:
                    result = {
                        "status": "failure",
                        "reason": type(exc).__name__,
                        "answer": "",
                        "evidence_ids": [],
                    }
                raw = getattr(generator, "last_output", "")
            generation_ms = (time.perf_counter() - tick) * 1000
            citations = [aliases[key] for key in result.pop("evidence_ids", [])]
            row = {
                **result,
                "query_id": query.query_id,
                "question": query.text,
                "family_id": query.family_id,
                "answerable": query.answerable,
                "answer_criteria": query.answer_criteria,
                "supporting_evidence": query.supporting_evidence,
                "citation_ids": citations,
                "elapsed_ms": retrieval_ms + generation_ms,
                "retrieval_ms": retrieval_ms,
                "generation_ms": generation_ms,
                "timing_scope": "shared retrieval plus individual generation; local offline",
                "trace": {**trace, "raw_generation": raw},
            }
            rows[variant].append(row)
            with (root / f"{variant}.jsonl").open("ab") as stream:
                stream.write(canonical(row) + b"\n")
        print(f"fresh validation {len(rows['control'])}/{len(queries)}", flush=True)
    return rows


def summarize(rows):
    metrics = {v: answer_metrics(records) for v, records in rows.items()}
    a, b = metrics["control"], metrics["constrained"]
    metrics["passes_validation_gate"] = (
        b["answerable_token_f1"] > a["answerable_token_f1"]
        and b["failure_count"] <= a["failure_count"]
        and b["missing_refusal_rate"] <= a["missing_refusal_rate"]
        if a["missing_refusal_rate"] is not None and b["missing_refusal_rate"] is not None
        else False
    )
    metrics["passes_validation_gate"] &= (
        a["upstream_citation_precision"] is not None
        and b["upstream_citation_precision"] is not None
        and b["upstream_citation_precision"] >= a["upstream_citation_precision"]
    )
    positives = [r for r in rows["control"] if r["answerable"]]
    metrics["evidence_recall"] = {
        stage: sum(
            len(set(r["trace"][stage]) & set(r["supporting_evidence"]))
            / len(set(r["supporting_evidence"]))
            for r in positives
        )
        / len(positives)
        for stage in ("pre_ids", "post_ids", "packed_ids")
    }
    metrics["evidence_recall_definition"] = (
        "Macro recall over answerable questions; pre/post rerank depth 50; packed IDs after "
        "threshold and top-3 selection. ID presence does not prove support survives "
        "character clipping."
    )
    return metrics
