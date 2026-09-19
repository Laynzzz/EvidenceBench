# 001: A versioned NIST cybersecurity corpus

Decision date: 2026-09-18. Implements plan phases 1 and 2 without changing architecture.

Use ten NIST technical publication families, six assigned to train and two each
to development and test before labels or model results exist. Versions of a
publication must retain its family assignment. This is a small, purposively
selected benchmark, not a representative sample of cybersecurity questions.

The sources are text-native public PDFs with stable citation locations. NIST
states that its publications are generally public domain in the United States:
[library FAQ](https://www.nist.gov/nist-research-library/library-faqs) and
[rights policy](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications).
Preserve attribution and any third-party notices. Raw PDFs are downloaded locally
and excluded from Git; the manifest records original URLs, dates and SHA-256 hashes.
This is a frozen-document retrieval task; historical publication versions are not
represented as current security guidance. Answers must identify their source version.

Use MIT-licensed pdfplumber for word text and PDF coordinates. Unlike an OCR
pipeline, it is suitable for these machine-generated PDFs and keeps extraction
inspectable. See [upstream documentation](https://github.com/jsvine/pdfplumber).
NFKC/whitespace normalization and overlapping page-local word windows are the
first version. Do not guess section headings, remove headers or join hyphenated
words before visual evidence supports a reliable rule. These limitations are
recorded for labeling/error review rather than hidden.

Full-document word 5-shingle Jaccard >= 0.85 flags likely copies assigned to
different families. It is a coarse check, not proof that semantic leakage is absent.
Manual review of related publication versions remains necessary. Source family
assignments and fingerprints must change if grouping changes before label freeze.
