# %% [markdown]
# # Session 05 · A Wide Net, Then a Careful Read
#
# **The question:** how do you make retrieval accurate instead of merely plausible?
#
# On 5 August the room wrote a pair of near-miss questions: how long does a
# *controller* have to notify the Commissioner (72 hours), and how long does a
# *processor* have to notify the controller (48 hours). Since then that pair has
# defeated TF-IDF, BM25, dense embeddings, and the fused system.
#
# Four methods, beaten by two sentences differing in one role name.

# %%
import os
import sys
import time
from pathlib import Path


def repo_root() -> Path:
    for base in (Path.cwd(), *Path.cwd().parents):
        if (base / "src" / "rerank.py").exists() and (base / "corpus").is_dir():
            return base
    raise SystemExit(
        f"Could not find the repository root from {Path.cwd()}.\n"
        "On session-05-start src/rerank.py does not exist yet - it is built live.\n"
        "Check out solution/session-05 to replay the finished lab."
    )


ROOT = repo_root()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
print(f"repo root : {ROOT}")
print(f"python    : {sys.executable}")

if not (ROOT / "models" / "ms-marco-MiniLM-L-6-v2").exists():
    raise SystemExit("Models missing. Run:  python tools/fetch_models.py")

# %% [markdown]
# ## Why the current system cannot tell them apart
#
# Everything built so far encodes the question and the passages **separately**, then
# compares the results. That is a **bi-encoder**, and its advantage is enormous:
# passages are encoded in advance, so searching 571 costs one encoding plus 571 cheap
# comparisons.
#
# Here is what it gives up. When a passage was encoded, the model had no idea what
# would be asked. It produced **one fixed summary** that must serve every possible
# question — and for s.43(1) and s.43(3) those summaries are nearly identical. The
# distinction between *controller notifies Commissioner* and *processor notifies
# controller* is exactly the fine detail a single fixed summary flattens away.
#
# The information needed to separate them was discarded at indexing time. No
# comparison of the resulting vectors can recover it.
#
# A **cross-encoder** does the opposite: question and passage go in **together**, one
# relevance score comes out, and the model can compare words across both texts.
#
# | | Bi-encoder | Cross-encoder |
# |---|---|---|
# | What goes in | one text at a time | question **and** passage together |
# | Cost for 571 passages | 1 model pass | **571 model passes** |
# | Compares words across texts | no | **yes** |
# | Use it for | searching everything | re-reading a shortlist |
#
# So the cross-encoder is not a better retriever. It is a better **judge**, and
# judges are expensive, so you only bring them a shortlist.

# %%
import yaml  # noqa: E402

from src.embed import embed_corpus, load_model  # noqa: E402
from src.evaluate import evaluate_with, load_passages  # noqa: E402
from src.pipeline import expected_strings, normalise_for_match  # noqa: E402
from src.rerank import load_reranker, rerank  # noqa: E402
from src.retrieve import build_sparse, search_fused  # noqa: E402

QUESTIONS = yaml.safe_load(Path("eval/questions.yaml").read_text(encoding="utf-8")) or []
passages = load_passages()
model = load_model()
matrix = embed_corpus(passages, model)
bm25 = build_sparse(passages)
reranker = load_reranker()
by_citation = {p["citation"]: p for p in passages}
print(f"{len(passages):,} passages · bi-encoder ok · cross-encoder ok · no network used")


def hit(question, results):
    wanted = [normalise_for_match(s) for s in expected_strings(question)]
    return any(any(w in normalise_for_match(p["text"]) for w in wanted) for p in results)


def stage1(q, k=3, pool=30):
    return search_fused(q, bm25, model, matrix, passages, k=k, pool=pool)


# %% [markdown]
# ## 01 · Move the index into ChromaDB
#
# The usual reason given is speed. At 571 passages that reason is **false** — last
# week's numpy dot product is already fast. The real reasons are **persistence** (the
# index survives a restart) and **filtering** (restricting to Part VI is a query, not
# a workaround).
#
# > **Pass `embeddings=` explicitly, or the session breaks silently.** Omit it and
# > ChromaDB embeds the documents itself with its own downloaded model — not the one
# > Session 04 used. Nothing errors. The index builds, queries return results, the
# > numbers move, and every comparison is quietly invalid. Same failure shape as
# > Session 02's stale index and Session 04's cache.

# %%
import shutil  # noqa: E402

from src.retrieve import search_dense  # noqa: E402
from src.store import build_store, search_store  # noqa: E402

shutil.rmtree("chroma", ignore_errors=True)
collection = build_store(passages, matrix)

a = evaluate_with(QUESTIONS, passages, lambda q, k=3: search_dense(q, model, matrix, passages, k))
b = evaluate_with(QUESTIONS, passages, lambda q, k=3: search_store(q, collection, model, passages, k))
print(f"numpy  dense  retrieval {a['retrieval']:.0%}  citation {a['citation']:.0%}")
print(f"chroma dense  retrieval {b['retrieval']:.0%}  citation {b['citation']:.0%}")
print(f"identical: {a['retrieval'] == b['retrieval'] and a['citation'] == b['citation']}"
      "   <- if False, the embeddings did not carry over. Stop and fix it.")

print("\nmetadata filtering - the feature that actually justifies the database:")
for p in search_store("transfer of personal data to another country", collection,
                      model, passages, k=3, where={"part": "VI"}):
    print(f"   {p['citation']:<16} part {p['part']}")

# %% [markdown]
# ## 02 · Add the cross-encoder, and run the pair that keeps winning

# %%
A = "Within how many hours must a data controller notify the Data Commissioner of a personal data breach?"
B = "Within how many hours must a data processor notify the data controller of a personal data breach?"

for label, q, want in [("A  controller / 72h", A, "DPA s.43(1)(a)"),
                       ("B  processor  / 48h", B, "DPA s.43(3)")]:
    candidates = stage1(q, k=30, pool=30)
    print(f"\n{label}   want {want}")
    print("   stage 1 (fused):      " + ", ".join(p["citation"] for p in candidates[:3]))
    ranked = rerank(q, candidates, reranker, k=3)
    got = ranked[0][0]["citation"]
    print(f"   stage 2 (re-ranked):  " + ", ".join(f"{p['citation']} ({s:+.2f})" for p, s in ranked))
    print(f"   -> {'CORRECT' if got == want else 'STILL WRONG'}")

# %% [markdown]
# **B breaks. A does not.**
#
# The processor question is answered correctly with a wide margin — the cross-encoder
# saw *processor* in the question and *processor* in s.43(3) in the same forward pass,
# which the bi-encoder never had the opportunity to do.
#
# The controller question still ranks s.43(3) first. That is worth ten minutes, and
# the cause is not the re-ranker.

# %%
TERMS = ("controller", "Commissioner", "processor", "seventy-two", "forty-eight")
for cite in ["DPA s.43(1)(a)", "DPA s.43(3)"]:
    text = " ".join(by_citation[cite]["text"].split())
    present = {w: w.lower() in text.lower() for w in TERMS}
    print(f"{cite}   ({'the answer to A' if '1)(a' in cite else 'the answer to B'})")
    print(f"   {text[:145]}")
    print(f"   {present}")
    print()

# %% [markdown]
# Read the two rows carefully, because the obvious explanation is wrong.
#
# `s.43(1)(a)` — the correct answer to A — contains **every** term in the question:
# controller, Commissioner, seventy-two, notify, hours. It is the better surface
# match. And it still loses.
#
# Look at what `s.43(3)` carries. It has *both* role names, *both* deadlines, and the
# notification vocabulary. It reads as the **comprehensive** passage about breach
# notification, so a judge scoring relevance prefers it for almost any question in
# that area — including the one it does not answer.
#
# It has "seventy-two hours" because the **overlap of 100 characters**, chosen by
# measurement in Session 03, prepended its neighbour's tail. That decision bought
# 26 points of retrieval accuracy at the time. Here it is paying some of that back.
#
# > **Check the other setting before blaming overlap.** At overlap 0, `s.43(3)` loses
# > "seventy-two hours" — and `s.43(1)(a)` loses "controller", which the cut leaves in
# > the `s.43` parent. The re-ranker still prefers `s.43(3)`. *Neither* chunking
# > setting presents A's answer as the better passage, for opposite reasons.
#
# So the honest statement is narrower than "the re-ranker fixed the pair". The
# mechanism works — B is separated with a wide margin, which four previous retrievers
# could not do. A is not, and the obstacle is where the boundaries fall rather than
# how carefully the shortlist is read.
#
# `src/rerank.py` offers `with_parent_stem`, which puts back the words the cut moved:

# %%
for label, q, want in [("A controller/72h", A, "DPA s.43(1)(a)")]:
    candidates = stage1(q, k=30, pool=30)
    for mode, stems in [("plain chunk", None), ("with parent stem", by_citation)]:
        ranked = rerank(q, candidates, reranker, k=2, by_citation=stems)
        gap = ranked[0][1] - ranked[1][1]
        print(f"   {mode:<17} 1st {ranked[0][0]['citation']:<15} ({ranked[0][1]:+.2f})"
              f"   2nd {ranked[1][0]['citation']:<15} ({ranked[1][1]:+.2f})   gap {gap:.2f}")

# %% [markdown]
# The gap closes from about 0.46 to about 0.07 and the order still does not flip.
# **Partial credit, honestly reported.** The fix is real and insufficient, and what
# remains is a chunking decision rather than a re-ranking one.
#
# Session 03 said chunking is the one decision later sophistication cannot compensate
# for. This is that sentence arriving two weeks later, inside the most sophisticated
# component built so far.

# %% [markdown]
# ## 03 · Time it, and choose a shortlist size
#
# The first thing built this quarter that makes the system **slower**. Measure it
# rather than estimating.

# %%
def timed(fn, questions, n=6):
    times = []
    for q in questions[:n]:
        t0 = time.perf_counter()
        fn(q["question"])
        times.append((time.perf_counter() - t0) * 1000)
    return sorted(times)[len(times) // 2]


print(f"{'configuration':<30} {'median ms':>10}")
print(f"{'stage 1 only (fused)':<30} {timed(lambda q: stage1(q), QUESTIONS):>9.0f}")
for shortlist in (10, 30, 100):
    fn = (lambda q, s=shortlist: rerank(q, stage1(q, k=s, pool=s), reranker, 3))
    print(f"{'+ rerank, shortlist ' + str(shortlist):<30} {timed(fn, QUESTIONS):>9.0f}")

# %% [markdown]
# Cost is **linear** in shortlist size — 100 candidates costs ten times what 10 does,
# with no plateau. Accuracy is not linear: it plateaus, because the answer was
# usually already in the top 30.
#
# Ask the room: at what point does extra accuracy stop being worth the wait? There is
# no correct answer. A system answering legal compliance questions can afford two
# seconds; a search box that autocompletes cannot.

# %% [markdown]
# ## 04 · Shortlist recall — the ceiling
#
# If the answer is not in the shortlist, the cross-encoder **cannot** find it. It
# never sees it. So this number is the hard ceiling on what re-ranking can achieve,
# and comparing it against the re-ranked score is what tells you where to invest next.

# %%
print(f"{'shortlist':>10} {'recall':>8}")
for shortlist in (10, 30, 100):
    recall = sum(hit(q, stage1(q["question"], k=shortlist, pool=shortlist))
                 for q in QUESTIONS) / len(QUESTIONS)
    print(f"{shortlist:>10} {recall:>7.0%}")

# %% [markdown]
# ## 05 · Report two scores from now on
#
# The near-miss questions have been failing since 5 August while the overall number
# improved. **The average has been hiding them.**

# %%
final = evaluate_with(QUESTIONS, passages,
                      lambda q, k=3: [p for p, _ in rerank(q, stage1(q, k=30, pool=30), reranker, k)])
print(f"all questions   retrieval {final['retrieval']:.0%}   citation {final['citation']:.0%}")
for tag, (r_got, r_tot, c_got, c_tot) in final["by_tag"].items():
    print(f"  {tag:<11} retrieval {r_got}/{r_tot}   citation {c_got}/{c_tot}")

# %% [markdown]
# The overall score is the headline. The subset scores tell you whether the system is
# getting genuinely better or merely getting easy questions right.
#
# > If the overall number rises while the hard subset does not, the system is
# > improving in the place that matters least.

# %% [markdown]
# ## 06 · The graph already in the Act
#
# The Act refers to itself — and those references are edges. A retriever scoring
# passages independently never notices them.
#
# Measure it before adopting it, like everything else.

# %%
from src.crossref import build_graph, expand, has_reference  # noqa: E402

graph = build_graph(passages)
print(f"graph: {graph.number_of_nodes()} sections, {graph.number_of_edges()} edges")
print(f"passages citing another section: {sum(has_reference(p) for p in passages)}/{len(passages)}")


def expand_if_ref(q, k=3):
    base = stage1(q, k)
    out = list(base)
    for p in base:
        if has_reference(p):
            out += [x for x in expand(p["citation"], graph, passages) if x not in out]
    return out[:k]


plain = evaluate_with(QUESTIONS, passages, lambda q, k=3: stage1(q, k))
expanded = evaluate_with(QUESTIONS, passages, expand_if_ref)
print(f"\nno expansion                  retrieval {plain['retrieval']:.0%}  citation {plain['citation']:.0%}")
print(f"expand when a reference exists retrieval {expanded['retrieval']:.0%}  citation {expanded['citation']:.0%}")

# %% [markdown]
# **It changes nothing here, and that is the finding.**
#
# The Content Pack says the Act "refers to itself constantly" and gives
# *"s.48 … subject to section 49"* as the example. In this text s.48 contains **no**
# section reference at all. The whole Act contains only 14 section-to-section
# references; the extractor finds 13 of them. What the Act *does* reference constantly
# is **subsections** of itself — 39 times — and those are intra-section, so the parent
# chunk is already adjacent.
#
# The technique is sound. This corpus does not need it. That is a measurement, not a
# failure, and it is the third time this quarter a technique has been adopted,
# measured, and found not to move the number.
#
# ---
#
# **Hard cases are scored separately. A system is judged on the questions it finds
# difficult, not on the average that hides them.**
