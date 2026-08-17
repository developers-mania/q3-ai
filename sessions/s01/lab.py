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
import os
import sys
from pathlib import Path


def repo_root() -> Path:
    """Find the clone, from wherever this happens to be running.

    WHY not Path.cwd(): a notebook's working directory is the folder the .ipynb
    sits in — notebooks/ — not the repository root. `import src.pipeline` then
    raises ModuleNotFoundError and every relative path like eval/questions.yaml
    misses, while the identical file run as a script from the root works fine.
    Walking up finds the clone from the root, from notebooks/, from sessions/s01/,
    and in Colab once the bootstrap cell has cloned and changed directory.
    """
    for base in (Path.cwd(), *Path.cwd().parents):
        if (base / "src" / "pipeline.py").exists() and (base / "corpus").is_dir():
            return base
    raise SystemExit(
        f"Could not find the repository root from {Path.cwd()}.\n"
        "Run this from a clone of q3-ai — the folder holding corpus/ and src/.\n"
        "On session-01-start there is no src/pipeline.py yet: it is built live in\n"
        "the session. Check out solution/session-01 to replay the finished lab."
    )


ROOT = repo_root()
os.chdir(ROOT)                      # so eval/... below resolves the same way everywhere
sys.path.insert(0, str(ROOT))

# If the score below is not 47%, or an import fails, check these two lines first.
# A notebook kernel is often a different interpreter from the shell's virtualenv,
# and the usual symptom is ModuleNotFoundError for sklearn or yaml.
print(f"repo root : {ROOT}")
print(f"python    : {sys.executable}")

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

# The room's set is empty until 3:40 on the day. Anyone replaying this alone falls
# back to eval/seed-questions.yaml so that step 06 produces an actual number — a
# session whose measurement step prints nothing has not been replayed at all.
room = yaml.safe_load(Path("eval/questions.yaml").read_text(encoding="utf-8")) or []
if room:
    questions, source_file = room, "eval/questions.yaml"
else:
    questions = yaml.safe_load(
        Path("eval/seed-questions.yaml").read_text(encoding="utf-8")
    ) or []
    source_file = "eval/seed-questions.yaml"
    print("eval/questions.yaml is empty — that is the room's file, written at 3:40.")
    print("Falling back to the seed set so this replay produces a number.\n")

print(f"{len(questions)} questions from {source_file}\n")
for q in questions:
    print(f"{q['id']:<5} {q['answer'][:34]:<36} {q['source']:<18} expect={expected_strings(q)}")

# %% [markdown]
# ## 06 · Run it and record the number
#
# Did the chunk containing the correct answer appear in the top three? Not whether
# a model phrased a good answer — whether the right passage was found at all.

# %%
if questions:
    accuracy = score(questions, chunks, vectorizer, matrix)
    print(f"\nRETRIEVAL ACCURACY: {accuracy:.0%}  ({len(questions)} questions"
          f" from {source_file})")
    if source_file.endswith("seed-questions.yaml"):
        print("Expect 47%. This is a learning score, NOT the cohort baseline —")
        print("eval/baseline.md is scored against the room's eval/questions.yaml.")

# %% [markdown]
# Write it on the board. Photograph the board. Commit it to `eval/baseline.md` with
# the date and the number of questions.
#
# Expect 30–55%. **If it comes out above 70%, the questions were too easy** — say so
# honestly and harden them before committing. A flattering baseline is worse than no
# baseline, because every improvement for the next nine weeks is measured against it.

# %% [markdown]
# ## Read the misses, not the number
#
# The number on its own teaches nothing. **Which** questions failed is the syllabus.
#
# On the seed set, the four `p0*` questions fail together. They ask the same things
# as `s01`, `s03`, `s04` and s.35 — but in the words an ordinary person would use:
# *regulator* not *Data Commissioner*, *leak* not *personal data breach*. The answers
# are provably in the corpus. TF-IDF cannot find them, because "notify the
# Commissioner" and "tell the regulator" share no terms and score near zero against
# each other.
#
# > That is **Flaw 2 — the index matches words, not meaning.** Owner: Session 04.
#
# Re-run exactly those four when Session 04 replaces the index with embeddings. If
# they do not become HITs, the embeddings are not earning their cost.

# %%
for q in questions:
    if q["id"].startswith("p"):
        print(f"{q['id']}  {q['question'][:66]}")
        for c, s in retrieve(q["question"], chunks, vectorizer, matrix)[:1]:
            print(f"      top hit [{s:.3f}] {c['source']} #{c['index']} — "
                  f"{'contains' if any(e.lower() in c['text'].lower() for e in expected_strings(q)) else 'does NOT contain'}"
                  " the answer\n")

# %% [markdown]
# ---
#
# **Measure first. Improve second. Never the other way round.**
