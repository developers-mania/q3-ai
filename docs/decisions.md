# Decisions

One line per decision, with the reason. The reason matters more than the choice
when this is reviewed in October.

| Date | Decision | Why | Decided by |
|---|---|---|---|
| 2026-08-05 | Session 03 topic — published default is **Getting Data Ready** | _one sentence, written in the room_ | Session 01 room |
| 2026-08-12 | Corpus converted from **PDF**, not DOCX, with `pdftotext -layout` | Only PDFs were available; all 75 DPA sections survived extraction, so Session 03 still has structure to recover | Facilitator prep |
| 2026-08-12 | Answer matching ignores whitespace and hyphens | The PDF hard-wraps at ~80 columns, so s.56(5) reads "ninety\ndays"; without this a perfect retrieval scores MISS for typographic reasons | Facilitator prep |
| 2026-08-12 | Corpus text is written and checked out as **LF**, enforced by `.gitattributes` | Windows would otherwise write CRLF, changing the bytes and the checksum; scores are unaffected, but a pin that reports CHANGED on every clean Windows clone teaches people to delete the manifest | Facilitator prep |
| 2026-08-17 | **`ai-strategy-2025.txt` re-extracted** with `tools/pdf2corpus.py`; manifest re-pinned. `dpa-2019.txt` deliberately untouched (hash unchanged) | The Strategy is a two-column PDF and `pdftotext -layout` had flattened it into side-by-side lines — 24% of lines spliced the facing column mid-sentence, so the Strategy's own phrase "anchored by three key pillars and supported by four enablers" did not exist in the text and any question about the pillars scored MISS on a perfect retrieval. Re-extraction loses no content (+25 word tokens, no vocabulary dropped) and recovers more structure (29 → 96 section markers) | Facilitator prep |
| 2026-08-17 | Landmark checks in `tools/prepare_corpus.py` are **phrases, not single words**, plus a new column-interleaving check | The old landmarks were `"pillars"` and `"enablers"` — bare words survive any extraction, including a broken one, so the report passed while the corpus was damaged. A landmark must break when the extraction breaks | Facilitator prep |
