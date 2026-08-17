# Sprint26 Q3 · Putting AI to Work

**You are on branch `session-01-start`.**

> ### Session 01 — What Changed
> *What actually changed in how software is built, and what does it mean for the
> work I already do?*
>
> **Stack layers today:** 1 (Data infrastructure) and 2 (Context and memory) —
> built badly, on purpose.

Ten weekly sessions. Each one improves **one layer** of a system this room built
and watched fail in Session 01. Nobody takes a facilitator's word for whether a
change helped — the room watches a number move, and can name the line of code that
moved it.

---

## What today produces

| Artifact | Where it lands |
|---|---|
| A working but deliberately poor retrieval pipeline | `src/pipeline.py` |
| A 20-question evaluation set written by the room | `eval/questions.yaml` |
| A recorded baseline retrieval score | `eval/baseline.md` |
| Five named flaws, each owned by a later session | `docs/flaws.md` |
| Layer ownership, the Session 03 decision, standard 1 of 10 | `docs/layer-ownership.md`, `docs/decisions.md`, `docs/standard.md` |

---

## Setup

Session 01 is led from the front on one screen. Following along locally is
optional — participants who watch and think produce the same output.

**No API key. No account. No network** once this repository is cloned. That is a
design choice, not a limitation: what is measured today is *retrieval*, and
retrieval is measurable with scikit-learn alone on a mid-range laptop.

```bash
git clone https://github.com/developers-mania/q3-ai.git && cd q3-ai
git checkout session-01-start

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python tools/check_setup.py      # one line per check, no network
```

`tools/check_setup.py` should print four `OK` lines before 2:00 PM.

## The corpus is committed and frozen

Both text files ship in `corpus/`, pinned by `corpus/MANIFEST.sha256`. Extraction is
not deterministic across tools, so a participant converting their own sources would
index different bytes and the baseline would stop being one reproducible number. See
[`corpus/README.md`](corpus/README.md) for provenance and revision. Check the pin:

```bash
python tools/verify_corpus.py
```

## Running the pipeline

```bash
python -m src.pipeline           # loads, chunks, indexes
python -m src.pipeline --ask "..."   # retrieve against one question
python -m src.pipeline --score   # run eval/questions.yaml, print the accuracy
```

---

## New here? Read these two

| | |
|---|---|
| [**docs/repository-guide.md**](docs/repository-guide.md) | How this repository is laid out, what you touch and what you never touch, the branch model, and the measurement spine. **Ten minutes, read it first.** |
| [**sessions/README.md**](sessions/README.md) | The ten sessions, and a codelab guide for each — what to check out, where to look, what it builds, and **how to know it worked** |

Going to a session? Open that session's guide:
[01](sessions/s01/README.md) · [02](sessions/s02/README.md) ·
[03](sessions/s03/README.md) · [04](sessions/s04/README.md) ·
[05](sessions/s05/README.md) · [06](sessions/s06/README.md) ·
[07](sessions/s07/README.md) · [08](sessions/s08/README.md) ·
[09](sessions/s09/README.md) · [10](sessions/s10/README.md)

## Repository layout

```
corpus/          the two source documents — provenance and checksums. FROZEN
fixtures/        pre-recorded model output, so the opening hook runs offline
src/pipeline.py  the growing library — this is what changes week to week
sessions/sNN/    codelab guide (README.md) + the lab as a .py notebook
eval/            the question set, and the score — the measurement spine
docs/            flaws, decisions, layer ownership, the Session 10 standard
tools/           setup check, corpus verification, notebook generation
```

Two things that surprise people: **`src/pipeline.py` does not exist on a `-start`
branch** — it is built live in the room, and appears on `solution/session-NN`. And
`notebooks/` is a gitignored build artifact; the `.py` under `sessions/` is the
source of truth.

## Branching

`session-NN-start` is where the room begins; `solution/session-NN` tags where it
finished. Fixes are merged forward, never rebased — because you have already
cloned this. Full convention, including the comment taxonomy used throughout the
code, is in [`CONTRIBUTING.md`](CONTRIBUTING.md).
