# Session 03 · Getting Data Ready

> **The question this session answers**
> *What shape does data need to be in before a model can use it — and what has to be
> stripped out first?*

| | |
|---|---|
| **Date** | Wednesday 19 August 2026 · 2:00–4:00 PM |
| **Module** | 1 · Data Infrastructure and Pipelines (**closing session**) |
| **Stack layer** | 1 into 2 |
| **Start branch** | `session-03-start` |
| **Finish tag** | `solution/session-03` |
| **Needs** | Python 3.10+. `spacy` optional. Still **no key, no account, no network** |
| **Repairs** | **Flaw 1** (chunks cut across meaning); completes **Flaw 5** (citation precision) |

---

## 1 · What this codelab is for

Two halves that teach opposite lessons.

**First half — cutting on meaning.** Session 01 cut the corpus into 500-character
pieces chosen for no reason at all. Session 02 built a parser that knows where every
subsection begins and ends, and deliberately left the cutting alone. Today they meet,
and **citation accuracy goes from 8% to 38%** — by doing *less*, not more. No new
model, no new index. Just cutting where the document says to cut.

**Second half — the failure nobody expects.** The room adds a redaction step, does it
competently, and watches the numbers move the wrong way — because a rule written to
protect people deleted the subject of half the evaluation set. Nothing errors. The
pipeline reports success. **Only the measurement notices.**

> The chunk is the **smallest addressable unit in the entire system**. A chunk cut
> through the middle of an answer cannot be repaired by a better embedding model, a
> better re-ranker, or a better prompt — the information is not there. Session 05's
> re-ranker cannot recover an answer destroyed in Session 01.
>
> **Chunking is the one decision that later sophistication cannot compensate for.**

---

## 2 · Working through this on your own

```bash
git clone https://github.com/developers-mania/q3-ai.git && cd q3-ai
git fetch --tags --force
git switch -c play/your-name solution/session-03

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python sessions/s03/lab.py
```

That last command is the whole session: the structure-aware cut, the overlap sweep,
recall against the fixture, precision against the corpus, the naive rule doing its
damage, and the recovery. About two minutes to run.

> **Which branch?** `solution/session-03` to read or replay. `session-03-start` to
> type it yourself — there `src/chunk.py` and `src/redact.py` do not exist yet.
> `git diff session-03-start solution/session-03` is the lesson.

---

## 3 · Before you start (in the room)

```bash
git fetch --tags --force && git checkout session-03-start
source .venv/bin/activate
pip install -r requirements.txt

python -m src.ingest --verify      # manifest still clean?
python -m src.evaluate --questions eval/seed-questions.yaml
```

**Put both Session 02 numbers on the board before anything is built** — retrieval
53%, citation 8%. Today moves both, and the second one moves sharply.

> This is the third week of re-running the evaluation set and the discipline should
> now be automatic. If someone asks why it runs when nothing has changed — that is
> the right question, and the answer is that you cannot attribute a movement to a
> change unless you know the starting point was stable.

---

## 4 · Where to look in the repository

| File | What to do with it |
|---|---|
| **`src/chunk.py`** | **New.** Walks the Session 02 parse tree and cuts on it |
| **`src/redact.py`** | **New.** Patterns, and the false-positive measurement |
| `fixtures/complaint-synthetic.txt` | A **fabricated** complaint with planted identifiers |
| `src/ingest.py` | Gains `--overlap` and `--redact` |
| `src/parse.py` | Read it — today's chunker consumes its tree |
| `docs/decisions.md` | Two decisions land here: the overlap value and the redaction policy |

> **The fixture is synthetic and must be introduced as such.** Invented names, an
> invalid ID format, telephone numbers in unallocated ranges, and email addresses on
> `example.com` — which RFC 2606 reserves precisely so it can never be a real
> address. A room learning about personal data should not be handed a file that could
> plausibly contain any.

---

## 5 · The six steps

| Time | Step | Effect on the numbers |
|---|---|---|
| 3:00 – 3:14 | 1 · Structure-aware chunking | **citation 8% → 38%** |
| 3:14 – 3:22 | 2 · Measure three overlap settings | decides a parameter |
| 3:22 – 3:30 | 3 · Pattern redaction on the fixture | none yet — fixture only |
| 3:30 – 3:38 | **4 · Run redaction on the real corpus** | **down. This is the lesson** |
| 3:38 – 3:44 | 5 · Measure the false positive rate | full recovery |
| 3:44 – 3:50 | 6 · What a pattern structurally cannot do | — |

### Three cases the chunker must handle

| Case | Example | Handling |
|---|---|---|
| Fits comfortably | s.43(3), one sentence | Emit as one chunk. The common case |
| Too small | a one-line definition in s.2 | Merge with siblings — **never across sections** |
| **Too large** | s.25, the eight principles | Subdivide **within** the unit; every piece keeps the citation |

Never merging across sections is not fussiness: a merged chunk carries only one
citation, so joining s.43(3) to s.44(1) would cite half its content wrongly — the
exact failure Session 02 measured.

> `MAX_CHARS` is a **ceiling, not a target**. In fixed-size chunking the size
> parameter governs every chunk. Here most subsections are naturally short and never
> approach it, so it only governs the handful of oversized sections — a much smaller
> and more predictable effect, and it changes how you tune it.

---

## 6 · How to know it worked

> **Two instruments, never mixed.** Every number in this section is measured against
> `eval/seed-questions.yaml`, so they are comparable with each other. The **cohort
> baseline** is a different, larger set — `eval/questions.yaml`, twenty questions —
> recorded in [`eval/baseline.md`](../../eval/baseline.md). On that set Session 03
> scores **45% retrieval, 33% citation**, against Session 02's 50% and 17%.

### ✅ 1 — The passage Session 02 got wrong is now right

```bash
python -m src.ingest --overlap 0 && python -m src.evaluate --questions eval/seed-questions.yaml
```

The chunk containing the 48-hour deadline was tagged `DPA s.43(2)` last week. It is
now **exactly `DPA s.43(3)`** — beginning at "A data processor shall notify" and
ending at the end of that subsection.

| | Session 02 | Session 03 (overlap 0) |
|---|---|---|
| Retrieval | 53% | 47% |
| **Citation** | **8%** | **38%** |

The near-miss pair from Session 01 can be told apart **by citation** for the first
time.

### ✅ 2 — Overlap is chosen by measurement, not by default

```bash
for n in 0 50 100 200 300; do python -m src.ingest --overlap $n >/dev/null && \
  python -m src.evaluate --questions eval/seed-questions.yaml --quiet; done
```

| Overlap | Chunks | Retrieval | Citation |
|---|---|---|---|
| 0 | 558 | 47% | **38%** |
| 50 | 564 | 53% | 31% |
| **100** | **571** | **73%** | **31%** |
| 200 | 587 | 80% | 31% |
| 300 | 606 | 80% | 31% |

**Ask the room to predict first.** The expectation — stated in the Study Guide — is
that overlap should matter *less* once cutting is semantic, because answers no longer
straddle boundaries at random.

**The prediction is wrong here, and that is why it was measured.** Overlap buys a lot
of retrieval and costs citation, and the mechanism is visible once stated: a chunk
beginning with its neighbour's tail can match a query on **borrowed text**, so the
answer is retrieved (retrieval up) from a chunk whose citation belongs to the passage
next door (citation down).

There is no setting that maximises both. **100 is the recorded choice** — the
smallest value that moves *both* numbers above Session 02, with the corpus growing
for nothing beyond 200. Recorded, with the trade, in `docs/decisions.md`.

> A parameter chosen by measurement is a decision. A parameter chosen by default is
> an accident that has not caused a problem yet.

### ✅ 3 — Recall: the fixture is cleaned

```bash
python -c "from pathlib import Path; from src.redact import *; print(redact(Path('fixtures/complaint-synthetic.txt').read_text(encoding='utf-8'), PATTERNS)[1])"
```

```
{'PHONE_KE': 4, 'EMAIL': 4, 'ID_KE': 2}
```

Every planted identifier removed. This is the rate everyone measures.

### ✅ 4 — Precision: and the corpus is destroyed

**This is the rate almost nobody measures.** The Act and the Strategy are public
documents; the Data Commissioner is named by *office*, not by name. So on this
corpus **every hit is a false positive by construction**, and the count *is* the
damage.

| Pattern | Hits on corpus | FP rate |
|---|---|---|
| `PHONE_KE` | 0 | 0% |
| `EMAIL` | 2 | 100% |
| `ID_KE` (labelled) | 0 | 0% |
| **`NAME_NAIVE`** | **739** | **100%** |
| `NAME_NARROW` | 2 | 100% |

**Stop here and let the room work out what happened.** The well-shaped patterns cost
almost nothing. The naive two-capitalised-words name rule fires 739 times, and not
one of them is a person:

```
  80x  Data Commissioner
  40x  Data Protection
  31x  The Data
  16x  Flagship Projects
  11x  Cabinet Secretary
```

`Data Commissioner` — 80 times in the Act alone, and the subject of most of the
evaluation set. **A rule written to protect people is about to delete the subject of
half the questions.**

| | Retrieval | Citation |
|---|---|---|
| Before redaction | 73% | 31% |
| **After the naive name rule** | **67%** | **23%** |

The pipeline reported success. Every stage ran cleanly. The output looks well-formed.
**Only the score noticed.** That is the third time this quarter measurement has caught
something no test would have raised.

> **A caution worth showing the room.** At `--overlap 0` the same destructive rule
> makes retrieval go *up* (47% → 53%) while citation still falls. A change that
> deletes 739 pieces of the corpus can move a metric the flattering way by accident.
> This is exactly why you look at **which questions flipped**, not at the number.

### ✅ 5 — Narrowing recovers everything

```python
# Before: any two capitalised words
NAME_NAIVE  = r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"

# After: require the context a person is actually introduced in
NAME_NARROW = r"\b(?:[Cc]omplainant|[Aa]pplicant|Mr|Mrs|Ms|Dr)\.?,?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})"
```

| | Retrieval | Citation |
|---|---|---|
| No redaction | 73% | 31% |
| Naive name rule | 67% | 23% |
| **Narrowed rule** | **73%** | **31%** |

**Full recovery**, and the narrowed rule still catches every planted name in the
fixture. It genuinely catches *less* — an unlabelled name walks straight through —
and **that trade is the decision the room is making**, not a detail.

### ✅ 6 — Two findings the measurement produced that nobody predicted

**A `(?i)` flag silently widened the pattern.** The narrowed rule was first written
`r"(?i)\b(?:complainant|mr|dr)\.?,?\s+([A-Z][a-z]+...)"`. The inline flag applies to
the *whole* pattern, so `[A-Z][a-z]+` matched lowercase too — and the phrase
"applicant is false or" became a person named *"is false or"*. An inline flag
quietly widening the half of a pattern you meant to keep strict is easy to ship and
hard to see.

**The corpus is not quite free of personal data.** The narrowed rule's two remaining
hits are `Melissa Omino` and `Nyawira Gitahi` — real contributors credited in the
Strategy's acknowledgements. So the premise of the precision measurement, *this
corpus contains no personal data*, is **almost** true and not quite. The Act contains
none. The Strategy names people.

Nobody predicted that. The measurement found it.

---

## 7 · The decision this room owns

The narrowed rule catches fewer real identifiers. The broad rule destroys corpus
content. **There is no setting that does neither**, and the choice depends on what
the corpus is.

| Corpus kind | Correct rule | Why |
|---|---|---|
| Reference corpus of public documents | **narrow** | Compliance risk near zero; content loss real and measurable |
| Corpus containing user records | **broad** | Content loss is an acceptable price for a real exposure |

What is never correct is choosing without knowing which kind you have, or shipping
either rule without measuring both rates. **In Session 09 the same question returns
as a confidence threshold, and this entry is what makes that conversation short.**

---

## 8 · What you should be able to explain afterwards

- Why a better embedding model, re-ranker or prompt **cannot** repair a bad chunk.
- Why this corpus takes structure-aware chunking and the AI Strategy does not — and
  why a Slack export would correctly take recursive character splitting.
- The two error rates of a redaction rule, and why **precision** is the one almost
  nobody measures.
- Why redaction runs at **ingestion** and not at query time. *"By design"* in s.41 is
  a timing requirement — a filter on results still leaves identifiers in the index,
  and the index is the copy that persists.
- The difference between *"we redact personal data"* and *"the index contains no
  personal data"* — and why only the first is defensible.

> Named entity recognition over-redacts too: run it over the Act and it will take
> "Kenya" as a location and possibly "Data Commissioner" as an organisation. Same
> failure, harder route — a regex can be read and narrowed in a minute; a model's
> decision cannot be inspected at all. **The risk of a redaction step is proportional
> to how little you have measured it, and a model-based step is harder to measure
> than a rule, not easier.**

---

## 9 · If it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| Citation accuracy barely moves | Chunker still cutting by character | Confirm it walks the tree, not the string |
| A chunk spans two sections | Merging across parents | Merge only within a section |
| Score changes in ways redaction cannot explain | Redacting *before* chunking shifts every parse offset | Redact the chunk text, not the text the offsets index into |
| Redaction has no effect on the score | Applied to retrieval results, not ingestion | It must run before indexing — s.41 is a timing requirement |
| A "person" called `is false or` | `(?i)` applied to the whole pattern | Scope the case-insensitivity to the trigger words only |
| `spacy` download fails | No network | Skip step 6 — the point survives without the code |

---

## 10 · Before Session 04

- Re-run the pipeline and confirm your chunk count matches the room's (**571** at the
  chosen overlap of 100).
- Read **section 41** of the Act and identify the line in `src/redact.py` that
  responds to it.
- **Add two evaluation questions phrased in your own words**, deliberately avoiding
  the Act's vocabulary. These are the questions the keyword index fails and Session
  04 should fix — the four `p0*` questions in the seed set still miss.
- Bring one redaction rule from your own work and an estimate of its false positive
  rate. **If you cannot estimate it, that is the finding.**

**Next:** [Session 04 · Giving Software Memory](../s04/README.md) — Module 1 closes.
The corpus is structured, cited, cut on meaning and cleaned. The index is still the
keyword matcher from 5 August, and it still has no idea what words mean.
