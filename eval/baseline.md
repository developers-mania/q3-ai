# Baseline retrieval accuracy

Recorded at the end of Session 01 and never re-based. Every later session is
measured against the first row of this table, not against the row above it.

| Date | Session | Questions | Retrieval accuracy | Citation accuracy | What changed |
|---|---|---|---|---|---|
| 2026-08-05 | 01 | _to be filled in the room_ | _to be filled in the room_ | not measurable | Baseline — fixed 500-char chunks, TF-IDF, top 3 |
| 2026-08-12 | 02 | _to be filled in the room_ | _expected: roughly unchanged_ | _expected: poor_ | Manifest and provenance, structural parser, passage schema, quarantine |

> A flattering baseline is a failure. If the number comes out above 70%, the
> questions were too easy — harden them before committing.

**Citation accuracy** arrives in Session 02 and is a different question from retrieval
accuracy: *does the top-ranked passage carry the section the answer actually came
from?* It is scored only over questions whose answer is in the Act — the AI Strategy
has no citable sections, and the run prints how many were excluded.

Expect it to be **poor** in Session 02. That is the session working, not failing: a
fixed-width chunk straddling a boundary can only be tagged with one subsection. On the
seed set it came out at 8%, with 5 more questions landing the right section and the
wrong subsection. Session 03 cuts on the boundary instead of across it.
