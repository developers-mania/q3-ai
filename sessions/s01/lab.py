# %% [markdown]
# # Session 01 · Build It Badly, Then Measure It
#
# **The question:** what actually changed in how software is built, and what does it
# mean for the work I already do?
#
# This is the replay of what happened on screen. It imports from `src/pipeline.py`
# rather than restating the code, so there is one place to fix a bug.
#
# Nothing here needs an API key, an account, or a network connection.

# %%
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from src.pipeline import (  # noqa: E402
    CHUNK_SIZE,
    build_chunks,
    build_index,
    chunk,
    expected_strings,
    load_documents,
    retrieve,
    score,
)

# %% [markdown]
# ## 01 · Load the corpus
#
# Two plain text files become two strings. No parsing, no cleaning, no metadata.

# %%
docs = load_documents()
for name, text in docs.items():
    print(f"{name:28} {len(text):>8,} characters")

# %% [markdown]
# **What have we already thrown away?**
#
# Section numbering. Part headings. The distinction between a section and a
# schedule. The fact that one document is binding law and the other is policy.
# All of it is still in the text as characters. None of it is available to the
# system as *structure*.

# %% [markdown]
# ## 02 · Chunk it badly
#
# Fixed-width cuts, no overlap, no awareness of meaning.

# %%
chunks = build_chunks(docs)
print(f"{len(chunks):,} chunks of {CHUNK_SIZE} characters")

# %% [markdown]
# Find a chunk that straddles a section boundary and read it aloud. Look for one
# carrying a deadline with no indication of whose deadline it is.

# %%
for c in chunks:
    if "hours" in c["text"].lower() and "breach" in c["text"].lower():
        print(f"{c['source']} #{c['index']}\n{c['text']}\n")
        break

# %% [markdown]
# > **Flaw 1 — chunks cut across meaning.** Owner: Session 03.
# >
# > **Flaw 5 — chunks carry no section number, so no answer can be cited.** Owner: Session 03.

# %% [markdown]
# ## 03 · Index it badly
#
# TF-IDF scores chunks by word overlap with the question. Fast, no model, offline —
# and no idea that "notify the Commissioner" and "inform the regulator" mean the
# same thing.

# %%
vectorizer, matrix = build_index(chunks)
print(f"vocabulary: {len(vectorizer.vocabulary_):,} terms")

# %% [markdown]
# > **Flaw 2 — the index matches words, not meaning.** Owner: Session 04.

# %% [markdown]
# ## 04 · Retrieve
#
# The near-miss pair. Both questions share almost every content word. Watch the
# same chunks come back for both.

# %%
pair = [
    "Within how many hours must a data controller notify the Data Commissioner of a personal data breach?",
    "Within how many hours must a data processor notify the data controller of a personal data breach?",
]
for q in pair:
    print(f"\nQ: {q}")
    for c, s in retrieve(q, chunks, vectorizer, matrix):
        print(f"  [{s:.3f}] {c['source']} #{c['index']}  {c['text'][:90]}...")

# %% [markdown]
# > **Flaw 3 — no re-ranking; the first plausible match wins.** Owner: Session 05.
# >
# > **Flaw 4 — no confidence threshold; the system never says "I don't know".** Owner: Session 09.

# %% [markdown]
# ## 05 · The evaluation set
#
# The most important thing that happened in the room. Four rules for a question:
# the answer is in the corpus; the answer is unambiguous; the answer is verifiable
# in one place by section; and some questions are near-miss traps.
#
# Note the `expect` field. Statutes spell numbers out — the Act says
# "seventy-two hours" where the board says "72 hours". `expect` lists the surface
# forms the corpus actually uses, so a correct retrieval scores as one.

# %%
import yaml  # noqa: E402

questions = yaml.safe_load(Path("eval/questions.yaml").read_text()) or []
for q in questions:
    print(f"{q['id']}  {q['answer']:<24} {q['source']:<18} expect={expected_strings(q)}")

# %% [markdown]
# ## 06 · Run it and record the number
#
# Did the chunk containing the correct answer appear in the top three? Not whether
# a model phrased a good answer — whether the right passage was found at all.

# %%
if questions:
    accuracy = score(questions, chunks, vectorizer, matrix)
    print(f"\nBASELINE RETRIEVAL ACCURACY: {accuracy:.0%}  ({len(questions)} questions)")

# %% [markdown]
# Write it on the board. Photograph the board. Commit it to `eval/baseline.md` with
# the date and the number of questions.
#
# Expect 30–55%. **If it comes out above 70%, the questions were too easy** — say so
# honestly and harden them before committing. A flattering baseline is worse than no
# baseline, because every improvement for the next nine weeks is measured against it.
#
# ---
#
# **Measure first. Improve second. Never the other way round.**
