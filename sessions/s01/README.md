# Session 01 · What Changed

> **The question this session answers**
> *What actually changed in how software is built, and what does it mean for the
> work I already do?*

| | |
|---|---|
| **Date** | Wednesday 5 August 2026 · 2:00–4:00 PM |
| **Module** | Foundations |
| **Stack layer** | 1 (data infrastructure) and 2 (context and memory) — **built badly, on purpose** |
| **Start branch** | `session-01-start` |
| **Finish tag** | `solution/session-01` |
| **Needs** | Python 3.10+. **No API key, no account, no network** after cloning |
| **Repairs** | Nothing. This session *creates* the flaws the quarter repairs |

---

## 1 · What this codelab is for

Most technical series open by demonstrating something impressive. This one opens by
building something bad on purpose.

By 3:50 the room has a pipeline that answers questions about two Kenyan policy
documents, and a measured score showing how often it retrieves the wrong thing.
**That score is the point.** It goes on the board, into the repository, and is
re-run at the start of every remaining session this quarter.

Nobody has to take a facilitator's word for whether re-ranking matters. They watch
the number move, and they can name the line of code that moved it.

You are building four functions and about forty lines of substance:

```
load  ─►  chunk  ─►  index  ─►  retrieve        ...then score it
```

Every one of those makes the laziest defensible choice available. Those choices are
not mistakes. **They are the syllabus.**

---

## 2 · Before you start

```bash
git clone https://github.com/developers-mania/q3-ai.git && cd q3-ai
git checkout session-01-start

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python tools/check_setup.py
python tools/verify_corpus.py
```

You should see exactly this:

```
OK    Python version           3.12.x (need 3.10+)
OK    Dependencies             scikit-learn and PyYAML importable
OK    Corpus present           2 non-empty .txt in corpus/ (need 2 — see corpus/README.md)
OK    Evaluation set           parses, 0 question(s)

Ready. The projector check is the facilitator's, not this script's.
```

```
OK        ai-strategy-2025.txt
OK        dpa-2019.txt
```

> **"0 questions" is correct.** `eval/questions.yaml` is empty on this branch. The
> room writes it at 3:26. An empty set is the starting state, not a broken one.

Following along locally is **optional**. Session 01 is led from the front on one
screen, and participants who watch and think produce the same output. Nobody is
blocked by an environment that will not install.

---

## 3 · Where to look in the repository

| File | What to do with it |
|---|---|
| **`src/pipeline.py`** | **Does not exist yet — you are writing it.** This is the codelab |
| **`eval/questions.yaml`** | **Empty — the room fills it at step 5.** Read the header comment first |
| `eval/baseline.md` | Where the number lands at 3:50 |
| `corpus/dpa-2019.txt` | The Act. Grep it — do not read it end to end |
| `corpus/ai-strategy-2025.txt` | The Strategy |
| `docs/flaws.md` | The running list. Five rows by 3:50 |
| `fixtures/opening-hook.md` | The pre-recorded model answer for the 2:15 hook |
| `sessions/s01/lab.py` | The same six steps as a notebook, for replaying at home |

Everything else — `tools/`, `docs/standard.md`, `CONTRIBUTING.md` — is scaffolding
you can ignore today.

---

## 4 · The six steps

| Time | Step | Who is working |
|---|---|---|
| 3:00 – 3:06 | 1 · Load the corpus | Facilitator |
| 3:06 – 3:14 | 2 · Chunk it badly | Facilitator + room |
| 3:14 – 3:20 | 3 · Index it badly | Facilitator |
| 3:20 – 3:26 | 4 · Retrieve | Facilitator |
| 3:26 – 3:40 | **5 · The room writes the evaluation set** | **Everyone, in groups** |
| 3:40 – 3:50 | 6 · Run it and record the number | Facilitator + room |

**Step 5 is the most important thing that happens today**, and it is the one that
needs no code. Writing an evaluation question with a verifiable answer is a domain
skill. If you are the person in the room who knows what the answer *should* be, you
are not the junior participant — you are Layer 5.

### The rules for a question

1. **The answer must be in the corpus.** A question the documents do not answer
   measures the model's training data, not this system.
2. **The answer must be unambiguous** — a number, a date, a named body, a closed
   list. *"What does the Act say about consent?"* cannot be scored.
3. **The answer must be verifiable in one place, cited by section.** Anyone must be
   able to check it in ten seconds without trusting the author.
4. **At least one question per group must be a near-miss trap** — worded closely to
   a *different* answer elsewhere in the corpus.

### Writing `expect` — read this before step 5

```yaml
- id: q01
  question: >-
    Within how many hours must a data controller notify the Data
    Commissioner of a personal data breach?
  answer: "72 hours"                                     # for the board
  expect: ["seventy-two hours", "seventy two hours"]     # what the scorer matches
  source: "DPA s.43(1)(a)"
```

The Act writes *seventy-two hours*. A substring test against `"72 hours"` scores
**MISS on a perfect retrieval**. So check the corpus before you write the question:

```bash
grep -in "seventy" corpus/dpa-2019.txt
```

> **Never write `expect` from the canonical publication.** Grep the converted text
> and copy what is actually there.

---

## 5 · How to know it worked

Run these. This is the checklist — if all six pass, the session succeeded.

### ✅ 1 — The pipeline loads and chunks

```bash
python -m src.pipeline
```

```
ai-strategy-2025.txt          172,056 characters
dpa-2019.txt                  103,177 characters
chunks                            552
```

**552 chunks.** If your number differs, your corpus differs — run
`python tools/verify_corpus.py` before going further.

### ✅ 2 — Retrieval returns something plausible

```bash
python -m src.pipeline --ask "notification of a personal data breach"
```

Three chunks, each with a similarity score and a source. They should be from
`dpa-2019.txt` and be recognisably about breach notification.

### ✅ 3 — The near-miss pair behaves badly, visibly

This is the demonstration the whole session turns on. Ask both questions:

```bash
python -m src.pipeline --ask "Within how many hours must a data controller notify the Data Commissioner of a personal data breach?"
python -m src.pipeline --ask "Within how many hours must a data processor notify the data controller of a personal data breach?"
```

**Both return the same top chunk** — the one containing the *forty-eight hour*
processor deadline. For the controller question that top-ranked chunk is the
**wrong answer**; the correct *seventy-two hour* chunk comes second.

Read all three chunks aloud for each question and ask the room which is right.
Two questions sharing nearly every content word, one index that cannot tell them
apart. That is Flaw 2 and Flaw 3, discovered rather than asserted.

### ✅ 4 — The evaluation set parses and scores

```bash
python -m src.pipeline --score
```

One `HIT`/`MISS` line per question, then the number.

### ✅ 5 — The number is in the expected band

**Expect 30–55%.**

| Result | What it means | What to do |
|---|---|---|
| 30–55% | As designed | Commit it |
| Below 30% | Usually an `expect` problem, not retrieval | Grep the corpus for the exact phrasing |
| **Above 70%** | **The questions were too easy** | **Harden them before committing** |

> A flattering baseline is a failure, not a good session. Every improvement for the
> next nine weeks is measured against this number. Buying one comfortable afternoon
> costs nine weeks of measurement.
>
> Watch for this specifically: questions phrased in the Act's *own* vocabulary
> ("notify", "Data Commissioner", "breach") are exactly what a keyword index is good
> at, and a set built only from those will flatter. Paraphrases and near-miss traps
> are what pull the number honestly down.

### ✅ 6 — Four things are recorded before the room empties

| | Lands in |
|---|---|
| The score, with the date and question count | `eval/baseline.md` |
| Five flaws, each with an owning session | `docs/flaws.md` |
| Layer ownership — named people | `docs/layer-ownership.md` |
| The Session 03 topic decision **and its one-sentence reason** | `docs/decisions.md` |
| Standard 1 of 10 | `docs/standard.md` |

Then commit, live, on the projector — this is also the demonstration of the
workflow:

```bash
git checkout -b session-01-baseline
git add src/pipeline.py eval/questions.yaml eval/baseline.md docs/
git commit -m "session 01: naive pipeline, 20-question eval set, baseline score"
git push -u origin session-01-baseline
```

---

## 6 · The five flaws you will have created

Written on the board as each is named. **This list is the syllabus** — nobody had
to decide what to teach next; the flaws named themselves as soon as the thing ran.

| # | Flaw | Named at step | Repaired in |
|---|---|---|---|
| 1 | Chunks cut across meaning | 2 | Session 03 |
| 2 | The index matches words, not meaning | 3 | Session 04 |
| 3 | No re-ranking — the first plausible match wins | 4 | Session 05 |
| 4 | No confidence threshold — never says "I don't know" | 4 | Session 09 |
| 5 | Chunks carry no section number, so no answer can be cited | 4 | Session 03 |
| — | The corpus is two static files a human downloaded | 1 | Session 02 |

Flaws 1 and 5 share an owner because they are the same flaw seen from two angles:
a chunk that respects section boundaries is also a chunk that knows which section
it came from.

---

## 7 · What you should be able to explain afterwards

If you cannot answer these without looking, re-read the Study Guide.

- Why a model that answers confidently and wrongly is a **retrieval** problem
  before it is a model problem.
- Why you cannot unit-test your way to confidence in a non-deterministic system,
  and what replaces the assertion.
- What TF-IDF actually computes, and the one thing it structurally cannot do.
- Why the score measures **retrieval** rather than answer quality — and what that
  buys (determinism, no key, no network) and what it gives up.
- Given a wrong answer, which layer to check first, and why that one.

---

## 8 · If it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: sklearn` | venv not active | `source .venv/bin/activate`, reinstall |
| `python -m src.pipeline` → no module | You are on `session-01-start` | Correct. It is built live; use `solution/session-01` to see it finished |
| `CHANGED` from `verify_corpus.py` | Corpus edited, or CRLF | `git checkout -- corpus/` and re-run |
| Chunk count ≠ 552 | Different corpus bytes | `python tools/verify_corpus.py` |
| Everything scores MISS | `expect` written from the publication, not the corpus | `grep -in "<phrase>" corpus/dpa-2019.txt` |
| Score is suspiciously high | Questions too easy | Harden them — see §5 check 5 |

---

## 9 · Before Session 02

- **Re-run today's pipeline** on your own machine if you did not follow along live.
  The branch is `session-01-baseline`.
- **Write two more evaluation questions** and open a pull request against
  `eval/questions.yaml`. The set grows all quarter; it never shrinks.
- **Read section 43 of the Act in full** — all subsections. It is one page and it
  is the source of half of today's near-miss traps.
- **Skim the three pillars and four enablers** of the National AI Strategy. Ten
  minutes.
- **Bring one sentence:** a place in your own work where a system currently answers
  confidently and might be wrong.

**Next:** [Session 02 · Where The Data Comes From](../s02/README.md) — the pipeline
reads two static files somebody downloaded by hand. That works exactly once.
