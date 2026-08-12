# Decisions

One line per decision, with the reason. The reason matters more than the choice
when this is reviewed in October.

| Date | Decision | Why | Decided by |
|---|---|---|---|
| 2026-08-05 | Session 03 topic — published default is **Getting Data Ready** | _one sentence, written in the room_ | Session 01 room |
| 2026-08-12 | Corpus converted from **PDF**, not DOCX, with `pdftotext -layout` | Only PDFs were available; all 75 DPA sections survived extraction, so Session 03 still has structure to recover | Facilitator prep |
| 2026-08-12 | Answer matching ignores whitespace and hyphens | The PDF hard-wraps at ~80 columns, so s.56(5) reads "ninety\ndays"; without this a perfect retrieval scores MISS for typographic reasons | Facilitator prep |
| 2026-08-12 | Corpus text is written and checked out as **LF**, enforced by `.gitattributes` | Windows would otherwise write CRLF, changing the bytes and the checksum; scores are unaffected, but a pin that reports CHANGED on every clean Windows clone teaches people to delete the manifest | Facilitator prep |
