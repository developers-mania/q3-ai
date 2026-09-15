# Session 05 · Remembering The Right Thing

> **The question this session answers**
> *How do you make retrieval accurate instead of merely plausible?*

| | |
|---|---|
| **Date** | Wednesday 2 September 2026 · 2:00–4:00 PM |
| **Module** | 2 · Context Engineering and Retrieval (**closing session**) |
| **Stack layer** | 2 — context and memory |
| **Start branch** | `session-05-start` |
| **Finish tag** | `solution/session-05` |
| **Needs** | Python 3.10+, `chromadb`, `networkx`, both models. Still no key, no account, no network |
| **Repairs** | **Flaw 3** — no re-ranking; the first plausible match wins |

> The Content Pack calls the finished branch `session-05-reranking`. This repository
> uses `session-NN-start` + a `solution/session-NN` tag throughout — see
> [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

---

## 1 · What this codelab is for

On 5 August the room wrote a near-miss pair: how long does a **controller** have to
notify the Commissioner (72 hours), and how long does a **processor** have to notify
the controller (48 hours). Since then that pair has defeated TF-IDF, BM25, dense
embeddings, and the fused system.

**Four methods, beaten by two sentences differing in one role name.**

Session 04 ended with the number that explains why: the answer is somewhere in a
30-passage shortlist **80%** of the time and reaches rank 1–3 only **50%** of the
time. Retrieval stopped failing to *find* the answer weeks ago. It is failing to
*recognise* it.

### Why the current system cannot tell them apart

Everything so far encodes the question and the passages **separately**, then compares
the results. That is a **bi-encoder**, and its advantage is enormous — passages are
encoded in advance, so searching 571 costs one encoding plus 571 cheap comparisons.

What it gives up: when a passage was encoded, the model had no idea what would be
asked. It produced **one fixed summary** that must serve every possible question. For
s.43(1) and s.43(3) those summaries are nearly identical — both are about breach
notification, deadlines and parties. The distinction is exactly the fine detail one
fixed summary flattens away, and it was discarded at indexing time.

| | Bi-encoder | Cross-encoder |
|---|---|---|
| What goes in | one text at a time | question **and** passage together |
| When it runs | passages once at indexing | every pair, at query time |
| Cost for 571 passages | 1 model pass | **571 model passes** |
| Compares words across texts | no | **yes** |
| Good at | finding roughly relevant things fast | telling similar things apart |

> The cross-encoder is **not a better retriever**. It is a better **judge**, and
> judges are expensive — so you only bring them a shortlist.

```
STAGE 1   fused retrieval      571 passages  ->  30 candidates   fast, approximate
STAGE 2   cross-encoder         30 candidates ->   3 passages    slow, accurate
```

Stage 1's job changes accordingly: it no longer has to put the answer at rank 1, only
somewhere in the shortlist — a much easier job it already does 80% of the time.

---

## 2 · Working through this on your own

```bash
git clone https://github.com/developers-mania/q3-ai.git && cd q3-ai
git fetch --tags --force
git switch -c play/your-name solution/session-05

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python tools/fetch_models.py
python -m src.rerank --check       # "bi-encoder ok, cross-encoder ok, no network used"

python sessions/s05/lab.py         # ~3 minutes; the cross-encoder is the slow part
```

> **Let it be slow and time it.** Re-ranking 30 candidates means 30 model passes per
> query. On an older laptop that is seconds. That is not a problem to work around —
> it *is* the measurement. This session is partly about discovering that accuracy
> costs time.

---

## 3 · Where to look in the repository

| File | What to do with it |
|---|---|
| **`src/rerank.py`** | **New.** The cross-encoder, two-stage retrieval, `with_parent_stem` |
| **`src/store.py`** | **New.** ChromaDB, with the `embeddings=` trap documented |
| **`src/crossref.py`** | **New.** The Act's own cross-references as a graph |
| `src/evaluate.py` | Gains per-subset scoring (`near_miss`, `paraphrase`) |
| `eval/questions.yaml` | Gains `tags:` — 5 near-miss, 5 paraphrase |
| `chroma/` | **Gitignored.** The persistent store |

---

## 4 · The six steps

| Time | Step | Effect |
|---|---|---|
| 3:00 – 3:08 | 1 · Move the index into ChromaDB | **None — and that is the check** |
| 3:08 – 3:20 | 2 · Add the cross-encoder | The pair half-breaks |
| 3:20 – 3:28 | 3 · Time it | Slower. Measure how much |
| 3:28 – 3:34 | 4 · Choose the shortlist size | Decides a parameter |
| 3:34 – 3:42 | 5 · Report two scores | The hard subsets get their own numbers |
| 3:42 – 3:50 | 6 · Follow the cross-references | Measured — and it changes nothing here |

---

## 5 · How to know it worked

### ✅ 1 — ChromaDB changes the numbers by exactly nothing

```
numpy  dense  retrieval 55%  citation 17%
chroma dense  retrieval 55%  citation 17%
identical: True
```

**If that says `False`, stop and fix it before continuing.**

> **Pass `embeddings=` explicitly, or the session breaks silently.** Omit it and
> ChromaDB embeds the documents with its *own* downloaded model — not Session 04's.
> Nothing errors. The index builds, queries return results, the numbers move, and
> every comparison is quietly invalid. It is the same failure shape as Session 02's
> stale index, Session 03's over-redaction and Session 04's cache: **the pipeline
> reports success and the measurement is void.**

Persistence and filtering are the honest reasons for the database. Speed is not — at
571 passages a numpy dot product is already fast, and saying so is part of the
session.

```
metadata filtering, where={"part": "VI"}:
   DPA s.48     DPA s.48(a)     DPA s.49(2)
```

### ✅ 2 — The pair half-breaks, and the half that fails is the interesting half

| Question | Stage 1 top | Stage 2 top | Verdict |
|---|---|---|---|
| **B** processor / 48h → want `s.43(3)` | `s.43(3)` | **`s.43(3)` (+9.48)** vs `s.43(1)(a)` (+6.16) | ✅ **correct, wide margin** |
| **A** controller / 72h → want `s.43(1)(a)` | `s.43(3)` | `s.43(3)` (+8.08) vs `s.43(1)(a)` (+7.62) | ❌ still wrong |

**B is a genuine first.** Four retrievers could not separate that pair; the
cross-encoder saw *processor* in the question and *processor* in s.43(3) in the same
forward pass, which a bi-encoder never has the opportunity to do.

**A is worth ten minutes, and the obvious explanation is wrong.** Print the terms:

| Chunk | controller | Commissioner | processor | seventy-two | forty-eight |
|---|---|---|---|---|---|
| `s.43(1)(a)` — answer to A | ✅ | ✅ | — | ✅ | — |
| `s.43(3)` — answer to B | ✅ | — | ✅ | ✅ | ✅ |

`s.43(1)(a)` matches **every** term in question A and still loses. Look at what
`s.43(3)` carries: **both** roles, **both** deadlines, all the notification
vocabulary. It reads as the *comprehensive* passage on breach notification, so a
relevance judge prefers it for almost any question in that area — including the one
it does not answer.

It has "seventy-two hours" because the **overlap of 100** chosen by measurement in
Session 03 prepended its neighbour's tail. That decision bought 26 points of
retrieval accuracy then. Here it pays some back.

> **Check the other setting before blaming overlap.** At overlap 0, `s.43(3)` loses
> "seventy-two hours" — and `s.43(1)(a)` loses "controller", which the cut leaves in
> the `s.43` parent. The re-ranker *still* prefers `s.43(3)`. **Neither chunking
> setting presents A's answer as the better passage**, for opposite reasons.

`with_parent_stem` puts back the words the cut moved. The gap closes from **0.46 to
0.07** — and the order still does not flip. Partial credit, honestly reported.

> Session 03 said chunking is the one decision later sophistication cannot compensate
> for. This is that sentence arriving two weeks later, inside the most sophisticated
> component built so far.

### ✅ 3 — Accuracy costs time, and the cost is linear

| Configuration | Median ms/query |
|---|---|
| Stage 1 only (fused) | **~50** |
| + re-rank, shortlist 10 | ~1,100 |
| + re-rank, shortlist 30 | ~2,500 |
| + re-rank, shortlist 100 | **~15,400** |

**Cost is linear in shortlist size. Accuracy is not** — it plateaus, because the
answer was usually already in the top 30. A hundred candidates costs ten times ten
candidates and buys very little.

Ask the room where the extra accuracy stops being worth the wait. There is no correct
answer: a system answering legal compliance questions can afford two seconds; a
search box that autocompletes cannot.

### ✅ 4 — Shortlist recall is the ceiling

| Shortlist | Recall |
|---|---|
| 10 | 65% |
| **30** | **80%** |
| 100 | 85% |

If the answer is not in the shortlist the cross-encoder cannot find it — it never
sees it. **80% is the hard ceiling on what re-ranking at shortlist 30 can achieve.**

### ✅ 5 — Two-stage retrieval improves both numbers

| Configuration | Retrieval | Citation |
|---|---|---|
| Stage 1 only (fused) | 45% | 22% |
| **+ cross-encoder, shortlist 30** | **50%** | **28%** |

A real improvement, and a modest one. **Recall is 80% and the score is 50%** — the
shortlist contains the answer and the judge is missing it 30 points of the time.

> By the pack's own rule, that says **invest in Stage 2, not Stage 1**. The finding
> above qualifies it: much of that 30-point gap is chunk boundaries, not judgement,
> so the honest next move is a chunking experiment as much as a better judge. This is
> the first session whose measurements point at what to do next rather than only
> reporting what happened.

### ✅ 6 — Two scores from now on

```
all questions   retrieval 50%   citation 28%
  near_miss     retrieval 5/5   citation 3/5
  paraphrase    retrieval 0/5   citation 0/5
```

**Our near-miss questions pass on retrieval and fail on citation** — they are
near-misses in *which subsection*, not in *whether the region was found*. The subset
that is genuinely hard here is **paraphrase: still 0/5**, unchanged since 5 August
despite embeddings arriving in Session 04.

> The overall score is the headline. The subset scores tell you whether the system is
> getting genuinely better or merely getting easy questions right. **If the overall
> number rises while a hard subset does not, the system is improving where it matters
> least.**

### ✅ 7 — The cross-reference graph is real, thin, and changes nothing

| | |
|---|---|
| Graph | 75 sections, **13 edges** |
| Passages citing another section | **21 / 571** |
| Expansion effect | retrieval 45% → 45%, citation 22% → 22% |

**It changes nothing, and that is the finding.** The Content Pack says the Act
"refers to itself constantly" and gives *"s.48 … subject to section 49"* as the
example. **In this text s.48 contains no section reference at all.** The whole Act
contains 14 section-to-section references; the extractor finds 13.

What the Act *does* reference constantly is its own **subsections** — 39 times — and
those are intra-section, so the parent chunk is already adjacent.

The technique is sound. This corpus does not need it. That is the third time this
quarter a technique has been adopted, measured, and found not to move the number —
which is exactly what measuring before adopting is for.

---

## 6 · The decisions this room owns

**Shortlist size.** 30. Recall rises 65% → 80% from 10 to 30, then only to 85% at 100
while cost goes up tenfold.

**Where next week's effort goes.** Recall 80% against a score of 50% says the answer
is being found and mis-ranked. Record which way the numbers point in
[`docs/decisions.md`](../../docs/decisions.md).

---

## 7 · What you should be able to explain afterwards

- Bi-encoder versus cross-encoder, in plain language, and why one is fast and one is
  accurate.
- Why you cannot simply use the cross-encoder for everything.
- Why passing `embeddings=` to ChromaDB explicitly is not a detail.
- What shortlist recall is, and why it is a **ceiling** rather than a score.
- Why an average hides the questions a system finds hard.
- Why the controller question still fails, and why the answer is a chunk boundary
  rather than the re-ranker.

---

## 8 · If it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| Chroma numbers differ from numpy | `embeddings=` omitted | Chroma embedded with its own model. See §5 check 1 |
| Re-ranking is very slow | 30 model passes per query, on CPU | Expected. That is the measurement |
| `No cross-encoder at models/...` | Not fetched | `python tools/fetch_models.py` |
| The near-miss pair both rank `s.43(3)` | Chunk boundaries, not the judge | See §5 check 2 |
| Expansion changes nothing | 13 edges in the whole Act | Correct. See §5 check 7 |

---

## 9 · Before Session 06

- Re-run the evaluation and bring your **shortlist recall** figure.
- Find one question where re-ranking made things **worse**. Work out whether the
  cross-encoder scored the right passage poorly, or Stage 1 never included it — those
  are different problems with different fixes.
- Read the **Model Context Protocol specification** — the overview and the tools
  section. Not a vendor SDK's documentation; the specification itself.
- Read the OWASP LLM Top 10 entries on **excessive agency** and insecure tool design.

**Next:** [Session 06 · Handing Over The Tools](../s06/README.md) — Module 2 closes.
Everything so far has been one shape: a question in, passages out. Session 06 is the
first time the system does something rather than answering something.
