# NIST cybersecurity corpus pilot

Manifest: `data/manifests/nist-cybersecurity.json`. Ten publications, 647 physical
PDF pages, 1,773 page-local chunks. Six families train, two development (800-207,
800-218), two test (800-137, 800-153). Source selection and assignments precede
labels/model selection. Related revisions must remain in the same family.

All sources were retrieved on 2026-09-19 UTC (2026-09-18 local). Exact dates and
SHA-256 checksums are in the manifest. Publications were acquired from NIST's
official publication host. See [corpus decision](../docs/adr/001-corpus-and-extraction.md)
for usage conditions. No resume, job descriptions or private documents are included.

Extraction: pdfplumber 0.11.10 / pdfminer-six 20260107; Unicode NFKC and whitespace
normalization; windows of 180 words with 30-word overlap. Chunks never cross pages.
PDF bounding boxes use points measured from the top left. `section` is null because
section inference is not implemented. Headers, footers, marginal watermarks and
literal hyphenation are retained in this initial version and can affect retrieval.

Both clean builds yielded fingerprint
`1644879e5b17288ccb6d90269089eaeb6a96a2a92deb958376077f57d5341c6b`.
No pages were classified as having zero extracted words. That does **not** prove
every page's content was extracted: diagrams and scanned regions can be omitted.
Visual pilot inspection included 800-207 PDF p12 and 800-34r1 PDF p26; the latter's
figure text is absent. SSDF's multi-column tables can interleave in reading order.
Exclude table/figure-dependent questions pending a dedicated extraction improvement.

Full-document 5-shingle Jaccard >= .85 found no cross-family near-duplicate documents.
Independent review found identical authority boilerplate across train/dev chunks.
This is a candidate-family split, not proof of complete leakage elimination or
pretraining contamination control. The pretrained model may have seen public NIST text.

Twelve development drafts contain nine answerable and three unanswerable examples;
none is human-reviewed. Training and final-test labels are not prepared. No quality
statistics are available. Only two families in each evaluation split limits any
later generalization claim. This frozen, English-language technical-document task
does not establish current cybersecurity guidance, multilingual quality, or CV skill.
