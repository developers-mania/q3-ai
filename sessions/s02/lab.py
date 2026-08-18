# %% [markdown]
# # Session 02 · Give the Corpus a Provenance
#
# **The question:** how does data get into a system reliably, and what breaks when
# it doesn't?
#
# This is the replay of what happened on screen. It imports from `src/` rather than
# restating the code, so there is one place to fix a bug.
#
# Nothing here needs an API key, an account, or a network connection.

# %%
import os
import sys
from pathlib import Path


def repo_root() -> Path:
    """Find the clone, from wherever this happens to be running.

    A notebook's working directory is the folder the .ipynb sits in - notebooks/ -
    not the repository root, so `import src...` would raise ModuleNotFoundError and
    every relative path would miss.
    """
    for base in (Path.cwd(), *Path.cwd().parents):
        if (base / "src" / "ingest.py").exists() and (base / "corpus").is_dir():
            return base
    raise SystemExit(
        f"Could not find the repository root from {Path.cwd()}.\n"
        "Run this from a clone of q3-ai - the folder holding corpus/ and src/.\n"
        "On session-02-start the Session 02 modules do not exist yet: they are built\n"
        "live in the room. Check out solution/session-02 to replay the finished lab."
    )


ROOT = repo_root()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
print(f"repo root : {ROOT}")
print(f"python    : {sys.executable}")

# %% [markdown]
# ## The failure this session is about
#
# Every failure so far has been visible. A wrong answer is wrong on the screen; a bad
# score is a bad number on the board.
#
# This one produces **no symptom at all**. When a source document changes and the
# index does not, the system keeps answering - fluently, confidently, in the same
# tone it uses when it is right - from a version of the truth that no longer exists.
# Nothing logs it. No test catches it. And the evaluation score does not move,
# *because the evaluation set was written against the old version too*.
#
# Session 01 established measurement as the discipline that catches problems.
# Staleness is the failure that defeats measurement, because the instrument and the
# system are wrong in the same direction at the same time.

# %% [markdown]
# ## 01 · Manifest and change detection
#
# Every source gets a record of where it came from, when it was retrieved, and a hash
# of what it contained. Change detection is then a comparison, not a guess.

# %%
import json  # noqa: E402

from src.ingest import CORPUS, MANIFEST, verify  # noqa: E402

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
for name, record in sorted(manifest["sources"].items()):
    print(name)
    print(f"    {record['title']}")
    print(f"    {record['publisher']}")
    print(f"    version   {record['version']}")
    print(f"    retrieved {record['retrieved']}")
    print(f"    sha256    {record['sha256'][:16]}")

print("\ndrifted:", verify() or "nothing - every source matches the manifest")

# %% [markdown]
# **The `version` field is the one people leave out and later wish they had not.**
# A hash tells you *that* something changed. A version tells you what it changed
# *from*, which is the difference between an alert and a diagnosis.

# %% [markdown]
# ### Change the world and tell nobody
#
# Doctor a source in memory and watch the fingerprint move. The file on disk is never
# touched - this is exactly the comparison the pipeline makes on every run.

# %%
import hashlib  # noqa: E402

original = (CORPUS / "dpa-2019.txt").read_bytes()
doctored = original.replace(b"seventy-two hours", b"twenty-four hours")
print(f"recorded  {manifest['sources']['dpa-2019.txt']['sha256'][:32]}")
print(f"on disk   {hashlib.sha256(original).hexdigest()[:32]}   <- matches")
print(f"doctored  {hashlib.sha256(doctored).hexdigest()[:32]}   <- refuses to ingest")
changed = sum(1 for a, b in zip(original, doctored) if a != b)
print(f"\none phrase changed, {changed} bytes differ, and the pipeline now stops.")

# %% [markdown]
# The system has not become smarter. It has become **capable of noticing**, which it
# previously was not.

# %% [markdown]
# ## 02 · Parse the Act into its structure
#
# The Act is not a string - it is a hierarchy of parts, sections, subsections and
# paragraphs, and every one of them has a number an answer can be cited against.

# %%
import collections  # noqa: E402

from src.parse import parse_act, strip_furniture  # noqa: E402

raw = (CORPUS / "dpa-2019.txt").read_text(encoding="utf-8")
_, dropped = strip_furniture(raw)
root, cleaned = parse_act(raw)

kinds = collections.Counter(n.kind for n in root.walk())
print(f"page-furniture lines removed: {dropped}")
print("nodes:", {k: v for k, v in kinds.items() if k != "document"})

sections = sorted({int(n.number) for n in root.walk() if n.kind == "section"})
missing = sorted(set(range(1, 76)) - set(sections))
print(f"sections {len(sections)}: {sections[0]}-{sections[-1]}, missing {missing or 'none'}")

# %% [markdown]
# ### Three things in this corpus break a naive parser
#
# The Content Pack's draft regex was `^PART\s+([IVXL]+)\s*[em-dash]` - uppercase,
# em-dash, column zero. It matches **nothing**. Budget five minutes for the room to
# find out why; that argument *is* the session.

# %%
import re  # noqa: E402

lines = raw.split("\n")

print("1. Part headings are title case, plain hyphen, and CENTRED (variable indent):")
for line in lines:
    if re.match(r"^\s*Part\s+[IVXL]+\s*-", line) and "...." not in line:
        print(f"     {line[:66]!r}")
        break
upper = sum(1 for line in lines if re.match(r"^PART\s+[IVXL]+", line))
print(f"     lines matching ^PART (uppercase, column zero): {upper}")

print("\n2. Every section number appears TWICE - contents page, then body:")
for i, line in enumerate(lines):
    if re.match(r"^\s*43\.\s", line):
        print(f"     line {i}: {line.strip()[:58]!r}")
print("     a parser that does not skip the contents finds the wrong one first")

banner = sum(1 for line in lines
             if "Data Protection Act (Cap. 411C)" in line and "Kenya" in line)
print(f"\n3. The running header sits INSIDE section text, not just at page edges: {banner}x")

# %% [markdown]
# ## 03 · The passage record and its schema
#
# Chunking stays naive this week - still fixed-width, still 500 characters, still
# cutting across meaning. What changes is that every chunk now knows **where it came
# from**. Fixing the cut itself is Session 03's job, and keeping the two separate is
# what makes next week's improvement measurable in isolation.

# %%
from src.ingest import build_candidates  # noqa: E402
from src.passage import Passage  # noqa: E402

candidates = build_candidates()
print(f"{len(candidates):,} candidate passages\n")
print(Passage(**candidates[400]).model_dump_json(indent=2)[:520])

# %% [markdown]
# Note what the schema makes **impossible**: a passage with no source, a passage with
# no citation, and a passage of pure whitespace. Session 01's pipeline produced all
# three without complaint.

# %% [markdown]
# ## 04 · Boundary validation and quarantine
#
# Validation is half the design. The other half is what happens when it fails, and
# there are four options of which only one is correct.
#
# | Option | What happens | Verdict |
# |---|---|---|
# | Crash | one bad record halts all ingestion | disproportionate |
# | Skip silently | the record vanishes, nothing logged | **the worst option** - indistinguishable from success |
# | Coerce | force it into shape and hope | plausible garbage, very hard to trace |
# | Quarantine | reject with the reason, keep going | **correct** |

# %%
from src.publish import publish  # noqa: E402

accepted, rejected = publish(candidates)
print(f"accepted {len(accepted):,}   quarantined {rejected}")

# %% [markdown]
# ### Break the schema on purpose
#
# Nothing quarantines on a clean corpus, which makes the dead-letter path easy to
# believe in and never see. So break it: strip the citation off a hundred passages and
# confirm they are **rejected with a reason**, not silently dropped.

# %%
import copy  # noqa: E402

broken = copy.deepcopy(candidates)
for candidate in broken[:100]:
    candidate["citation"] = "   "

demo = ROOT / "quarantine-demo.jsonl"
kept, lost = publish(broken, quarantine=demo)
print(f"accepted {len(kept):,}   quarantined {lost}")

print("\nfirst quarantined record, as a human would read it:")
first = json.loads(demo.read_text(encoding="utf-8").splitlines()[0])
print(json.dumps(first["errors"], indent=2))
print("payload text:", first["payload"]["text"][:70])
demo.unlink()

# %% [markdown]
# Nothing was lost and nothing was guessed. **What would Session 01's pipeline have
# done?** It had no schema, so it indexed everything - including the whitespace-only
# chunks, which are still in that index.

# %% [markdown]
# ## 05 · Idempotent publish
#
# An ingestion step is idempotent if running it twice produces the same result as
# running it once. Not a refinement - it is the property that makes a pipeline safe to
# retry, and retries are inevitable.

# %%
from src.passage import passage_id  # noqa: E402

a = passage_id("dpa-2019.txt", "DPA s.43(1)", 69000, "text")
b = passage_id("dpa-2019.txt", "DPA s.43(1)", 69000, "text")
print(f"same content, same position -> {a} == {b}   {a == b}")

ids_run1 = sorted(p.passage_id for p in publish(build_candidates())[0])
ids_run2 = sorted(p.passage_id for p in publish(build_candidates())[0])
print(f"\nrun 1: {len(ids_run1):,} passages")
print(f"run 2: {len(ids_run2):,} passages")
print(f"identifier SETS identical: {ids_run1 == ids_run2}")

# %% [markdown]
# The count is the **weak** test. The strong test is that the set of *identifiers* is
# identical - that catches the case where the same number of passages is produced with
# different identities. Compare the sorted id list, not the line count.
#
# With `uuid4()` instead, re-running would double the corpus, retrieval would return
# duplicates, and the score would move for a reason unconnected to quality.

# %% [markdown]
# ## 06 · Re-run, and meet the second number
#
# Retrieval accuracy will **barely move** - chunking has not changed, the index has not
# changed, retrieval works the way it did on 5 August. Say that out loud before the
# number appears, so it lands as a prediction confirmed rather than a disappointment.

# %%
import yaml  # noqa: E402

from src.evaluate import build_index, evaluate, load_passages  # noqa: E402
from src.ingest import write_passages  # noqa: E402

write_passages(accepted)

room = yaml.safe_load(Path("eval/questions.yaml").read_text(encoding="utf-8")) or []
if room:
    questions, source_file = room, "eval/questions.yaml"
else:
    questions = yaml.safe_load(Path("eval/seed-questions.yaml").read_text(encoding="utf-8")) or []
    source_file = "eval/seed-questions.yaml"
    print("eval/questions.yaml is empty - that is the room's file, written at 3:40.")
    print("Falling back to the seed set so this replay produces numbers.\n")

passages = load_passages()
vectorizer, matrix = build_index(passages)
result = evaluate(questions, passages, vectorizer, matrix)

print(f"{'id':<5} {'RETR':<5} {'CITE':<5} top citation      expected")
for qid, found, exact, nearly, got, want, _q in result["rows"]:
    if exact:
        mark = "OK  "
    elif nearly:
        mark = "near"
    elif want.startswith("DPA"):
        mark = "MISS"
    else:
        mark = "n/a "
    print(f"{qid:<5} {'HIT ' if found else 'MISS':<5} {mark:<5} {got:<17} {want}")

excluded = result["n"] - result["citable_n"]
print(f"\nRETRIEVAL ACCURACY: {result['retrieval']:.0%}   "
      f"({result['n']} questions from {source_file})")
print(f"CITATION  ACCURACY: {result['citation']:.0%}   "
      f"({result['citable_n']} citable; {excluded} excluded - the Strategy has no sections)")
print(f"{result['near']} more retrieved the right SECTION but the wrong subsection.")

# %% [markdown]
# ## Read the misses, not the number
#
# **Citation accuracy came out poor, and that is the session working.**
#
# Look at the `near` rows. The 48-hour deadline lives in `s.43(3)`; the passage that
# contains it is tagged `s.43(2)`. The 90-day period lives in `s.56(5)`; its passage is
# tagged `s.56(4)`. In every case retrieval was *right* and the citation was *wrong by
# one subsection*.
#
# That is not a parser bug. Print the offending passage and the cause is obvious:

# %%
def flatten(text: str) -> str:
    return " ".join(text.replace("-", " ").split()).lower()


passage = next(p for p in passages if "forty eight hours" in flatten(p["text"]))
print(f"citation: {passage['citation']}   offset: {passage['offset']}")
print(f"starts:  {passage['text'][:96].strip()}")
print(f"ends:    {passage['text'][-96:].strip()}")

# %% [markdown]
# The chunk **starts** inside subsection (2), runs through (3), and ends inside (4).
# It can only be tagged with one of them, and it is tagged with the one it started in.
#
# > **Flaw 5 is half repaired.** Every passage can now cite a source - but a
# > fixed-width cut across a boundary cites the wrong one. Owner of the other half:
# > **Session 03**, which stops cutting by the character and starts cutting by meaning.
#
# The room has just measured, precisely, why chunking on meaning matters. Next week
# they fix it.
#
# ---
#
# **Data carries its provenance. A passage that cannot cite its own source does not
# reach an index.**
