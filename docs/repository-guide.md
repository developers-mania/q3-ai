# How this repository works

A map of the repository and how to move around it. Read this once, before your
first session. It should take ten minutes.

If you want the rules rather than the map, read [`CLAUDE.md`](../CLAUDE.md) (the
non-negotiables) and [`CONTRIBUTING.md`](../CONTRIBUTING.md) (branches and comment
conventions). This file is the friendly version.

---

## 1 · The one idea

This repository is not a finished application. It is **one retrieval system,
rebuilt ten times, each time one layer better than the week before.**

Session 01 built it badly on purpose. Every session after that repairs one named
flaw and measures whether the repair worked. So:

> **The teaching artifact is the diff between two branches, not the code on any
> one of them.**

The most useful command in this repository is not `python` — it is:

```bash
git diff session-01-start solution/session-01
```

That is the whole of Session 01: 359 lines across two files. Every later session
has the same shape.

---

## 2 · Directory map

```
q3-ai/
├── corpus/          the two source documents. FROZEN — see §5
├── eval/            the question set and the score. The measurement spine
├── src/             the growing library. THIS is what changes week to week
├── sessions/sNN/    per-session codelab guide + the lab as a .py notebook
├── fixtures/        pre-recorded model output, so demos run offline
├── docs/            flaws, decisions, standard, layer ownership, guides
└── tools/           setup check, corpus verification and preparation
```

In more detail, and — more usefully — **who touches what**:

| Path | What it is | You touch it |
|---|---|---|
| `corpus/*.txt` | Kenya DPA and the National AI Strategy, as plain text | **Never.** Frozen and checksum-pinned |
| `corpus/MANIFEST.sha256` | The checksum pin | Never, unless deliberately changing the corpus |
| `eval/questions.yaml` | The evaluation set | **Yes** — you add questions, by pull request |
| `eval/baseline.md` | One row per session: the score and what moved it | Read every week; the score owner writes it |
| `src/pipeline.py` | The pipeline itself | **Yes** — this is the codelab |
| `sessions/sNN/README.md` | The codelab guide for session NN | Read before and during the session |
| `sessions/sNN/lab.py` | The same steps as a runnable notebook | Optional, for replaying at home |
| `docs/flaws.md` | The running list of flaws and who repairs each | Read; tick a row when a score moves |
| `docs/decisions.md` | Every decision, with its reason and date | Written in the room |
| `docs/standard.md` | The engineering standard, one line per session | Written in the room |
| `docs/layer-ownership.md` | Who leads on which layer | Filled in at Session 01 |
| `docs/guides/` | The Study Guides and Content Packs (`.docx`) | Read before each session |
| `tools/` | Facilitator tooling | Rarely; see §6 |
| `fixtures/` | Recorded model output for offline demos | Read |
| `notebooks/` | Generated from `sessions/*/lab.py` | Never — gitignored build artifact |

### Two things that surprise people

- **`src/pipeline.py` does not exist on a `-start` branch.** That is the point:
  it is built live in the room. It appears on `solution/session-NN`. If you check
  out `session-01-start` and `python -m src.pipeline` fails, nothing is broken.
- **`notebooks/` is gitignored.** `.ipynb` is JSON with embedded outputs; it
  diffs badly and merges worse, which would wreck the fix-forward rule in §4.
  The `.py` is the source of truth. Generate notebooks with
  `python tools/build_notebooks.py`.

---

## 3 · The five-layer stack

Every session sits on exactly one layer. When something breaks, the stack is how
the room works out whose problem it is — read top to bottom, and the first "no"
names the layer.

| Layer | Question it answers | Sessions |
|---|---|---|
| 5 · Safety and evaluation | Did anything check the result? | 09, 10 |
| 4 · Protocol and execution | Did it call the right thing, with the right permission? | 06 |
| 3 · Orchestration and state | Did the system take the right next step? | 07 |
| 2 · Context and memory | Was the right passage retrieved? | 04, 05 |
| 1 · Data infrastructure | Is the data present and current? | 02, 03 |

Layer 2 accounts for most failures teams initially blame on the model, and it is
the cheapest to check: print the retrieved chunks.

---

## 4 · Branches and tags

```
session-01-start ──► solution/session-01 ─┐
                                          ├─► session-02-start ──► solution/session-02 ─┐
                                          ┘                                             ├─► …
```

| Name | What it is |
|---|---|
| `session-NN-start` | Everything through Session NN-1, working, plus Session NN's scaffolding and TODOs. Checking it out puts you where the room is at 2:00 PM |
| `solution/session-NN` | A **tag** at the finished state of Session NN |
| `session-01-baseline` | Session 01 only — the branch the room creates live, demonstrating the commit workflow |
| `main` | Tracks the most recently completed session |

**`solution/` tags are movable.** When a bug in Session 02 is found during Session
06, the tag is re-pointed at the corrected commit. A tag here means "the completed
state of Session NN as it now stands", not "an immutable historical commit".

### Because they move, you have to ask for updates

`git pull` will **not** update a tag you already have. Git refuses to overwrite an
existing local tag, and it says nothing when it declines. Clone in August, and you
keep August's `solution/session-02` forever — including the bug that was fixed in
September.

So refresh tags explicitly before each session:

```bash
git fetch --tags --force
```

That one flag is the difference between studying the corrected code and studying a
bug the facilitator believes they fixed weeks ago.

### Checking out a tag detaches HEAD — branch from it instead

`git checkout solution/session-01` works, but it leaves you on **no branch**. Any
commit you make there belongs to nothing, and the next `git checkout` silently
orphans it. It looks like a safe sandbox and it is closer to a scratch pad that
throws your work away.

If you only want to *read* the code, a detached checkout is fine. If you intend to
change anything — and you should, that is the point — start a branch from the tag:

```bash
git switch -c play/your-name solution/session-01
```

Now your work has a name and cannot be lost. To experiment without disturbing your
main clone at all, use a second working directory sharing the same history:

```bash
git worktree add ../q3-play solution/session-01
# ... break things freely ...
git worktree remove ../q3-play
```

> Nothing you do locally can damage the shared repository unless you have push
> access to it. That — not the detached HEAD — is what actually makes experimenting
> safe. Untracked and ignored files (`.venv/`, `notebooks/`, `sources/`) are never
> swapped by a checkout, so they follow you across every branch switch.

### Fix forward, never rebase

Branches are published and cloned. Rebasing breaks every clone. When a bug in an
early session surfaces later:

1. Commit the fix on `session-02-start`
2. Merge forward through each later branch **in order**
3. Re-point the affected `solution/` tags

Tedious, non-destructive, and the only option once people have the code.

---

## 5 · The corpus is frozen, and why that matters to you

Both `.txt` files are committed and pinned by `corpus/MANIFEST.sha256`.

```bash
python tools/verify_corpus.py     # OK / CHANGED / MISSING per file
```

**Do not convert your own copies of the source documents.** Extraction is not
deterministic across tools — two people running different extractors on the same
PDF index different bytes, and every score after that stops being comparable to
the baseline. The pin is what makes ten weeks of numbers one series rather than
ten unrelated measurements.

If the corpus genuinely must change, that is a decision: record it in
[`decisions.md`](decisions.md) and mark the affected row in
[`../eval/baseline.md`](../eval/baseline.md).

---

## 6 · The measurement spine

This is the part that makes the quarter honest, and it is three files.

```
eval/questions.yaml  ──run──►  retrieval accuracy  ──record──►  eval/baseline.md
```

**`eval/questions.yaml` grows and never shrinks.** A question that has failed since
August is the most informative item in the file, not a candidate for removal.

**The baseline is never re-based.** October's score is compared to 5 August's, not
to last week's.

### The `answer` / `expect` rule

Every question carries two fields, and this catches people out:

```yaml
- id: q01
  question: Within how many hours must a data controller notify the Data Commissioner?
  answer: "72 hours"                                    # human-readable, for the board
  expect: ["seventy-two hours", "seventy two hours"]    # what the SCORER matches on
  source: "DPA s.43(1)(a)"
```

Statutes spell numbers out. The Act says *seventy-two hours*; the board says
*72 hours*. Scoring a substring against the board answer returns MISS on a perfect
retrieval. So `answer` is for humans and `expect` is for the machine.

> **Never write `expect` from the canonical publication.** Grep the converted text
> in `corpus/` and copy what is actually there. This is the single most common way
> to produce a wrong score.

```bash
grep -in "seventy" corpus/dpa-2019.txt      # check before you write the question
```

---

## 7 · Commands you will actually use

```bash
# Setup, once
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Before every session
git fetch --tags --force           # --force, or moved solution/ tags never reach you
git checkout session-NN-start
python tools/check_setup.py        # four OK lines
python tools/verify_corpus.py      # the corpus pin still holds

# During and after
python -m src.pipeline                    # load, chunk, index
python -m src.pipeline --ask "..."        # retrieve against one question
python -m src.pipeline --score            # run the eval set, print the number
```

Facilitator-only, from `requirements-dev.txt`:

```bash
python tools/prepare_corpus.py --check-only    # re-report on corpus/*.txt
python tools/build_notebooks.py                # sessions/*/lab.py -> notebooks/
```

---

## 8 · Where to start

**If you are a participant:**

1. Read this file.
2. Read [`sessions/s01/README.md`](../sessions/s01/README.md) — the Session 01
   codelab guide. Then the guide for whichever session is next.
3. Run `python tools/check_setup.py`. Four `OK` lines and you are ready.
4. Read the Study Guide for the coming session in [`docs/guides/`](guides/).

**If you are facilitating:**

1. Everything above, plus [`CONTRIBUTING.md`](../CONTRIBUTING.md) and
   [`CLAUDE.md`](../CLAUDE.md).
2. The "Before the room arrives" checklist at the top of each session's codelab
   guide.
3. [`HANDOFF.md`](../HANDOFF.md) for the current state of play.

**If you missed a session:** check out that session's `solution/` tag and read its
codelab guide. You will be level for the next one — every session starts from a
prepared branch, so nobody is behind because of one Wednesday.

---

## 9 · Comment conventions in the code

The code is teaching material. Comments carry content, but stay to one line each —
anything longer belongs in a session's `README.md`.

| Convention | Use |
|---|---|
| Module docstring | Session number, the plain-language question, the stack layer |
| `# WHY:` | Rationale — especially for choices that are deliberately bad |
| `# FLAW n:` | A named flaw from [`flaws.md`](flaws.md), with the session that repairs it |
| `# DPA s.43:` | This line reflects a specific statutory requirement |
| `# TODO(session-NN):` | A live-coding gap to be filled in the room |

The `# DPA s.NN` anchors are the ones to be strict about. They are what lets a
reader trace a retention rule or a notification deadline from the statute to the
line of code that honours it.
