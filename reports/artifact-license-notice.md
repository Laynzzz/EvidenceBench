# Artifact attribution and scope

QASPER v0.3 text and annotations: Allen Institute for AI / original QASPER authors,
CC BY 4.0. Source: https://huggingface.co/datasets/allenai/qasper and
https://arxiv.org/abs/2105.03011. EvidenceBench filters questions, maps paragraphs to
source PDF pages, adds title context, and creates deterministic IDs/splits. These
modifications and exclusions are described in the dataset card. Original paper PDFs
and their rendered page images are excluded from this bundle and retain author rights.

The fine-tuned checkpoint derives from cross-encoder/ms-marco-TinyBERT-L2-v2,
https://huggingface.co/cross-encoder/ms-marco-TinyBERT-L2-v2, pinned at
81d1926f67cb8eee2c2be17ca9f793c7c3bd20cc, Apache-2.0. The full Apache license is in
artifacts/exports/LICENSE-Apache-2.0.txt in the bundle. EvidenceBench fine-tuned its
weights on the documented training pairs; its generated model card retains base
model attribution. The selected original checkpoint is included; no base Qwen or
MiniLM model downloads are bundled.

The bundle is prepared locally for reproduction. It has not been published, uploaded
or sent to another person. It contains public benchmark-derived material and local
experiment records, not credentials, private resume content or application records.
