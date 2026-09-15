# Session 04 · Giving Software Memory

> **The question this session answers**
> *How does an application recall things it was not trained on?*

| | |
|---|---|
| **Date** | Wednesday 26 August 2026 · 2:00–4:00 PM |
| **Module** | 2 · Context Engineering and Retrieval |
| **Stack layer** | 2 — context and memory |
| **Start branch** | `session-04-start` |
| **Finish tag** | `solution/session-04` |
| **Needs** | Python 3.10+, two local models (~175 MB, fetched once). **No key, no account, no network at runtime** |
| **Repairs** | **Flaw 2** — the index matches words, not meaning |

> The Content Pack calls the finished branch `session-04-hybrid` and says it starts
> from `session-03-preparation`. This repository uses the convention in
> [`CONTRIBUTING.md`](../../CONTRIBUTING.md) throughout — `session-NN-start` plus a
> `solution/session-NN` tag — so the names differ and nothing is missing.

---

## 1 · What this codelab is for

The easy version of this session is *"embeddings are better than keyword search, so
we switch"*. **That version is wrong**, and the room disproves it in twenty minutes
with measurement rather than argument.

Embeddings understand meaning and are bad at exact numbers and section references —
which is most of what this corpus contains. Keyword search is the reverse. So the
session is not about replacing one with the other. It is about running both,
comparing them question by question, and combining them properly.

**The interesting engineering is in the combining** — and in discovering, this week,
that combining is not enough.

---

## 2 · Working through this on your own

```bash
git clone https://github.com/developers-mania/q3-ai.git && cd q3-ai
git fetch --tags --force
git switch -c play/your-name solution/session-04

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # adds sentence-transformers (brings torch), rank-bm25

python tools/fetch_models.py       # ~175 MB, once
python sessions/s04/lab.py
```

> **The models are not in the repository.** Two of ~88 MB each. Committing them
> would take a 1.2 MB clone to ~180 MB permanently, for every participant and every
> remaining session, and git stores binary blobs badly. `tools/fetch_models.py`
> downloads them into a gitignored `models/`; after that the session is fully
> offline. A facilitator on slow venue wifi should copy `models/` onto a USB stick
> rather than have twenty laptops pull 175 MB at 2:05.

Verify they load without touching the network — the check sets `HF_HUB_OFFLINE`, so
a model that silently falls back to downloading **fails** instead of passing:

```bash
python tools/fetch_models.py --check
```

---

## 3 · Where to look in the repository

| File | What to do with it |
|---|---|
| **`src/embed.py`** | **New.** Local bi-encoder; unit-normalised so a dot product *is* cosine |
| **`src/retrieve.py`** | **New.** BM25, dense, and reciprocal rank fusion |
| **`src/cache.py`** | **New.** The semantic cache, built to be broken |
| **`src/compare.py`** | **New.** Per-question keyword-vs-dense comparison |
| `tools/fetch_models.py` | Fetches both models; `--check` proves they load offline |
| `src/evaluate.py` | Gains `evaluate_with(questions, passages, search_fn)` — scores any retriever |
| `models/` | **Gitignored.** Models and the cached corpus embeddings |

> `requirements.txt` stopped being tiny this week, and the file says so in its own
> header. The promise that *ended* is "this needs almost nothing to install". The
> promise that **holds** is no key, no account, and no network at runtime — which is
> the one DPA s.50 actually rests on.

---

## 4 · The six steps

| Time | Step | Effect |
|---|---|---|
| 3:00 – 3:08 | 1 · Embed the corpus, locally | Setup for everything after |
| 3:08 – 3:14 | 2 · Dense retrieval | Mixed — some up, some down |
| 3:14 – 3:24 | **3 · Compare question by question** | **The heart of the session** |
| 3:24 – 3:30 | 4 · Upgrade keyword to BM25 | Saturation and length normalisation |
| 3:30 – 3:40 | 5 · Fuse the rankings | Not what the pack predicts — see §6 |
| 3:40 – 3:50 | 6 · Add a cache, then break it | A demonstrated, measured failure |

### What embeddings are bad at

The part most sessions skip. Dense retrieval has a specific, predictable weakness,
and this corpus is built out of exactly that weakness.

| Query type | Dense | Keyword | Why |
|---|---|---|---|
| Paraphrased question | wins | fails | Meaning is shared; words are not |
| Exact reference — `s.43(3)` | **fails** | wins | To an embedding, s.43(3) and s.43(1) look nearly identical |
| A specific number | weak | wins | Numbers carry little semantic signal |
| Proper noun | fair | wins | Exact term match is unbeatable |
| Conceptual question | wins | fails | No shared vocabulary to match on |

Read row two again. The corpus is a **statute** — section numbers, deadlines and
monetary amounts.

---

## 5 · How to know it worked

### ✅ 1 — The model loads offline, 384 dimensions

```bash
python tools/fetch_models.py --check
```

```
OK    all-MiniLM-L6-v2           loaded, 384 dimensions, no network used
OK    ms-marco-MiniLM-L-6-v2     loaded and scored a pair, no network used
```

### ✅ 2 — The corpus embeds locally

```bash
python -m src.embed
```

**571 passages → 384 dimensions**, about 25 seconds on CPU. Nothing leaves the
machine. The sanity check prints:

```
notify / tell     cosine +0.317   same meaning, no shared words
notify / farming  cosine -0.104   unrelated
```

> The first number is **not** close to 1.0, and that matters. "Similar" is relative
> — what counts is that it is far above the unrelated pair. Reading a cosine as a
> percentage is a common and expensive mistake.

### ✅ 3 — Each retriever wins different questions

```bash
python -m src.compare
```

| Retriever | Retrieval | Citation |
|---|---|---|
| sparse (BM25) | 45% | **28%** |
| dense | **55%** | 17% |
| fused (RRF) | 50% | 22% |

| | Questions |
|---|---|
| Both found it | 8/20 |
| **Keyword only** | 1/20 — `q15` |
| **Dense only** | 3/20 — `q04`, `q16`, `q19` (two are paraphrases) |
| Neither | 8/20 |
| **An oracle picking the better one per question** | **60%** |

Ask the room to name the pattern before you do. Note also that dense *improves*
retrieval (45% → 55%) while *lowering* citation (28% → 17%) — it finds the right
region and is worse at picking the exact subsection, which is row two of the table
above, measured.

### ✅ 4 — Fusion does **not** beat both, and that is the finding

The Content Pack predicts the fused result beats both inputs, and says that if it
does not, the outcome is worth ten minutes. **It does not**, at any setting:

| pool | rrf_k | Retrieval | Citation |
|---|---|---|---|
| 3–30 | 1, 10 | 50% | 22% |
| 30 | 60 | 45% | 22% |

Fusion lands **between** its two inputs, never above both. The mechanism is visible
once stated: RRF rewards *agreement* — a passage ranked third by both beats one
ranked first by only one. Usually that is what you want. Here the two retrievers
agree on the easy questions and disagree on exactly the hard ones, so the minority
opinion that happened to be **right** is voted down by two mediocre ones that
happened to concur.

> That is not a reason to discard fusion. It is a reason to stop asking a **vote** to
> do a **judge's** job — which is exactly what Session 05 builds.

### ✅ 5 — The number that sets up next week

Stage 1's job is about to change. From Session 05 it no longer has to put the answer
at rank 1; it only has to get the answer **somewhere in a shortlist** a slower model
re-reads. So measure recall, not precision:

| pool | sparse | dense | fused |
|---|---|---|---|
| 10 | 55% | 55% | **65%** |
| 30 | 65% | **85%** | 80% |
| 50 | 70% | 85% | 85% |

**The answer is in the top 30 about 80% of the time; ranking surfaces it at rank 1–3
about 50% of the time.** That 30-point gap is the entire case for Session 05 — the
retriever is not failing to *find* the answer, it is failing to *recognise* it among
things that look similar.

> Dense edges fused by one question at pool 30. **One question in twenty is inside
> the noise of a 20-question set**, not a result. Say so rather than reading a 5%
> difference as a finding.

### ✅ 6 — The cache cannot be tuned, and the measurement is short

The pack shows the cache serving a wrong answer at a threshold of 0.95. On this
corpus and this model it is worse than that.

| Pair kind | Example | Cosine |
|---|---|---|
| **Safe** — different wording, same answer | `q18 ~ q10` | 0.3372 |
| **Safe** — highest of five | `q16 ~ q07` | **0.5814** |
| **Dangerous** — similar wording, different answers | `q01 ~ q02` | 0.7627 |
| **Dangerous** — the 72h/48h breach pair | seed `s01 ~ s02` | **0.9225** |

```
To be safe, a threshold must sit ABOVE 0.9225.
To ever fire on a true duplicate, it must sit BELOW 0.5814.
NO SUCH THRESHOLD EXISTS.
```

The two ranges are not merely overlapping — they are **inverted**. Every dangerous
pair scores higher than every safe pair.

The reason is Flaw 2 seen from the other side: an embedding largely measures *how
alike two sentences look*, not *whether they share an answer*. Two questions phrased
almost identically that differ in one role name look nearly the same; two questions
with identical answers phrased in different registers look far apart.

> So a semantic cache here is not a good idea needing careful tuning. **It cannot be
> tuned.** Any threshold that ever fires usefully also fires wrongly — and it serves
> the wrong answer *faster than the right one used to arrive*.

Two honest corrections while you are there: the query must be embedded **before** the
cache can be checked, and locally the embedding is the slow part — so the cache saves
the search, not the embedding. And the lookup is a linear scan, which at ten thousand
cached queries costs more than the search it was avoiding.

---

## 6 · The decision this room owns

**Cache policy.** Three options in the pack: no cache; a higher threshold; or cache
only high-confidence answers. The measurement above removes the middle one — there is
no threshold that is both safe and useful on this corpus.

Record the choice and the reason in [`docs/decisions.md`](../../docs/decisions.md).
**Session 09 revisits this as a confidence threshold problem**, and this entry is what
makes that conversation short.

---

## 7 · What you should be able to explain afterwards

- What an embedding is, in one sentence, and why no single position in the vector
  means anything.
- Why running the model locally is a **s.50** question and not only a latency one.
- Which questions dense retrieval wins and which it loses — **from the measurement**,
  not from the table in the pack.
- Why BM25 improves on TF-IDF: saturation, and length normalisation.
- Why you cannot add a cosine score to a BM25 score, and what RRF does instead.
- Why fusion landed *between* its inputs here, and what that says about votes versus
  judges.
- Why a semantic cache on this corpus cannot be given a safe threshold.

---

## 8 · If it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| `No model at models/...` | Models not fetched | `python tools/fetch_models.py` |
| Model downloads during `--check` | It fell back to the hub | That is the check working — the model directory is incomplete; re-fetch with `--force` |
| Embedding takes minutes every run | Cache missed | Expected once. `models/corpus-embeddings.npz` is reused unless the corpus changed |
| "corpus changed since the embeddings were cached" | Chunking, overlap or redaction changed | Correct behaviour — stale vectors describe text that no longer exists |
| Fused is worse than dense | Not a bug — see §5 check 4 | Measure `pool` and `rrf_k`, and read which questions flipped |
| `ModuleNotFoundError: torch` | New and large this week | `pip install -r requirements.txt` — a few GB |

---

## 9 · Before Session 05

- Re-run `python -m src.compare` and bring the list of questions where dense and
  keyword disagreed.
- Pick one of the **8 questions neither retriever found**. Work out why, and bring the
  answer.
- Read the reciprocal rank fusion paper — Cormack, Clarke and Buettcher (2009). Two
  pages, and the reason `k=60` is everyone's default.
- Try `k=10` and `k=200` in the fusion function and form a view on why the result
  barely moves here.

**Next:** [Session 05 · Remembering The Right Thing](../s05/README.md) — the answer is
in the top 30 about 80% of the time and reaches rank 1–3 about 50% of the time. Next
week closes that gap with something that reads the question and the passage
*together*.
