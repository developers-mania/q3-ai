# The running list of flaws

Written on the board in Session 01 as each one is named, and carried in this file
for the rest of the quarter. Nobody had to decide what to teach next — the flaws
named themselves as soon as the pipeline ran.

Tick a row only when the number moves and the evaluation set shows it.

| # | Flaw | Named at | Repair | Owner session | Repaired |
|---|---|---|---|---|---|
| 1 | Chunks cut across meaning | S01 step 2 | Semantic chunking on section boundaries | 03 | ☐ |
| 2 | The index matches words, not meaning | S01 step 3 | Dense embeddings, then hybrid search | 04 | ☐ |
| 3 | No re-ranking — the first plausible match wins | S01 step 4 | Two-stage retrieval with a re-ranker | 05 | ☐ |
| 4 | No confidence threshold — never says "I don't know" | S01 step 4 | Scored guardrails and abstention | 09 | ☐ |
| 5 | Chunks carry no section number, so no answer can be cited | S01 step 4 | Structure-preserving ingestion | 03 | ☐ |
| — | The corpus is two static files a human downloaded | S01 step 1 | Live ingestion and freshness | 02 | ☐ |

Flaws 1 and 5 share an owner because they are the same flaw seen from two angles:
a chunk that respects section boundaries is also a chunk that knows which section
it came from.
