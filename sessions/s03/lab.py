# %% [markdown]
# # Session 03 · Cut on Meaning, Then Take Things Out
#
# **The question:** what shape does data need to be in before a model can use it -
# and what has to be stripped out first?
#
# Two halves that teach opposite lessons. The first is the payoff for two weeks of
# unglamorous work. The second is the one people remember.

# %%
import os
import sys
from pathlib import Path


def repo_root() -> Path:
    for base in (Path.cwd(), *Path.cwd().parents):
        if (base / "src" / "chunk.py").exists() and (base / "corpus").is_dir():
            return base
    raise SystemExit(
        f"Could not find the repository root from {Path.cwd()}.\n"
        "Run this from a clone of q3-ai - the folder holding corpus/ and src/.\n"
        "On session-03-start src/chunk.py and src/redact.py do not exist yet: they\n"
        "are built live. Check out solution/session-03 to replay the finished lab."
    )


ROOT = repo_root()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
print(f"repo root : {ROOT}")
print(f"python    : {sys.executable}")

# %% [markdown]
# ## The chunk is the unit of retrieval
#
# A retrieval system returns chunks. Not sentences, not sections, not answers -
# chunks, exactly as they were cut at ingestion time. The chunk is the **smallest
# addressable unit in the entire system**, and every later stage operates on units
# whose boundaries were fixed here.
#
# > A chunk cut through the middle of an answer cannot be repaired by a better
# > embedding model, a better re-ranker, or a better prompt. The information is not
# > there. Session 05 will add a re-ranker that re-reads the shortlist carefully; it
# > cannot recover an answer that was destroyed in Session 01.
#
# ### Where Session 02 left it

# %%
import yaml  # noqa: E402

from src.evaluate import build_index, evaluate  # noqa: E402
from src.ingest import build_candidates  # noqa: E402
from src.publish import publish  # noqa: E402

QUESTIONS = yaml.safe_load(
    Path("eval/seed-questions.yaml").read_text(encoding="utf-8")
) or []


def measure(overlap: int, redact_fn=None):
    """Ingest at these settings and return both numbers."""
    accepted, _rejected = publish(build_candidates(overlap=overlap, redact_fn=redact_fn))
    passages = [p.model_dump() for p in accepted]
    vectorizer, matrix = build_index(passages)
    return passages, evaluate(QUESTIONS, passages, vectorizer, matrix)


print("This lab measures against eval/seed-questions.yaml throughout, so every")
print("number it prints is comparable with every other number it prints.")
print("Session 02 on that same set: retrieval 53%, citation 8%.")
print()
print("The COHORT baseline is a different set - eval/questions.yaml, twenty questions")
print("- recorded in eval/baseline.md. There Session 02 scored 50%/17% and Session 03")
print("scores 45%/33%. Both instruments are honest. Mixing them is not.")
print()
print("Session 02 cut every 500 characters and tagged each chunk with whichever")
print("subsection it happened to START in. The parser was fine. The cut was not.")

# %% [markdown]
# ## 01 · Structure-aware chunking
#
# Session 02 gave every node a span that partitions the document, so a node's own
# text is exactly its span. Emitting one chunk per node cuts precisely where the Act
# says one idea ends and another begins.
#
# Three cases arise and only the third is difficult:
#
# | Case | Example | Handling |
# |---|---|---|
# | fits comfortably | s.43(3), one sentence | emit as one chunk |
# | too small | a one-line definition | merge with siblings, **never across sections** |
# | too large | s.25, the eight principles | subdivide, **keeping the citation** |

# %%
passages, result = measure(overlap=0)
print(f"{len(passages):,} chunks (Session 02 produced 547)")
print(f"retrieval {result['retrieval']:.0%}   citation {result['citation']:.0%}"
      f"   ({result['near']} near)")

# %% [markdown]
# **Citation accuracy 8% -> 38%.** That is the largest single movement of the
# quarter so far, and it came from doing *less*: no new model, no new index, just
# cutting where the document says to cut.
#
# Read the same passage Session 02 got wrong:

# %%
def flatten(text: str) -> str:
    return " ".join(text.replace("-", " ").split()).lower()


hit = next(p for p in passages if "forty eight hours" in flatten(p["text"]))
print(f"citation: {hit['citation']}      (Session 02 tagged this DPA s.43(2))")
print(f"text: {hit['text'][:260]}")

# %% [markdown]
# It is now exactly subsection 43(3) - it begins at "A data processor shall notify"
# and ends at the end of that subsection. The near-miss pair from Session 01 can be
# told apart **by citation** for the first time.

# %% [markdown]
# ## 02 · Measure three overlap settings
#
# Overlap repeats the tail of one chunk at the head of the next, so content spanning
# a boundary survives in at least one piece. Common defaults are 10-20% and they are
# copied far more often than they are measured.
#
# **Predict before running.** The argument for overlap is supposed to *weaken* once
# cutting is semantic, because answers no longer straddle boundaries at random.

# %%
print(f"{'overlap':>8} {'chunks':>8} {'retrieval':>10} {'citation':>9}")
for ov in (0, 50, 100, 200, 300):
    ps, r = measure(overlap=ov)
    print(f"{ov:>8} {len(ps):>8,} {r['retrieval']:>9.0%} {r['citation']:>8.0%}")

# %% [markdown]
# **The prediction was wrong, and that is why it was measured.**
#
# Overlap buys a great deal of retrieval here - and costs citation. The reason is
# visible once stated: a chunk that begins with its neighbour's tail can match a
# query on borrowed text, so the answer is retrieved (**retrieval up**) from a chunk
# whose citation belongs to the passage *next door* (**citation down**).
#
# There is no setting that maximises both:
#
# | | retrieval | citation |
# |---|---|---|
# | overlap 0 | 47% | **38%** |
# | overlap 100 | **73%** | 31% |
# | overlap 200+ | 80% | 31% |
#
# 100 is recorded as the chosen value: it is the smallest setting that moves *both*
# numbers above Session 02 (53% and 8%), and beyond 200 the corpus grows for nothing.
# The trade is written down in `docs/decisions.md`, because a parameter chosen by
# measurement is a decision and a parameter chosen by default is an accident that has
# not caused a problem yet.

# %% [markdown]
# ## 03 · Pattern redaction on the fixture
#
# `fixtures/complaint-synthetic.txt` is **fabricated** - invented names, an invalid
# ID format, telephone numbers in unallocated ranges, and email addresses on
# example.com, which RFC 2606 reserves so it can never be real. A room learning about
# personal data should not be handed a file that could plausibly contain any.
#
# This measures **recall**: of the identifiers we planted, how many were removed?

# %%
from src.redact import NAME_NAIVE, NAME_NARROW, PATTERNS, false_positive_rate, redact  # noqa: E402

fixture = Path("fixtures/complaint-synthetic.txt").read_text(encoding="utf-8")
print("recall on the fixture:")
print("   well-shaped :", redact(fixture, PATTERNS)[1])
print("   NAME narrow :", redact(fixture, {"NAME": NAME_NARROW})[1])
print("\nsanitised extract:")
print(redact(fixture, {**PATTERNS, "NAME": NAME_NARROW})[0][1180:1450])

# %% [markdown]
# ## 04 · Run it on the real corpus
#
# The Act and the Strategy are public documents. The Data Commissioner is named by
# **office**, not by name. So what is there to redact?
#
# This measures **precision** - the rate almost nobody measures. On a corpus known
# to contain no data-subject identifiers, *every hit is a false positive by
# construction*, so the count IS the damage.

# %%
corpus = "\n".join(Path("corpus", n).read_text(encoding="utf-8")
                   for n in ("dpa-2019.txt", "ai-strategy-2025.txt"))

print(f"{'pattern':<14} {'hits':>6}   {'FP rate':>7}")
for label, (pattern, _r) in list(PATTERNS.items()) + [("NAME_NAIVE", NAME_NAIVE),
                                                      ("NAME_NARROW", NAME_NARROW)]:
    rate, n = false_positive_rate(corpus, pattern)
    print(f"{label:<14} {n:>6}   {rate:>6.0%}")

# %% [markdown]
# **Stop here and let the room work out what happened.**
#
# The well-shaped patterns cost almost nothing: zero phone numbers, zero labelled ID
# numbers. The naive name rule fires **739 times**, and not one of them is a person.

# %%
import collections  # noqa: E402
import re  # noqa: E402

print("what the naive name rule actually redacts:")
for term, n in collections.Counter(re.findall(NAME_NAIVE[0], corpus)).most_common(8):
    print(f"   {n:>4}x  {term}")

# %% [markdown]
# `Data Commissioner` - 80 times in the Act alone. That term appears in most of the
# evaluation set. A rule written to protect people is about to delete the subject of
# half the questions.

# %%
_ps, plain = measure(overlap=100)
_ps, naive = measure(overlap=100, redact_fn=lambda t: redact(t, {**PATTERNS, "NAME": NAME_NAIVE}))
print(f"{'':<22} {'retrieval':>10} {'citation':>9}")
print(f"{'before redaction':<22} {plain['retrieval']:>9.0%} {plain['citation']:>8.0%}")
print(f"{'after NAIVE name rule':<22} {naive['retrieval']:>9.0%} {naive['citation']:>8.0%}")

# %% [markdown]
# The pipeline reported success. Every stage ran cleanly. The output looks
# well-formed. **Only the score noticed.**
#
# That is the third time this quarter measurement has caught something no test would
# have raised.

# %% [markdown]
# ## 05 · Measure the false positive rate, then narrow the rule
#
# A redaction rule has two error rates and only one is usually measured.
#
# | Rate | Question | Measured against | Usually measured? |
# |---|---|---|---|
# | Recall | of the personal data present, how much was removed? | a fixture with planted identifiers | yes |
# | **Precision** | of what was removed, how much was actually personal data? | a corpus known to contain none | **rarely** |

# %%
_ps, narrow = measure(overlap=100,
                      redact_fn=lambda t: redact(t, {**PATTERNS, "NAME": NAME_NARROW}))
print(f"{'':<22} {'retrieval':>10} {'citation':>9}")
print(f"{'no redaction':<22} {plain['retrieval']:>9.0%} {plain['citation']:>8.0%}")
print(f"{'NAIVE name rule':<22} {naive['retrieval']:>9.0%} {naive['citation']:>8.0%}")
print(f"{'NARROWED name rule':<22} {narrow['retrieval']:>9.0%} {narrow['citation']:>8.0%}")

print("\nnarrowed rule on the corpus:", re.findall(NAME_NARROW[0], corpus))

# %% [markdown]
# **Full recovery, and the narrowed rule still catches every planted name in the
# fixture.** It genuinely catches less - an unlabelled name walks straight through -
# and that trade is the decision the room is making, not a detail.
#
# ### The two names it does find are not a false positive
#
# They are real contributors credited in the Strategy's acknowledgements. Which means
# the premise of the precision measurement - *this corpus contains no personal data* -
# is **almost** true and not quite. The Act contains none. The Strategy names people.
#
# Nobody predicted that. The measurement found it.

# %% [markdown]
# ## 06 · What a pattern structurally cannot do
#
# ```
# "The complainant, Wanjiru Kamau, alleges that her employer..."
# ```
#
# A name has no fixed shape. There is no regular expression for *this string is a
# person*, and capitalisation is not enough - the Act capitalises Data Commissioner,
# Cabinet Secretary and First Schedule. Named entity recognition asks a **model**
# whether a span looks like a person in context.
#
# It fails differently, and worse in one specific way:
#
# | | Pattern | Named entity recognition |
# |---|---|---|
# | Determinism | total | none - a model decision |
# | **Debuggability** | **you can read the rule** | **the model decided; you cannot read why** |
# | Auditability | the rule is the audit trail | every decision must be logged separately |
# | On this corpus | over-redacts visibly | over-redacts *invisibly* - it will take "Kenya" as a location |
#
# When a regulator asks why a particular identifier was not removed, a pattern is an
# answer. A model that scored the span below threshold is not an answer, it is a
# description of an outcome.
#
# > The risk of a redaction step is proportional to how little you have measured it -
# > and a model-based step is **harder** to measure than a regular expression, not
# > easier.

# %% [markdown]
# ## What this pipeline can and cannot claim
#
# Being precise about this matters, because overclaiming compliance is itself a risk.
#
# | Claim | Supported? | Basis |
# |---|---|---|
# | Redaction runs before indexing | **yes** | it is in the ingestion path; the code shows it |
# | Structured identifiers are removed | mostly | measured recall against the fixture, which is not exhaustive |
# | Person names are removed | partially | only where a title or role introduces them |
# | The index contains no personal data | **no** | not demonstrable. Redaction reduces exposure; it does not prove absence |
# | The pipeline satisfies s.41 | partially | it implements a measure of the kind s.41 names. Whether it is *appropriate* is a judgement, not a test result |
#
# The fourth row is the one to internalise. *"We redact personal data"* and *"the
# index contains no personal data"* are different claims, and only the first is
# defensible.
#
# > The strongest control is not indexing the document in the first place. The second
# > strongest is indexing a derived summary that never contained identifiers.
# > Redaction is third, and it is a mitigation rather than a guarantee.
#
# ---
#
# **A safeguard is measured in both directions. Measure what you remove, not only
# what you keep.**
