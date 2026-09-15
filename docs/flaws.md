# The running list of flaws

Written on the board in Session 01 as each one is named, and carried in this file
for the rest of the quarter. Nobody had to decide what to teach next — the flaws
named themselves as soon as the pipeline ran.

Tick a row only when the number moves and the evaluation set shows it.

| # | Flaw | Named at | Repair | Owner session | Repaired |
|---|---|---|---|---|---|
| 1 | Chunks cut across meaning | S01 step 2 | Semantic chunking on section boundaries | 03 | ☑ |
| 2 | The index matches words, not meaning | S01 step 3 | Dense embeddings, then hybrid search | 04 | ☑ |
| 3 | No re-ranking — the first plausible match wins | S01 step 4 | Two-stage retrieval with a re-ranker | 05 | ◐ |
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

**Session 04 (26 August).** Flaw 2 closed. A local bi-encoder gives the system a
notion of meaning: dense retrieval takes the cohort set from 45% to 55% and wins
three questions keyword search could not reach, two of them paraphrases.

It is closed, not solved, and the measurement says how. Dense *lowers* citation
accuracy (28% -> 17%) because an embedding finds the right region and is worse at
picking the exact subsection. Rank fusion lands BETWEEN its two inputs rather than
above them at every setting tried, because RRF rewards agreement and the two
retrievers agree on the easy questions and disagree on exactly the hard ones.

The number that matters for next week: the answer is somewhere in a 30-passage
shortlist 80% of the time, and reaches rank 1-3 only 50% of the time. Retrieval is
no longer failing to FIND the answer. It is failing to RECOGNISE it.

**Session 05 (2 September).** Flaw 3 is **half** closed, and the half that remains is
a chunk boundary rather than a ranking problem.

A cross-encoder re-reads the 30-passage shortlist, reading question and passage
together. Retrieval 45% -> 50%, citation 22% -> 28%. The near-miss pair that defeated
four retrievers finally separates in one direction: the PROCESSOR question is answered
correctly with a wide margin (+9.48 against +6.16).

The CONTROLLER question is not, and the obvious explanation is wrong. s.43(1)(a)
matches every term in that question and still loses to s.43(3), which carries both
roles, both deadlines and all the notification vocabulary - it reads as the
comprehensive passage on the topic. At overlap 0 the same thing happens for the
opposite reason: s.43(1)(a) loses "controller" to its parent. Neither chunking setting
presents the right answer as the better passage. Putting the parent stem back closes
the score gap from 0.46 to 0.07 without flipping the order.

Shortlist recall is 80% against a score of 50%, so the answer is usually found and
mis-ranked. Session 03 said chunking is the one decision later sophistication cannot
compensate for; this is that sentence arriving inside the most sophisticated
component built so far.
