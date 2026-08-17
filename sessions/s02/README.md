# Session 02 · Where The Data Comes From

> **The question this session answers**
> *How does data get into a system reliably, and what breaks when it doesn't?*

| | |
|---|---|
| **Date** | Wednesday 12 August 2026 · 2:00–4:00 PM |
| **Module** | 1 · Data Infrastructure and Pipelines |
| **Stack layer** | 1 — data infrastructure |
| **Start branch** | `session-02-start` (= `solution/session-01` + a `raw/` directory) |
| **Finish tag** | `solution/session-02` |
| **Needs** | Python 3.10+, `pydantic`. Still **no key, no account, no network** |
| **Repairs** | Flaw 5 (passages carry no section number) and Flaw 6 (corpus is two hand-downloaded files) |

---

## 1 · What this codelab is for

Every failure so far has been visible. A wrong answer is wrong on the screen; a bad
score is a bad number on the board.

**This session is about the failure that produces no symptom at all.**

When a source document changes and the index does not, the system keeps answering —
fluently, confidently, in the same tone it uses when it is right — from a version of
the truth that no longer exists. Nothing logs it. No test catches it. And the
evaluation score does not move, *because the evaluation set was written against the
old version too.*

Session 01 established measurement as the discipline that catches problems.
Staleness is the failure that defeats measurement, because the instrument and the
system are wrong in the same direction at the same time.

> **Set expectations now: retrieval accuracy will barely move today.** Say it out
> loud before the number appears, so it lands as a prediction confirmed rather than
> a disappointment. What this session delivers is a corpus that is *trustworthy and
> citable* — the precondition for Sessions 03 and 04 to work at all.

---

## 2 · Before you start

```bash
git fetch && git checkout session-02-start
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # adds: pydantic

python tools/check_setup.py
python tools/verify_corpus.py
python -m src.pipeline --score     # last week's number, unchanged
```

### Re-run the baseline before building anything

Put last week's number on the board next to today's date. **It should be
identical**, because nothing has changed.

That is the point. The first re-run establishes that the measurement is stable and
reproducible. **If it is not identical, stop and find out why** — an evaluation that
drifts on its own is worthless for the next eight weeks.

---

## 3 · Where to look in the repository

| File | What to do with it |
|---|---|
| **`src/ingest.py`** | **New.** Manifest and change detection |
| **`src/parse.py`** | **New.** The Act as a tree of parts, sections, subsections |
| **`src/passage.py`** | **New.** The pydantic boundary contract |
| **`src/publish.py`** | **New.** Validation and the quarantine path |
| `manifest.json` | Provenance: source, publisher, version, retrieval date, hash |
| `quarantine.jsonl` | Rejected records, with reasons. **Open it and read it** |
| `raw/` | The source documents as retrieved |
| `src/pipeline.py` | Mostly unchanged — chunking stays naive on purpose (see §5) |
| `eval/questions.yaml` | Add two questions whose answers sit in a *subsection* |

---

## 4 · The six steps

| Time | Step | Repairs |
|---|---|---|
| 3:00 – 3:08 | 1 · Manifest and change detection | Flaw 6 |
| 3:08 – 3:22 | **2 · Parse the Act into its structure** | Groundwork for Flaw 1 |
| 3:22 – 3:32 | 3 · The passage record and its schema | Flaw 5 |
| 3:32 – 3:40 | 4 · Boundary validation and quarantine | — |
| 3:40 – 3:45 | 5 · Idempotent publish | — |
| 3:45 – 3:50 | 6 · Re-run, and meet the second number | — |

### Step 2 is the long one, and it will not parse cleanly first time

**That is intended.** Legal text is irregular. Budget five of the fourteen minutes
for the room to find failures and argue about them — that argument *is* the session.

Three things in this corpus specifically will break a naive parser. They are worth
knowing in advance so the argument is productive rather than a hunt:

| Trap | What you will see |
|---|---|
| **Part headings are title case with a plain hyphen** | The text reads `Part IV - PRINCIPLES AND OBLIGATIONS`, not `PART IV — …`. A regex anchored on uppercase `PART` and an em-dash matches **nothing**. All 11 parts are there — the pattern is wrong, not the corpus |
| **Every section number appears twice** | Once in the contents page (with dot leaders), once in the body. A naive `^\d+\.\s` finds **150 markers for 75 sections**, and the first `43.` it hits is the contents entry |
| **Sub-paragraph roman numerals collide with part numbering** | `(ii)` in a list, `Part II` in a heading |

```bash
grep -n "^Part " corpus/dpa-2019.txt      # 22 hits: 11 in contents, 11 in the body
```

---

## 5 · Why chunking deliberately does NOT change today

Passages are still cut at fixed 500-character intervals. They simply now carry the
section they fell inside.

Cutting on section boundaries is **Session 03's job**, and separating the two is
what makes next week's improvement measurable in isolation. If both changed in the
same week, the movement in the score could not be attributed to either.

It also produces the specific, visible failure that motivates Session 03: a
500-character chunk straddling the boundary between s.43(1) and s.43(2) can only be
tagged with **one** of them. Citation accuracy will be poor for exactly this
reason, and the room will have measured the problem before being offered the fix.

---

## 6 · How to know it worked

### ✅ 1 — Change detection catches a doctored source

```bash
sed -i "s/seventy-two hours/twenty-four hours/" raw/dpa-2019.txt
python -m src.ingest --verify
```

It must **refuse to proceed and name the file that drifted**. Then restore it:

```bash
git checkout -- raw/
```

The system has not become smarter. It has become capable of noticing, which it
previously was not.

### ✅ 2 — The parser resolves to the subsection, not just the section

```bash
python -m src.inspect --citation "DPA s.43(3)"
```

**This is the check that decides whether citation accuracy means anything.** The
evaluation set cites the 72-hour deadline to `s.43(1)(a)` and the 48-hour one to
`s.43(3)`. If the parser resolves only to `DPA s.43`, both near-miss questions score
as citation hits and the metric collapses into flattery.

> Resolve to the subsection, or do not report citation accuracy at all.

### ✅ 3 — Every passage validates, and failures are quarantined not lost

```bash
python -m src.ingest
```

```
accepted 1,8xx  quarantined N
```

Then **open `quarantine.jsonl` and read three entries aloud.** Some will be
genuinely malformed input that has been sitting in the index since 5 August.

Break it on purpose: add a required field to `Passage` that the parser does not
produce, re-run, and confirm *everything* lands in quarantine with nothing lost.

### ✅ 4 — The pipeline is idempotent

```bash
python -m src.ingest && wc -l passages.jsonl
python -m src.ingest && wc -l passages.jsonl      # identical
```

The count is the **weak** test. The strong test is that the set of identifiers is
identical — that catches the case where the same number of passages is produced with
different identities:

```bash
python -m src.ingest && cut -d'"' -f4 passages.jsonl | sort > /tmp/a
python -m src.ingest && cut -d'"' -f4 passages.jsonl | sort > /tmp/b
diff /tmp/a /tmp/b && echo "IDEMPOTENT"
```

### ✅ 5 — Both numbers are on the board

```bash
python -m src.evaluate
```

| Measure | Expected |
|---|---|
| **Retrieval accuracy** | **Roughly unchanged from 5 August.** Predicted out loud in advance |
| **Citation accuracy** | **New, and poor.** This is the motivation for Session 03 |

Citation accuracy being poor is a *success* today. A 500-character chunk straddling
two sections gets tagged with only one of them, so even a correct retrieval
frequently carries the wrong citation. The room has just measured, precisely, why
chunking on meaning matters.

### ✅ 6 — Recorded before the room empties

| | Lands in |
|---|---|
| Both numbers, plus passages ingested and quarantined | `eval/baseline.md` |
| The subsidiary regulations decision **and its reason** | `docs/decisions.md` |
| Standard 2 of 10 | `docs/standard.md` |

---

## 7 · The decision this room owns

Three sets of subsidiary regulations sit under the Act: the General Regulations 2021
(LN 263), Registration (LN 265) and Complaints Handling (LN 264).

Adding them roughly doubles the corpus, introduces cross-document references, and
**will lower both scores in the short term.** That is an argument *for* adding them,
not against — a corpus that only contains easy material produces a flattering
number, and this quarter has already committed to refusing those.

> **If it goes ahead it must go ahead early.** Adding documents changes every chunk
> index downstream. Record the decision and its reason in `docs/decisions.md` either
> way, and note that the twenty original questions continue to be reported unchanged.

---

## 8 · What you should be able to explain afterwards

- Why polling is not ingestion, and what change data capture gives you that polling
  cannot — **the insert-then-delete between two polls is the argument that settles it.**
- Why an append-only log beats a queue when three consumers have three different
  latency tolerances.
- The four failure options for a bad record — crash, skip, coerce, quarantine — and
  why quarantine is the only correct default.
- Why `uuid4()` breaks a pipeline and a content hash does not.
- Why Session 02 barely moves retrieval accuracy, and what it makes measurable
  instead.

> **The rule to carry out of this session:** validate at the boundary, quarantine on
> failure, **never coerce.** A pipeline that silently repairs bad input is a pipeline
> that will one day silently repair good input into something wrong.

---

## 9 · If it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| Parser finds 0 parts | Regex expects `PART` + em-dash | The corpus says `Part IV - `. See §4 |
| Section 43 resolves to the contents page | The TOC duplicates every section number | Skip lines with dot leaders |
| Everything quarantines | Schema requires a field the parser does not emit | Read `quarantine.jsonl` — the reason is in it |
| Passage count doubles on re-run | Identity includes a timestamp or a UUID | Derive it from content and position |
| Citation accuracy looks *great* | Parser stopped at the section | Resolve to the subsection. See §6 check 2 |

---

## 10 · Before Session 03

- Run `python -m src.ingest --verify` and confirm the manifest matches.
- **Open `quarantine.jsonl` and read every entry.** Bring one that surprised you.
- Read **section 41** of the Act — data protection by design and by default. One page.
- Add two evaluation questions whose answers sit in a **subsection**, so the citation
  must be precise to `s.43(3)` rather than merely `s.43`.
- Bring one sentence on where, in your own work, a downstream system would not find
  out that an upstream source had changed.

**Next:** [Session 03 · Getting Data Ready](../s03/README.md) — the two halves of the
first module finally meet, and the score is expected to move more than in any other
week.
