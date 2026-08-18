# The running list of flaws

Written on the board in Session 01 as each one is named, and carried in this file
for the rest of the quarter. Nobody had to decide what to teach next — the flaws
named themselves as soon as the pipeline ran.

Tick a row only when the number moves and the evaluation set shows it.

| # | Flaw | Named at | Repair | Owner session | Repaired |
|---|---|---|---|---|---|
| 1 | Chunks cut across meaning | S01 step 2 | Semantic chunking on section boundaries | 03 | ☑ |
| 2 | The index matches words, not meaning | S01 step 3 | Dense embeddings, then hybrid search | 04 | ☐ |
| 3 | No re-ranking — the first plausible match wins | S01 step 4 | Two-stage retrieval with a re-ranker | 05 | ☐ |
| 4 | No confidence threshold — never says "I don't know" | S01 step 4 | Scored guardrails and abstention | 09 | ☐ |
| 5 | Chunks carry no section number, so no answer can be cited | S01 step 4 | Structure-preserving ingestion | 02, 03 | ☑ |
| 6 | The corpus is two static files a human downloaded | S01 step 1 | Manifest, provenance and change detection | 02 | ☑ |

Flaws 1 and 5 share an owner because they are the same flaw seen from two angles:
a chunk that respects section boundaries is also a chunk that knows which section
it came from.

**Session 02 (12 August).** Flaw 6 closed: `manifest.json` records where every source
came from, which version it is and when it was retrieved, and `python -m src.ingest`
refuses to proceed when the bytes no longer match.

Flaw 5 is **half** closed, and the half that remains is the point. Every passage now
carries a citation — but a 500-character chunk that straddles a subsection boundary
gets tagged with whichever subsection it *starts* in. Citation accuracy came out at
8%, with 5 more questions retrieving the right section and the wrong subsection.
The parser is fine. The cut is not. Session 03 repairs the cut.

**Session 03 (19 August).** Flaws 1 and 5 closed together, which is what the running
list predicted when it noted they were the same flaw seen from two angles: a chunk
that respects section boundaries is also a chunk that knows which section it came
from.

Citation accuracy 8% -> 38% on the structure-aware cut alone, and the passage holding
the 48-hour deadline is now cited `DPA s.43(3)` rather than `DPA s.43(2)`. With the
measured overlap of 100 both numbers clear Session 02: **retrieval 73%, citation 31%**.

The second half added redaction and took some of it back. The naive name rule fires
739 times at a 100% false positive rate — 80 of them on "Data Commissioner" — and
costs 6 points of retrieval and 8 of citation. Narrowing recovers all of it. Nothing
errored; only the score noticed.
