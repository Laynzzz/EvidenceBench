"""Emit the first agent-drafted review batch; never marks labels human-reviewed."""

from pathlib import Path

from evidencebench.ingestion import load_units
from evidencebench.labels import validate_labels
from evidencebench.schemas import QueryExample

# Source passages inspected directly, without using model ranking scores.
DRAFTS = [
    (
        "207",
        "Does being on an enterprise network automatically make a device trusted?",
        "316ba8e4d297d4bf365ed6e10c1d5c5c8a122aa4cdc07d2c0500eb8039764e9f",
        "No. Network location alone does not imply trust; communication must be secured.",
    ),
    (
        "207",
        "Does authorization for one resource automatically authorize access to another?",
        "6d63df28b1d2248c329ecb3c41a0d80e59e2ab17df44f75b322d34cc601bf411",
        "No. Access is per resource/session and uses the least privileges needed.",
    ),
    (
        "207",
        "Which component enables, monitors, and terminates connections to enterprise resources?",
        "f8f9eae7482451b58129358099de366592c92ed001d4cb2b11fad9a9e0e7d439",
        "The policy enforcement point (PEP). "
        "Distinguish it from the policy engine and administrator.",
    ),
    (
        "207",
        "What device-state information can CDM provide to a zero-trust policy engine?",
        "05cbe8d143ccaa3f4b386baf24b5fa9919ad93991de361c6d56500cc23153913",
        "Examples include OS patch status, approved software integrity, "
        "unapproved software, and known vulnerabilities.",
    ),
    (
        "207",
        "Does zero trust authenticate a user only once for an entire transaction?",
        "f4d29acaa8b37489333d4990de8d7a6730c0539a8d0d583d45c64baae0702af1",
        "No. Policy can require ongoing monitoring, reauthentication, and reauthorization.",
    ),
    (
        "218",
        "Must every organization implement SSDF using the same tools and techniques?",
        "f1d01989d43bfa4cec6a349d8ffe525c67c3dcc1f54fda8e4c15081f4fa09c50",
        "No. SSDF focuses on outcomes and does not prescribe implementation tools or mechanisms.",
    ),
    (
        "218",
        "Does SSDF require adopting every practice for every use case?",
        "f1d01989d43bfa4cec6a349d8ffe525c67c3dcc1f54fda8e4c15081f4fa09c50",
        "No. Use a risk-based approach to select relevant, appropriate, effective practices.",
    ),
    (
        "218",
        "Why should secure development practices be integrated throughout an SDLC?",
        "de8da6cef05d410d436cc1c99ccb659a59eb9cb564ab81bf049a45f26b2fae30",
        "Reduce vulnerabilities, reduce exploitation impact, "
        "and address root causes to prevent recurrence.",
    ),
    (
        "218",
        "What does shifting security left aim to reduce?",
        "ff0e6dcf06d43de60c5ee5f5efd6c39bf7593689d2812e875e137969b562e716",
        "Addressing security earlier reduces remediation effort/cost "
        "and accumulated technical debt.",
    ),
    (
        "207",
        "What is Acme Corporation's current production VPN administrator password?",
        None,
        "Refuse: this public corpus contains no Acme production credentials.",
    ),
    (
        "218",
        "What dollar amount did my company spend implementing SSDF last quarter?",
        None,
        "Refuse: the corpus has no private company budget records.",
    ),
    (
        "218",
        "Which exact critical vulnerabilities exist in my company's unreleased source code?",
        None,
        "Refuse: the code and vulnerability assessment are absent from this corpus.",
    ),
]


def main():
    target = Path("data/labels/dev-pilot-draft.jsonl")
    if target.exists():
        raise SystemExit("Review batch exists; refusing to overwrite possible human edits")
    units = load_units(Path("data/processed/nist-v1"))
    lookup = {u.element_id: u for u in units}
    examples = [
        QueryExample(
            query_id=f"dev-pilot-{i:02d}",
            text=text,
            split="dev",
            family_id=f"nist-sp-800-{family}",
            query_type="fact" if key else "unanswerable",
            relevance={key: 2} if key else {},
            answerable=key is not None,
            answer_criteria=criteria,
            supporting_evidence=[key] if key else [],
            label_provenance=(
                "Agent-authored from source passages on 2026-09-18; human review pending"
            ),
            review_status="draft",
        )
        for i, (family, text, key, criteria) in enumerate(DRAFTS, 1)
    ]
    validate_labels(examples, units, allow_drafts=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(q.model_dump_json() for q in examples) + "\n", encoding="utf-8")
    lines = [
        "# First development-label review batch",
        "",
        "Status: 12 agent drafts, zero human reviews.",
        "This batch is not the full benchmark. No model scores are shown. Check each claim against",
        "the PDF, correct relevance/answer criteria, and add other supporting chunks where needed.",
        "Unanswerable cases here are deliberately easy; the full set needs harder in-domain cases.",
        "",
    ]
    for query in examples:
        lines += [
            f"## {query.query_id}",
            "",
            query.text,
            "",
            f"Draft criteria: {query.answer_criteria}",
            "",
        ]
        for key in query.supporting_evidence:
            unit = lookup[key]
            lines += [
                f"Source: [{unit.document_id}, PDF page {unit.page}]"
                f"({unit.source_url}#page={unit.page})",
                "",
                f"Evidence ID: `{key}`",
                "",
                f"> {unit.text}",
                "",
            ]
        lines += [
            "Review: **pending**. Record corrections; do not accept based only on fluent wording.",
            "",
        ]
    Path("docs/label-review-pilot.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Prepared {len(examples)} drafts in {target}; none are approved labels.")


if __name__ == "__main__":
    main()
