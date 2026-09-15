# Baseline retrieval accuracy

Recorded at the end of Session 01 and never re-based. Every later session is
measured against the first row of this table, not against the row above it.

| Date | Session | Questions | Retrieval accuracy | Citation accuracy | What changed |
|---|---|---|---|---|---|
| 2026-08-05 | 01 | 20 | **50%** | not measurable | Baseline — fixed 500-char chunks, TF-IDF, top 3 |
| 2026-08-12 | 02 | 20 | 50% | **17%** | Manifest and provenance, structural parser, passage schema, quarantine |
| 2026-08-19 | 03 | 20 | 45% | **33%** | Structure-aware chunking, measured overlap of 100, redaction with a false positive rate |
| 2026-08-26 | 04 | 20 | 55% *(dense)* | 17% *(dense)* | Local embeddings, BM25, rank fusion. **Three retrievers — see the note below** |

> **These three rows were measured by the facilitator on 19 August 2026, not recorded
> in the room.** Session 01 ran without the twenty questions being written down, and
> they could not be reconstructed afterwards. `eval/questions.yaml` carries the full
> provenance note and what it costs. Read it before quoting any of these numbers.

## The two measures

**Retrieval accuracy** — did a chunk containing the correct answer reach the top
three? Not whether a model phrased a good answer; whether the right passage was found
at all. It needs no model, no network and no key, and it returns the identical number
every run.

**Citation accuracy** — does the *top-ranked* passage carry the section the answer
actually came from? It arrives in Session 02, because it cannot be computed at all
without structure, and it is scored only over questions whose answer is in the Act.
The AI Strategy has no citable sections; the run prints how many were excluded.

## Reading the table

**Session 02 moved retrieval by nothing at all**, which is exactly what it predicted
of itself. Chunking, the index and retrieval were all untouched; what changed is that
citation accuracy became *computable*. A flat row is the session working.

**Session 03 moved citation from 17% to 33% and retrieval down 5 points.** A
fixed-width chunk straddling a boundary can only be tagged with one subsection;
cutting on the boundary instead of across it is what moved citation. The retrieval
drop is a single question — q14, on the AI Strategy, which is chunked flat because
that document has no structure to be aware of. One question on twenty is 5%, and it
is worth more as a recorded oddity than as a rounding error nobody explained.

**The five paraphrase questions (q16–q20) miss on every row so far.** That is by
design: they ask the same things as q07, q05, q10, q08 and q09 in the words an
ordinary person would use, and a keyword index cannot match "privacy watchdog" to
"Data Commissioner". They are the headroom, and they are the first thing to re-run
when Session 04 replaces the index with embeddings. **If they do not flip, the
embeddings are not earning their cost.**

## The rules that make this table worth keeping

- The set **grows and never shrinks**. A question that has failed since August is the
  most informative item in the file.
- The baseline is **never re-based**. October's score is compared to 5 August's, not
  to the row above it.
- A **flattering baseline is a failure**. If a number comes out above 70%, the
  questions were too easy — harden them before committing.
- Any change to the corpus makes scores before and after **incomparable**. Record it
  in `docs/decisions.md` and mark the row here.

## Session 04 reports three numbers, not one

From 26 August there is more than one retriever, so a single row misrepresents the
week. Measured on the cohort set:

| Retriever | Retrieval | Citation |
|---|---|---|
| sparse (BM25) | 45% | **28%** |
| dense | **55%** | 17% |
| fused (RRF) | 50% | 22% |

The headline row above records **dense**, because it is the best retrieval figure and
retrieval accuracy is the quarter's headline metric. It is not the best on citation,
and pretending otherwise by picking a different retriever per column would make the
table a scoreboard rather than a measurement.

**Rank fusion did not beat both inputs**, which is what the Content Pack predicts.
Measured at every combination of pool and `rrf_k`, it lands between them. RRF rewards
agreement, and here the two retrievers agree on the easy questions and disagree on
exactly the hard ones.

**The number that matters for Session 05** is not in this table: the answer is
somewhere in a 30-passage shortlist **80%** of the time and reaches rank 1–3 about
**50%** of the time. That 30-point gap is what re-ranking exists to close, and it is
the ceiling on what re-ranking can achieve.
