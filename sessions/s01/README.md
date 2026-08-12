# Session 01 · Build It Badly, Then Measure It

Six steps, fifty minutes, one screen. The facilitator types; the room watches,
argues, and writes questions.

| Time | Step | Who is working |
|---|---|---|
| 3:00 – 3:06 | 1 · Load the corpus | Facilitator |
| 3:06 – 3:14 | 2 · Chunk it badly | Facilitator + room |
| 3:14 – 3:20 | 3 · Index it badly | Facilitator |
| 3:20 – 3:26 | 4 · Retrieve | Facilitator |
| 3:26 – 3:40 | 5 · The room writes the evaluation set | Everyone, in groups |
| 3:40 – 3:50 | 6 · Run it and record the number | Facilitator + room |

## The running list of flaws

Written on the board as each one is named. By 3:50 it has five items and each has a
session number against it. This list is the syllabus — nobody had to decide what to
teach next; the flaws named themselves as soon as the thing ran.

| # | Flaw | Named at step | Repaired in |
|---|---|---|---|
| 1 | Chunks cut across meaning | 2 | Session 03 |
| 2 | The index matches words, not meaning | 3 | Session 04 |
| 3 | No re-ranking — the first plausible match wins | 4 | Session 05 |
| 4 | No confidence threshold — never says "I don't know" | 4 | Session 09 |
| 5 | Chunks carry no section number, so no answer can be cited | 4 | Session 03 |
| — | The corpus is two static files a human downloaded | — | Session 02 |

## Running it

```bash
python -m src.pipeline          # steps 1–4: load, chunk, index, retrieve a demo question
python -m src.pipeline --score  # step 6: run the evaluation set and print the number
```

The lab in `lab.py` is the same six steps in jupytext percent format, for
participants replaying at home. `src/pipeline.py` is the source of truth — the lab
imports from it rather than restating it, so there is one place to fix a bug.

## Two things the facilitator should have ready

- **The opening hook, pre-recorded as a transcript file** (`fixtures/opening-hook.md`). It is the only moment in
  Session 01 that touches a model. If the network is down the hook still runs.
- **The eight seed questions from Appendix A of the Content Pack**, printed. Groups
  that see a worked example produce good questions in four minutes; groups that do
  not spend eight minutes deciding what a question is.
