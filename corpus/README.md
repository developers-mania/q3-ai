# The corpus

Two plain text files. Both are public documents. Neither was chosen for convenience.

| Filename | Document | Source |
|---|---|---|
| `dpa-2019.txt` | Kenya Data Protection Act, Cap. 411C (No. 24 of 2019), as revised 31 December 2022 | Kenya Law — new.kenyalaw.org |
| `ai-strategy-2025.txt` | Kenya National Artificial Intelligence Strategy 2025–2030 | Ministry of Information, Communications and the Digital Economy |

## Why the text is committed

Kenya Law's contents are in the public domain, so redistribution raises no licensing
question. The converted text is committed rather than fetched because extraction is
not deterministic across tools: two people running different extractors on the same
PDF index different bytes, and every score after that stops being comparable to the
baseline. The *revision* matters for the same reason — a chunk index built against the
2022 revision and an evaluation set written against a later one disagree silently, a
Layer 1 failure of exactly the kind Session 02 is about.

`corpus/MANIFEST.sha256` is the pin. `python tools/verify_corpus.py` writes it on
first run and checks against it afterwards.

## Preparing the text

Source documents are commonly published as PDF or DOCX. That is fine — they are
converted once, in advance, by the facilitator:

```bash
pip install -r requirements-dev.txt
python tools/prepare_corpus.py sources/dpa.docx --name dpa-2019
python tools/prepare_corpus.py --check-only        # re-report on corpus/*.txt
```

### Two tools, and when to use which

| Tool | Job |
|---|---|
| `tools/pdf2corpus.py` | **Extraction.** Orders two-column pages into real reading order, strips running headers, de-hyphenates. Needed whenever the source is a multi-column PDF. |
| `tools/prepare_corpus.py` | **Normalisation and the report.** NFKC, straight quotes, LF endings, then the checks that say whether the conversion is usable. Always run last — it is what writes into `corpus/`. |

A single-column source needs only the second. A two-column source needs both, in
order:

```bash
python tools/pdf2corpus.py sources/Strategy.pdf -o /tmp/conv       # de-column
python tools/prepare_corpus.py /tmp/conv/Strategy.txt --name ai-strategy-2025
```

What was actually run for the committed text:

```bash
# dpa-2019.txt — 12 August 2026. Single column; pdftotext -layout was enough.
python tools/prepare_corpus.py "sources/DataProtectionAct.pdf" --name dpa-2019

# ai-strategy-2025.txt — re-extracted 17 August 2026, see docs/decisions.md.
python tools/pdf2corpus.py "sources/KenyaAIStrategy.pdf" -o <scratch>
python tools/prepare_corpus.py "<scratch>/KenyaAIStrategy.txt" --name ai-strategy-2025
```

All 75 sections of the Act survived, so the PDF cost nothing there. The Strategy is
two-column and the first conversion did cost something — it flattened the columns
into side-by-side lines, which destroyed every phrase spanning a line break. The
report now catches that; see `find_interleaved_columns` in `tools/prepare_corpus.py`.

`sources/` is gitignored: the committed `.txt` is the artifact, and the PDFs are 23 MB.

**Prefer DOCX over PDF where both exist.** DOCX is structured XML, so section
numbering arrives as text. PDF numbering is inferred from glyph positions and is
the thing most often lost.

The script prints a report after converting. Read it — the conversion succeeding
is not the same as the conversion being usable.

Strip nothing. In particular keep section numbering, part headings and subsection
markers in the plain text — Session 01 deliberately discards them at the *chunking*
stage, and Session 03 recovers them. If they are stripped at the source, Session 03
has nothing to recover and the largest expected jump in the quarter's number
disappears.

Target: UTF-8, Unix line endings, no page furniture (running headers, page numbers).

## Extending the corpus

A decision open until Session 02: whether to add the three 2021 subsidiary
regulations made under the Act —

- Data Protection (General) Regulations 2021 — Legal Notice 263
- Data Protection (Registration of Data Controllers and Data Processors) Regulations 2021 — LN 265
- Data Protection (Complaints Handling and Enforcement) Regulations 2021 — LN 264

**If this goes ahead it must go ahead early.** Adding documents changes every chunk
index downstream, so the earlier it lands the less there is to rebuild. Record the
decision and its reason in `docs/decisions.md` either way.
