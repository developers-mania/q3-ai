# %% [markdown]
# # Session 04 · Two Retrievers, Then One
#
# **The question:** how does an application recall things it was not trained on?
#
# The easy version of this session is "embeddings are better than keyword search, so
# we switch". That version is wrong, and this lab proves it wrong with measurement
# rather than argument.

# %%
import os
import sys
from pathlib import Path


def repo_root() -> Path:
    for base in (Path.cwd(), *Path.cwd().parents):
        if (base / "src" / "embed.py").exists() and (base / "corpus").is_dir():
            return base
    raise SystemExit(
        f"Could not find the repository root from {Path.cwd()}.\n"
        "Run this from a clone of q3-ai - the folder holding corpus/ and src/.\n"
        "On session-04-start src/embed.py does not exist yet: it is built live.\n"
        "Check out solution/session-04 to replay the finished lab."
    )


ROOT = repo_root()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
print(f"repo root : {ROOT}")
print(f"python    : {sys.executable}")

if not (ROOT / "models" / "all-MiniLM-L6-v2").exists():
    raise SystemExit(
        "The models are not here yet. They are deliberately not committed - about\n"
        "90 MB each. Fetch them once:\n\n"
        "    python tools/fetch_models.py\n"
    )

# %% [markdown]
# ## The hook: ask the same thing twice
#
# Two questions with the same answer. One uses the words the Act uses. One does not.

# %%
import yaml  # noqa: E402

from src.evaluate import evaluate_with, load_passages  # noqa: E402
from src.pipeline import expected_strings, normalise_for_match  # noqa: E402

QUESTIONS = yaml.safe_load(Path("eval/questions.yaml").read_text(encoding="utf-8")) or []
passages = load_passages()
print(f"{len(passages):,} passages from Session 03")


def hit(question: dict, results: list[dict]) -> bool:
    wanted = [normalise_for_match(s) for s in expected_strings(question)]
    return any(any(w in normalise_for_match(p["text"]) for w in wanted) for p in results)

# %% [markdown]
# ## 01 · What an embedding is
#
# A list of numbers representing a piece of text, arranged so that text with similar
# meaning gets similar numbers. That is the whole idea.
#
# Two things worth being precise about: the numbers mean nothing individually - no
# position corresponds to a concept you could name, only distances carry information
# - and **a model produced them**, which is why the model's blind spots become yours.

# %%
from src.embed import embed_corpus, embed_texts, load_model  # noqa: E402

model = load_model()
print(f"model loaded, {model.get_sentence_embedding_dimension()} dimensions, no network used")

a, b, c = embed_texts([
    "notify the Commissioner of a personal data breach",
    "tell the regulator we have been hacked",
    "agricultural subsidies for smallholder farmers",
], model)
print(f"\n  notify / tell     cosine {float(a @ b):+.3f}   same meaning, no shared words")
print(f"  notify / farming  cosine {float(a @ c):+.3f}   unrelated")

# %% [markdown]
# Note the first number is not close to 1.0. "Similar" is relative: what matters is
# that it is far above the unrelated pair, not that it is large in absolute terms.
# Reading a cosine as a percentage is a common and expensive mistake.

# %% [markdown]
# ## 02 · Where the embeddings are computed
#
# Most tutorials call a hosted service, which means every passage of your corpus and
# every question your users ask is sent to a third party, usually outside Kenya.
#
# > **DPA s.50** permits the Cabinet Secretary to require that certain processing be
# > carried out only through a server or data centre **located in Kenya**. The
# > National AI Strategy puts data sovereignty among its central concerns.
#
# Nothing below leaves this laptop. That is not a limitation imposed by the venue -
# it is the architecture Session 08 makes permanent, and it starts here.

# %%
matrix = embed_corpus(passages, model)
print(f"{matrix.shape[0]:,} passages embedded to {matrix.shape[1]} dimensions, on this CPU")

# %% [markdown]
# ## 03 · Three retrievers
#
# BM25 replaces Session 01's TF-IDF on the keyword side. Two fixes, both of which
# matter here: **saturation** (a word appearing twenty times is not twenty times as
# relevant) and **length normalisation** (s.25 is long and matches many queries by
# accident; s.43(3) is one sentence and is the right answer more often).

# %%
from src.retrieve import build_sparse, search_dense, search_fused, search_sparse  # noqa: E402

bm25 = build_sparse(passages)
searchers = {
    "sparse (BM25)": lambda q, k=3: search_sparse(q, bm25, passages, k),
    "dense": lambda q, k=3: search_dense(q, model, matrix, passages, k),
    "fused (RRF)": lambda q, k=3: search_fused(q, bm25, model, matrix, passages, k),
}
for name, fn in searchers.items():
    r = evaluate_with(QUESTIONS, passages, fn)
    print(f"{name:<14} retrieval {r['retrieval']:>4.0%}   citation {r['citation']:>4.0%}")

# %% [markdown]
# ## 04 · Compare question by question
#
# The most valuable part of the session. *"Which retriever is better"* has no answer.
# *"Which questions does each one win"* has a very clear one.

# %%
res = {n: {q["id"]: hit(q, fn(q["question"])) for q in QUESTIONS} for n, fn in searchers.items()}
sp, dn = res["sparse (BM25)"], res["dense"]

only_s = [q["id"] for q in QUESTIONS if sp[q["id"]] and not dn[q["id"]]]
only_d = [q["id"] for q in QUESTIONS if dn[q["id"]] and not sp[q["id"]]]
both = [q["id"] for q in QUESTIONS if dn[q["id"]] and sp[q["id"]]]
neither = [q["id"] for q in QUESTIONS if not dn[q["id"]] and not sp[q["id"]]]

print(f"both found it    {len(both):>2}/20   {both}")
print(f"keyword only     {len(only_s):>2}/20   {only_s}")
print(f"dense only       {len(only_d):>2}/20   {only_d}")
print(f"neither          {len(neither):>2}/20   {neither}")
print(f"\nan oracle picking the better retriever per question: "
      f"{(len(both)+len(only_s)+len(only_d))/len(QUESTIONS):.0%}")

# %% [markdown]
# ## 05 · Fusion, and an honest result
#
# Reciprocal rank fusion throws the scores away and uses only positions. You cannot
# add the scores: cosine runs 0 to 1, BM25 is unbounded, and adding 0.83 to 14.2
# produces a number with no meaning - the keyword side would dominate purely because
# its numbers are bigger.
#
# The Content Pack predicts the fused result beats both inputs. **On this corpus it
# does not**, and the pack itself says that outcome is worth ten minutes.

# %%
import itertools  # noqa: E402

from src.retrieve import fuse  # noqa: E402

by_id = {p["passage_id"]: p for p in passages}


def fused_at(pool, rrf_k):
    def f(q, k=3):
        s = [p["passage_id"] for p in search_sparse(q, bm25, passages, pool)]
        d = [p["passage_id"] for p in search_dense(q, model, matrix, passages, pool)]
        return [by_id[i] for i, _ in fuse([s, d], k=rrf_k)[:k]]
    return f


print(f"{'pool':>5} {'rrf_k':>6} {'retrieval':>10} {'citation':>9}")
for pool, rrf_k in itertools.product((3, 10, 30), (1, 10, 60)):
    r = evaluate_with(QUESTIONS, passages, fused_at(pool, rrf_k))
    print(f"{pool:>5} {rrf_k:>6} {r['retrieval']:>9.0%} {r['citation']:>8.0%}")

# %% [markdown]
# Fusion lands **between** its two inputs at every setting, never above both.
#
# The mechanism is visible once stated. RRF rewards *agreement*: a passage ranked
# third by both retrievers beats one ranked first by only one. That is usually the
# behaviour you want - and here the two retrievers agree on the easy questions and
# disagree on exactly the hard ones, so the minority opinion that happened to be
# right gets voted down by two mediocre ones that happened to concur.
#
# > This is not a reason to discard fusion. It is a reason to stop asking a *vote* to
# > do a *judge's* job - which is precisely what Session 05 builds.

# %% [markdown]
# ## 06 · The number that sets up next week
#
# Stage 1's job is about to change. From Session 05 it no longer has to put the right
# answer at rank 1 - it only has to get the answer **somewhere in a shortlist** that a
# slower, more careful model then re-reads.
#
# So measure the thing that will matter: how often is the answer anywhere in the pool?

# %%
print(f"{'pool':>5} {'sparse':>8} {'dense':>8} {'fused':>8}   <- recall, not precision")
for pool in (10, 30, 50):
    s_r = sum(hit(q, search_sparse(q["question"], bm25, passages, pool)) for q in QUESTIONS)
    d_r = sum(hit(q, search_dense(q["question"], model, matrix, passages, pool)) for q in QUESTIONS)
    f_r = sum(hit(q, fused_at(pool, 60)(q["question"], pool)) for q in QUESTIONS)
    n = len(QUESTIONS)
    print(f"{pool:>5} {s_r/n:>7.0%} {d_r/n:>8.0%} {f_r/n:>8.0%}")

# %% [markdown]
# At a pool of 30 the answer is present about **80%** of the time, while ranking
# surfaces it at rank 1-3 only about **50%** of the time.
#
# That gap is the entire case for Session 05. The retrieval is not failing to *find*
# the answer - it is failing to *recognise* it among things that look similar.
#
# Dense edges fused by one question at pool 30. **One question in twenty is inside
# the noise of a 20-question set**, and not a basis for declaring a winner. Say that
# out loud rather than reading a 5% difference as a result.

# %% [markdown]
# ## 07 · Add a cache, then discover it cannot be tuned
#
# A semantic cache stores past queries with their results; a new query close enough
# to a stored one gets the stored answer without searching.
#
# The Content Pack shows it serving a wrong answer at a threshold of 0.95. On this
# corpus and this model the picture is worse than that, and the measurement is short.

# %%
from src.cache import SemanticCache, cached_search  # noqa: E402

qs_by_id = {q["id"]: q for q in QUESTIONS}


def sim(x, y):
    v = embed_texts([x, y], model)
    return float(v[0] @ v[1])


print("SAFE to cache - different wording, SAME answer (a hit here is correct):")
safe = []
for para, orig in [("q16", "q07"), ("q17", "q05"), ("q18", "q10"), ("q19", "q08"), ("q20", "q09")]:
    s = sim(qs_by_id[para]["question"], qs_by_id[orig]["question"])
    safe.append(s)
    print(f"   {s:.4f}   {para} ~ {orig}   both -> {qs_by_id[orig]['source']}")

print("\nDANGEROUS to cache - similar wording, DIFFERENT answers (a hit here is wrong):")
danger = [
    ("q01 ~ q02", sim(qs_by_id["q01"]["question"], qs_by_id["q02"]["question"])),
    ("seed s01 ~ s02  (72h vs 48h)", sim(
        "Within how many hours must a data controller notify the Data Commissioner of a personal data breach?",
        "Within how many hours must a data processor notify the data controller of a personal data breach?")),
]
for label, s in danger:
    print(f"   {s:.4f}   {label}")

hi_safe, hi_danger = max(safe), max(s for _, s in danger)
print(f"\n  highest SAFE pair   : {hi_safe:.4f}")
print(f"  highest DANGER pair : {hi_danger:.4f}")
print(f"\n  To be safe, a threshold must sit ABOVE {hi_danger:.4f}.")
print(f"  To ever fire on a true duplicate, it must sit BELOW {hi_safe:.4f}.")
print("  " + ("NO SUCH THRESHOLD EXISTS." if hi_danger >= hi_safe else "A usable window exists."))

# %% [markdown]
# ## What that actually means
#
# The two ranges are not merely overlapping. They are **inverted**. Every dangerous
# pair scores higher than every safe pair.
#
# The reason is the same one that made Session 01's keyword index fail, seen from the
# other side. An embedding largely measures *how alike two sentences look*, not
# *whether they have the same answer*. Two questions phrased almost identically that
# differ in one role name look nearly the same. Two questions with identical answers
# phrased in different registers look far apart.
#
# So on this corpus a semantic cache is not a good idea that needs careful tuning.
# **It cannot be tuned.** Any threshold that ever fires usefully also fires wrongly,
# and it will serve the wrong answer *faster than the right one used to arrive*.
#
# Two honest corrections while you are here:
#
# - The cache saves less than people think. The query must be embedded *before* the
#   cache can be checked, and locally the embedding is the slow part. It saves the
#   search, not the embedding.
# - The lookup is a linear scan. At ten thousand cached queries you compare against
#   ten thousand vectors per request - more than the search you were avoiding.

# %%
cache = SemanticCache(threshold=0.90)  # deliberately lowered, to show the failure
search = searchers["fused (RRF)"]
A = "Within how many hours must a data controller notify the Data Commissioner of a personal data breach?"
B = "Within how many hours must a data processor notify the data controller of a personal data breach?"
r1, c1, _ = cached_search(A, cache, model, search)
r2, c2, ev = cached_search(B, cache, model, search)
print(f"A  {'CACHE HIT' if c1 else 'searched '}  -> {r1[0]['citation']}")
print(f"B  {'CACHE HIT' if c2 else 'searched '}  -> {r2[0]['citation']}"
      + (f"   (similarity {ev[0]:.3f} to A - it answered B with A's result)" if c2 else ""))

# %% [markdown]
# ---
#
# **We do not replace one method with another on the strength of a single number. We
# compare per question, keep what each is good at, and measure the combination.**
