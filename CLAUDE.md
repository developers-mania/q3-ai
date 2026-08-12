# Sprint26 Q3 · Putting AI to Work

Ten-week community codelab at American Corner Nakuru. Each session improves **one
layer** of a retrieval system the room built and watched fail in Session 01. The
teaching artifact is the **diff between session branches**, and the measurement is
a single retrieval-accuracy number tracked from 5 August to October.

Corpus: Kenya Data Protection Act (Cap. 411C) and the Kenya National AI Strategy
2025–2030. Python. Read `sessions/sNN/README.md` for a session's shape and
`CONTRIBUTING.md` for the full branch and comment rules.

## Non-negotiables

These exist because breaking them silently invalidates weeks of measurement.

- **The corpus is committed and frozen.** Extraction is not deterministic across
  tools, so if participants convert their own sources they index different bytes
  and the baseline stops being one reproducible number. Changing the corpus makes
  scores before and after incomparable — record any change in `docs/decisions.md`
  and mark the row in `eval/baseline.md`.
- **`eval/questions.yaml` grows and never shrinks.** A question failing since
  August is the most informative item in the file, not a candidate for removal.
- **The baseline is never re-based.** Later sessions are measured against the
  first row of `eval/baseline.md`, not the row above them.
- **Never rebase a published branch.** See fix-forward below.
- **`requirements.txt` stays tiny.** It is read aloud in the room as evidence the
  session needs almost nothing. Facilitator tooling goes in `requirements-dev.txt`.

## The `answer` / `expect` rule

Statutes spell numbers out. The Act says *seventy two hours*; the board says
*72 hours*. Scoring a substring against the board answer returns MISS on a perfect
retrieval. So every question carries both: `answer` is human-readable, `expect` is
a list of the surface forms the corpus actually uses, and `expect` is what the
scorer matches on.

**Never write `expect` from the canonical publication.** Grep the converted text in
`corpus/` and copy what is actually there.

## Branches and tags

- `session-NN-start` — everything completed through Session NN-1, working, plus
  Session NN's scaffolding and TODOs. Checking it out puts you where the room is
  at 2:00 PM.
- `solution/session-NN` — tag at the completed state. **Movable**: re-point it when
  an earlier session is fixed.
- `session-01-baseline` — Session 01 only, demonstrating the live commit workflow.

**Fix forward, never rebase.** Branches are cloned by participants. When a bug in
Session 02 surfaces during Session 06: commit on `session-02-start`, merge forward
through each later branch in order, re-point affected tags.

## Comment conventions

Code is teaching material. Comments carry content — but one line each, or the code
stops being readable. Anything longer belongs in `sessions/sNN/README.md`.

| Convention | Use |
|---|---|
| Module docstring | Session number, the plain-language question, the stack layer |
| `# WHY:` | Rationale — especially for choices that are deliberately bad |
| `# FLAW n:` | A named flaw from the running list, with the session that repairs it |
| `# DPA s.43:` | This line reflects a specific statutory requirement |
| `# TODO(session-NN):` | A live-coding gap to be filled in the room |

The `# DPA s.NN` anchors are the ones to be strict about. They are what keeps the
legal layer concrete rather than framing.

## Introduce technology only when a question demands it

A stated rule of the quarter: every technology is introduced to answer a question
posed before the technology was named. Do not pre-build abstractions for later
sessions. Session 01 needs no API key, no account and no network — so no config or
inference layer exists yet, and adding one early would contradict what the room was
told.

Model access, when it arrives, is bring-your-own-key.

## Working style

- State divergences between source documents plainly. Do not smooth them over.
- Concrete, testable claims over aspirational language.
- Distinguish decisions from proposals; do not upgrade one into the other.
- Do not fill gaps with assumptions — surface them as questions.
- Read files in full before making evidential claims about them.
