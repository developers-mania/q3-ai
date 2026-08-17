# Session 03 · Getting Data Ready

> **The question this session answers**
> *What shape does data need to be in before a model can use it — and what has to be
> stripped out first?*

| | |
|---|---|
| **Date** | Wednesday 19 August 2026 · 2:00–4:00 PM |
| **Module** | 1 · Data Infrastructure and Pipelines (**closing session**) |
| **Stack layer** | 1 into 2 |
| **Start branch** | `session-03-start` (= `solution/session-02` + a synthetic complaint fixture) |
| **Finish tag** | `solution/session-03` |
| **Needs** | Python 3.10+. `spacy` optional. Still no key, no account, no network |
| **Repairs** | Flaw 1 (chunks cut across meaning); completes Flaw 5 (citation precision) |

---

## 1 · What this codelab is for

This is the session the whole first half has been building toward, and it has two
halves that teach opposite lessons.

**First half — cutting on meaning.** Session 01 cut the corpus into 500-character
pieces chosen for no reason at all. Session 02 built a parser that knows where every
section begins and ends, but deliberately left the cutting alone. Today those meet.
**This is expected to produce the largest single movement in the score of the entire
quarter** — and it does so by doing *less*, not more. No new model, no new index.
Just cutting where the document says to cut.

**Second half — the failure nobody expects.** The room adds a redaction step, does it
competently, and **watches the score go down** — because a rule tuned for one kind of
data destroyed another kind. Nothing errors. The pipeline reports success. Only the
measurement notices.

> Both halves matter. **The second is the one people remember.**

### The two directions redaction fails

| Direction | What happens | Who anticipates it |
|---|---|---|
| **Under-redaction** | Personal data reaches the index, and from there possibly a model provider abroad | Everybody |
| **Over-redaction** | A pattern matching 7–8 digit numbers redacts `5000000` from s.63 — the maximum administrative fine — and the system can no longer answer a question it answered correctly on 5 August | Almost nobody |

In *this* corpus — two public policy documents containing essentially no personal
data — **over-redaction is the dangerous one.** Which is why this session does
redaction last and re-runs the evaluation set immediately afterwards.

---

## 2 · Before you start

```bash
git fetch && git checkout session-03-start
source .venv/bin/activate
pip install -r requirements.txt        # nothing new required this week

# Optional, for the named entity recognition demo only (~12 MB):
pip install spacy && python -m spacy download en_core_web_sm

python tools/verify_corpus.py
python -m src.ingest --verify          # manifest still clean?
python -m src.evaluate                 # both numbers, unchanged from 12 August
```

**Put both numbers on the board before anything is built.** This is the third week
of re-running the evaluation set and the discipline should now be automatic.

> If someone asks why it is run before every session when nothing has changed — that
> is the right question. The answer: you cannot attribute a movement to a change
> unless you know the starting point was stable.

---

## 3 · Where to look in the repository

| File | What to do with it |
|---|---|
| **`src/chunk.py`** | **New.** Walks the Session 02 parse tree and cuts on it |
| **`src/redact.py`** | **New.** Pattern redaction, and the false-positive measurement |
| `fixtures/complaint-synthetic.txt` | A **fabricated** complaint with invented names, phone and ID numbers |
| `src/parse.py` | Read it — today's chunker consumes its tree |
| `docs/decisions.md` | Two decisions land here: the overlap value and the redaction policy |
| `eval/questions.yaml` | Add two questions phrased in **your own words**, avoiding the Act's vocabulary |

> **On the fixture:** it must be *obviously* synthetic — invented names, invalid ID
> formats, phone numbers in unallocated ranges. Say so aloud when it is introduced. A
> room learning about personal data should not be handed a file that could plausibly
> contain any.

---

## 4 · The six steps

| Time | Step | Effect on the numbers |
|---|---|---|
| 3:00 – 3:14 | 1 · Structure-aware chunking | **Both up, citation sharply** |
| 3:14 – 3:22 | 2 · Measure three overlap settings | Small; decides a parameter |
| 3:22 – 3:30 | 3 · Pattern redaction on the fixture | None yet — fixture only |
| 3:30 – 3:38 | **4 · Run redaction on the real corpus** | **Down. This is the lesson** |
| 3:38 – 3:44 | 5 · Measure the false positive rate | Recovers most of the loss |
| 3:44 – 3:50 | 6 · Named entities, and what remains | — |

### Three cases the chunker must handle

| Case | Example | Handling |
|---|---|---|
| Fits comfortably | s.43(3), one sentence | Emit as one chunk. The common case |
| Too small | A one-line definition in s.2 | Emit anyway, or merge with siblings — **never across parents** |
| **Too large** | s.25, the eight principles, running to pages | Subdivide **within** the unit; every piece keeps the parent citation |

The third is why structure-aware chunking is not simply "one chunk per section". A
split s.25 produces three chunks all correctly cited `DPA s.25` — less precise than
a subsection, and enormously better than three chunks cited to nothing.

> `MAX_CHARS` is a **ceiling, not a target.** In fixed-size chunking the size
> parameter governs every chunk. Here it governs only the handful of oversized
> sections — a much smaller and more predictable effect.

---

## 5 · How to know it worked

### ✅ 1 — The same chunk, read again, is now clean

Before today, chunk 847 read:

```
citation: DPA s.43
text: "...ays of the receipt of the notification. (3) A data processor shall
notify the data controller without delay, within forty eight hours of becoming
aware of a personal data breach. 44. (1) Where a data controller or data
processor processes sensitive personal data, the data controlle..."
```

Three failures in five lines: it starts inside the word "days", it contains the end
of s.43 **and** the beginning of s.44, and it is cited `DPA s.43` even though a
question answered from its last sentence belongs to s.44 entirely.

Print the chunk containing the 48-hour deadline now:

```bash
python -m src.inspect --citation "DPA s.43(3)"
```

It must be **exactly** subsection 43(3) — beginning at "A data processor shall
notify", ending at the end of that subsection, cited `DPA s.43(3)`.

### ✅ 2 — Both numbers move, citation sharply

```bash
python -m src.evaluate
```

| Measure | Expectation |
|---|---|
| Retrieval accuracy | Up — likely the largest single jump of the quarter |
| **Citation accuracy** | **Up sharply** — this is the headline |

Citation is the headline because the near-miss pair from Session 01 can now be told
apart **by citation** for the first time.

### ✅ 3 — Overlap is chosen by measurement, not by default

```bash
python -m src.evaluate --overlap 0
python -m src.evaluate --overlap 100
python -m src.evaluate --overlap 300
```

| Overlap | Chunks | Retrieval | Citation | Verdict |
|---|---|---|---|---|
| 0 | | | | |
| 100 | | | | |
| 300 | | | | |

**Ask the room to predict before running.** The likely finding: with chunks already
cut on section boundaries, overlap buys much less than it did in Session 01, because
answers no longer straddle boundaries at random. The right answer here may well be
**zero**, which would have been clearly wrong two weeks ago.

> A parameter chosen by measurement is a decision. A parameter chosen by default is
> an accident that has not caused a problem yet. **Record the value and the reason in
> `docs/decisions.md`.**

### ✅ 4 — Redaction catches everything in the fixture

```bash
python -m src.redact fixtures/complaint-synthetic.txt
```

```
PHONE_KE   4
EMAIL      3
ID_KE      2
→ all identifiers in the fixture removed
```

### ✅ 5 — And then breaks the real corpus, visibly

```bash
python -m src.ingest --redact && python -m src.evaluate
```

```
redaction hits:  PHONE_KE 0   EMAIL 0   ID_KE 31
```

**Stop here and let the room work out what happened.** Zero phone numbers, zero
emails, and thirty-one identity-number hits in two public policy documents that
contain no national identity numbers whatsoever.

Ask: *what in a statute looks like a seven-to-eight-digit number?* Let them find it.
Then print the affected passages and read one aloud. **At least one evaluation
question that passed at 3:14 will now fail.**

The pipeline reported success. Every stage ran cleanly. The only thing that revealed
the damage was the score.

### ✅ 6 — The false positive rate is measured, and the narrowed rule recovers it

```python
# Before: any 7-8 digit number
ID_KE = r"\b\d{7,8}\b"

# After: require the context a real ID appears in
ID_KE = r"(?i)\b(?:national\s+id|id\s+(?:no|number))\D{0,10}(\d{7,8})\b"
```

Re-run both:

| Target | Expected |
|---|---|
| The fixture | Identifiers **still caught** — they appear labelled, "National ID: 34820192" |
| The corpus | Hits drop to **zero** |
| The score | **Recovers to its 3:14 value** |

The corpus gives an unusually clean measurement: it is known to contain no personal
data, so **every hit is a false positive by construction.** Thirty-one hits means
thirty-one pieces of statute destroyed for no compliance benefit.

The narrowed rule genuinely catches less — an unlabelled ID now passes through. **That
trade is the decision the room is making.** Record both rules and both measurements.

### ✅ 7 — Recorded before the room empties

| Stage | Retrieval | Citation |
|---|---|---|
| 5 Aug baseline | | n/a |
| 12 Aug — ingestion | | |
| 19 Aug — after chunking | | |
| 19 Aug — after redaction | | |
| 19 Aug — after narrowing | | |

Plus the overlap value and its reason, the redaction policy and its reason, and
standard 3 of 10.

---

## 6 · The decision this room owns

The narrowed rule catches fewer real identifiers. The broad rule destroys corpus
content. **There is no setting that does neither**, and the choice depends on what
the corpus is.

| Corpus kind | Correct rule | Why |
|---|---|---|
| Reference corpus of public documents | **Narrow** | Compliance risk near zero; content loss real and measurable |
| Corpus containing user records | **Broad** | Content loss is an acceptable price for a real exposure |

What is never correct is choosing without knowing which kind you have, or shipping
either rule without measuring both rates. Record which this corpus is, which rule was
chosen, and why. **In Session 09 the same question returns as a threshold decision,
and this entry is what makes that conversation short.**

---

## 7 · What you should be able to explain afterwards

- Why a better embedding model, re-ranker or prompt **cannot** repair a bad chunk.
  Chunking is the one decision later sophistication cannot compensate for.
- Why this corpus takes structure-aware chunking — and why a Slack export would
  correctly take recursive character splitting instead.
- The two error rates of a redaction rule, and why **precision** is the one almost
  nobody measures.
- Why redaction runs at **ingestion** and not at query time. ("By design" in s.41 is
  a *timing* requirement — a filter on results still leaves the identifiers in the
  index, and the index is the copy that persists.)
- The difference between *"we redact personal data"* and *"the index contains no
  personal data"* — and why only the first is defensible.

> Named entity recognition over-redacts too: run it over the Act and it will redact
> "Kenya" as a location and possibly "Data Commissioner" as an organisation. Same
> failure, arriving by a harder route — a regex can be read and narrowed in a minute;
> a model's decision cannot be inspected at all.

---

## 8 · If it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| Chunk count explodes | Every tiny definition emitted alone | Merge small siblings under the same parent |
| Citation accuracy barely moves | Chunker still cutting by character | Confirm it walks the tree, not the string |
| A chunk spans two sections | Subdivision lost the parent citation | Every piece inherits the parent's citation |
| Score does **not** fall after redaction | Redaction not in the ingestion path | It must run before indexing, not on results |
| `spacy` model download fails | No network | Skip step 6 — the point survives without the code |

---

## 9 · Before Session 04

- Re-run the pipeline and confirm your chunk count matches the room's.
- Read **section 41** of the Act and identify the line in `src/redact.py` that
  responds to it.
- **Add two evaluation questions phrased in your own words**, deliberately avoiding
  the Act's vocabulary. These are the questions the keyword index will fail and
  Session 04 should fix.
- Bring one redaction rule from your own work, and an estimate of its false positive
  rate. **If you cannot estimate it, that is the finding.**

**Next:** [Session 04 · Giving Software Memory](../s04/README.md) — Module 1 closes.
The corpus is structured, cited, cut on meaning and cleaned. The index is still the
keyword matcher from 5 August, and it still has no idea what words mean.
