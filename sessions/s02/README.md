# Session 02 · Where The Data Comes From

> **The question this session answers**
> *How does data get into a system reliably, and what breaks when it doesn't?*

| | |
|---|---|
| **Date** | Wednesday 12 August 2026 · 2:00–4:00 PM |
| **Module** | 1 · Data Infrastructure and Pipelines |
| **Stack layer** | 1 — data infrastructure |
| **Start branch** | `session-02-start` |
| **Finish tag** | `solution/session-02` |
| **Needs** | Python 3.10+, `pydantic`. Still **no key, no account, no network** |
| **Repairs** | **Flaw 6** (corpus is two hand-downloaded files) and **half of Flaw 5** (passages carry no section number) |

---

## 1 · What this codelab is for

Every failure so far has been visible. A wrong answer is wrong on the screen; a bad
retrieval score is a bad number on the board.

**This session is about the failure that produces no symptom at all.**

When a source document changes and the index does not, the system keeps answering —
fluently, confidently, in the same tone it uses when it is right — from a version of
the truth that no longer exists. Nothing logs it. No test catches it. And the
evaluation score does not move, *because the evaluation set was written against the
old version too*.

Session 01 established measurement as the discipline that catches problems.
Staleness is the failure that **defeats** measurement, because the instrument and
the system are wrong in the same direction at the same time.

> **Say this out loud before the numbers appear: retrieval accuracy will barely
> move today.** It lands as a prediction confirmed rather than a disappointment.
> What this session delivers is a corpus that is *trustworthy and citable* — the
> precondition for Sessions 03 and 04 to work at all.

### What ingestion actually owes you

Four jobs. Session 01 did exactly one.

| Job | What it means | Session 01 | Session 02 |
|---|---|---|---|
| **Acquire** | Get the bytes from a known location, repeatably | a person clicked a link | `manifest.json` |
| **Verify** | Confirm they are what was expected; notice change | not done | content hash comparison |
| **Structure** | Turn a document into parts, sections, identity | not done | `src/parse.py` |
| **Publish** | Emit records downstream in a shape consumers rely on | not done | `src/passage.py` + `src/publish.py` |

---

## 2 · Working through this on your own

**Missed the session? It is fully self-contained.** No facilitator, no room, no
network.

```bash
git clone https://github.com/developers-mania/q3-ai.git && cd q3-ai
git fetch --tags --force
git switch -c play/your-name solution/session-02    # a branch OF the tag, not the tag

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # adds pydantic

python sessions/s02/lab.py
```

That last command is the whole session narrated — the manifest, the drift check, the
parser and the three traps in it, the schema, quarantine, idempotency, and both
numbers. About a minute to run.

> **Which branch?** `solution/session-02` to read or replay the finished code.
> `session-02-start` to type it yourself — there the Session 02 modules do not
> exist yet, exactly as the room finds them at 2:00 PM.
> `git diff session-02-start solution/session-02` is the lesson.

---

## 3 · Before you start (in the room)

```bash
git fetch --tags --force && git checkout session-02-start
source .venv/bin/activate
pip install -r requirements.txt

python tools/verify_corpus.py      # the corpus pin still holds
python -m src.pipeline --score --questions eval/seed-questions.yaml
```

### Re-run the baseline before building anything

Put last week's number on the board next to today's date. **It should be identical**,
because nothing has changed.

That is the point. The first re-run establishes that the measurement is stable and
reproducible. **If it is not identical, stop and find out why** — an evaluation that
drifts on its own is worthless for the next eight weeks.

---

## 4 · Where to look in the repository

| File | What to do with it |
|---|---|
| **`src/ingest.py`** | **The session.** Manifest, drift detection, passage building |
| **`src/parse.py`** | **The long step.** The Act as a tree of parts, sections, subsections |
| **`src/passage.py`** | The pydantic boundary contract |
| **`src/publish.py`** | Validation and the quarantine path |
| **`src/evaluate.py`** | Both numbers |
| `manifest.json` | Provenance: title, publisher, version, retrieval date, hash |
| `passages.jsonl` | Generated output. **Gitignored** — reproducible from `corpus/` + the parser |
| `quarantine.jsonl` | Rejected records with reasons. **Open it and read it** |
| `src/pipeline.py` | Session 01's. Untouched — chunking stays naive on purpose |
| `eval/questions.yaml` | Add two questions whose answers sit in a **subsection** |

> **There is no `raw/` directory**, and the Content Pack says there should be. A
> second copy of a frozen, checksum-pinned corpus can drift from the first, and a
> downstream system reading the stale copy is precisely the Layer 1 failure this
> session teaches. `corpus/` already *is* the artifact as retrieved. Recorded in
> [`docs/decisions.md`](../../docs/decisions.md).

---

## 5 · The six steps

| Time | Step | Repairs |
|---|---|---|
| 3:00 – 3:08 | 1 · Manifest and change detection | Flaw 6 |
| 3:08 – 3:22 | **2 · Parse the Act into its structure** | groundwork for Flaw 1 |
| 3:22 – 3:32 | 3 · The passage record and its schema | Flaw 5 (half) |
| 3:32 – 3:40 | 4 · Boundary validation and quarantine | — |
| 3:40 – 3:45 | 5 · Idempotent publish | — |
| 3:45 – 3:50 | 6 · Re-run, and meet the second number | — |

### Step 2 will not parse cleanly first time — and that is the session

Budget five of the fourteen minutes for the room to find the failures and argue.
Three traps are in this corpus specifically, and all three are worth finding rather
than being told:

| Trap | What you will see |
|---|---|
| **The Content Pack's own regex matches nothing** | It ships `^PART\s+([IVXL]+)\s*[—-]` — uppercase, em-dash, column zero. The Act writes `    Part IV - PRINCIPLES...`: title case, plain hyphen, and **centred**, with indentation from 0 to 44 spaces. All 11 Parts are there; the pattern is wrong, not the corpus |
| **Every section number appears twice** | Once in the contents page with dot leaders, once in the body. A naive `^\d+\.\s` finds **150 markers for 75 sections**, and the first `43.` it hits is the contents entry, which has no text under it |
| **The running header sits inside section text** | `Data Protection Act (Cap. 411C)  Kenya` appears **26 times**, and not only at page edges — one lands between s.38(1)(b) and s.38(6). A parser that keeps it attaches a page banner to a subsection |

Dot leaders alone are *not* a safe way to find the contents block — the First
Schedule's oath template is full of them (`I, ......., make oath`). The block is
bounded instead: it ends at the first Part heading that is not a contents entry.

### Why chunking deliberately does NOT change today

Passages are still cut at fixed 500-character intervals. They simply now carry the
section they fell inside.

Cutting on section boundaries is **Session 03's job**, and separating the two is what
makes next week's improvement measurable in isolation. If both changed in the same
week, the movement in the score could not be attributed to either.

It also produces the specific, visible failure that motivates Session 03 — and the
room measures it before being offered the fix.

---

## 6 · How to know it worked

### ✅ 1 — Drift is detected, and refuses to proceed

```bash
python -m src.ingest --verify
```

```
OK        all sources match manifest.json
```

The lab doctors a source *in memory* and shows the fingerprint move without touching
the file. To see the refusal for real, edit a copy and re-run — the pipeline names
the drifted file and exits non-zero.

The system has not become smarter. It has become **capable of noticing**.

### ✅ 2 — The parser recovers the whole Act

```bash
python -c "from src.parse import parse_act; from pathlib import Path; import collections; r,_=parse_act(Path('corpus/dpa-2019.txt').read_text(encoding='utf-8')); print(collections.Counter(n.kind for n in r.walk()))"
```

```
Counter({'paragraph': 296, 'subsection': 154, 'section': 75, 'part': 11, 'schedule': 1, 'document': 1})
```

**75 sections, 11 parts, none missing.** If sections are missing, the contents block
is being parsed instead of the body.

### ✅ 3 — It resolves to the subsection, not just the section

This is the check that decides whether citation accuracy means anything.

The evaluation set cites the 72-hour deadline to `s.43(1)(a)` and the 48-hour one to
`s.43(3)`. **If the parser resolved only to `DPA s.43`, both near-miss questions
would score as citation hits and the metric would collapse into flattery.**

> Resolve to the subsection, or do not report citation accuracy at all.

### ✅ 4 — Every passage validates, and failures are quarantined not lost

```bash
python -m src.ingest
```

```
OK        all sources match manifest.json
accepted  547 passages
quarantined 0
of those, 160 carry a section number (29%)
```

**Zero quarantined is correct here** — the corpus is clean. Which makes the
dead-letter path easy to believe in and never see, so the lab **breaks the schema on
purpose**: it strips the citation off 100 passages and shows them rejected with a
readable reason, nothing lost, nothing guessed.

*29% carrying a section* is not a failure either: the AI Strategy contributes 345 of
the 547 passages and has no citable sections at all. Of the Act's 202 passages, 160
carry one.

### ✅ 5 — The pipeline is idempotent

```bash
python -m src.ingest && wc -l passages.jsonl
python -m src.ingest && wc -l passages.jsonl      # identical
```

The count is the **weak** test. The strong test is that the set of *identifiers* is
identical — that catches the case where the same number of passages is produced with
different identities:

```bash
python -m src.ingest && cut -d'"' -f4 passages.jsonl | sort > /tmp/a
python -m src.ingest && cut -d'"' -f4 passages.jsonl | sort > /tmp/b
diff /tmp/a /tmp/b && echo IDEMPOTENT
```

### ✅ 6 — Both numbers, and the second one is poor

```bash
python -m src.evaluate --questions eval/seed-questions.yaml
```

```
RETRIEVAL ACCURACY: 53%   (15 questions)
CITATION  ACCURACY:  8%   (13 citable; 2 excluded — the AI Strategy has no citable sections)
            5 more retrieved the right SECTION but the wrong subsection
```

| Measure | Expected | Why |
|---|---|---|
| **Retrieval** | roughly unchanged | Chunking, index and retrieval are Session 01's |
| **Citation** | **poor** | This is the session working, not failing |

**Citation accuracy being poor is a success today.** A 500-character chunk straddling
two subsections gets tagged with whichever one it *starts* in, so even a correct
retrieval frequently carries the wrong citation.

> Retrieval moved 47% → 53%, which the Content Pack predicted would "barely move".
> That is explained rather than ignored: `strip_furniture()` removes 54 lines of
> running header and page numbers that Session 01 was indexing as content. It is a
> Layer 1 effect, not a retrieval improvement. See `docs/decisions.md`.

### ✅ 7 — Recorded before the room empties

| | Lands in |
|---|---|
| Both numbers, passages ingested, passages quarantined | `eval/baseline.md` |
| The subsidiary regulations decision **and its reason** | `docs/decisions.md` |
| Standard 2 of 10 | `docs/standard.md` |

---

## 7 · The result that motivates Session 03

The `near` rows are the whole argument. Retrieval was **right** and the citation was
**wrong by one subsection**:

| Question | Answer lives in | Passage was tagged |
|---|---|---|
| 48-hour processor deadline | `s.43(3)` | `s.43(2)` |
| 90-day complaint period | `s.56(5)` | `s.56(4)` |
| 30-day portability request | `s.38(6)` | `s.38(5)(b)` |
| 60-day DPIA report | `s.31(5)` | `s.31(4)` |

Print the offending passage and the cause is obvious — it **starts** inside
subsection (2), runs through (3), and ends inside (4). It can only be tagged with one
of them.

**That is not a parser bug.** The parser is fine. The cut is not.

---

## 8 · What you should be able to explain afterwards

- Why polling is not ingestion, and what change data capture gives you that polling
  cannot — **the row inserted and deleted between two polls is the argument that
  settles it.**
- Why an append-only log beats a queue when three consumers have three different
  latency tolerances and three different failure modes.
- The four options for a bad record — crash, skip, coerce, quarantine — and why
  quarantine is the only correct default.
- Why `uuid4()` breaks a pipeline and a content hash does not — and what including
  `offset` in the identity costs you.
- Why Session 02 barely moves retrieval accuracy, and what it makes measurable
  instead.
- Why the AI Strategy gets a document-level citation while the Act gets `s.43(3)` —
  and why faking precision on the Strategy would be worse than admitting it has none.

> **The rule to carry out of this session:** validate at the boundary, quarantine on
> failure, **never coerce.** A pipeline that silently repairs bad input is a pipeline
> that will one day silently repair good input into something wrong.

---

## 9 · If it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| Parser finds 0 parts | Regex expects `PART` + em-dash at column 0 | The Act says `    Part IV - `. See §5 |
| Section 43 resolves to an empty node | The contents page duplicates every section number | Skip to the first non-contents Part heading |
| `No manifest.json` | Verification cannot run without its reference | One of the few defensible crashes — proceeding would mean ingesting unverified sources while appearing not to |
| Everything quarantines | Schema requires a field the parser does not emit | Read `quarantine.jsonl`; the reason is in the record |
| Passage count doubles on re-run | Identity includes a timestamp or a UUID | Derive it from content and position |
| Citation accuracy looks *great* | Parser stopped at the section | Resolve to the subsection. See §6 check 3 |
| `ModuleNotFoundError: pydantic` | New dependency this week | `pip install -r requirements.txt` |

---

## 10 · Before Session 03

- Run `python -m src.ingest --verify` and confirm the manifest matches.
- **Open `quarantine.jsonl`.** If it is empty, break the schema yourself and read
  what comes out.
- Read **section 41** of the Act — data protection by design and by default. One page.
- Add two evaluation questions whose answers sit in a **subsection**, so the citation
  must be precise to `s.43(3)` rather than merely `s.43`.
- Bring one sentence on where, in your own work, a downstream system would not find
  out that an upstream source had changed.

**Next:** [Session 03 · Getting Data Ready](../s03/README.md) — the parser knows where
every subsection begins and ends, and the chunker still ignores it. Those two finally
meet, and the score is expected to move more than in any other week.
