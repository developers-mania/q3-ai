"""Sprint26 Q3 · Session 01 · What Changed.

Question this answers:
    What actually changed in how software is built, and what does it mean for the
    work I already do?

Where this sits on the stack:
    Layers 1 and 2 — data infrastructure and context — built badly on purpose.

Four functions, about forty lines of substance. Each makes the laziest defensible
choice available. Those choices are not mistakes; they are the syllabus. Every one
is repaired in a named later session and the repair is measured against the number
this file prints today.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
QUESTIONS = ROOT / "eval" / "questions.yaml"

CHUNK_SIZE = 500  # characters — chosen for no reason at all
TOP_K = 3


# --------------------------------------------------------------------------
# 01 · Load the corpus                                            3:00 – 3:06
# --------------------------------------------------------------------------

def load_documents() -> dict[str, str]:
    """Read every .txt in corpus/ into a {filename: text} mapping.

    No parsing, no cleaning, no metadata. Deliberately the least work that
    produces something loadable.
    """
    docs = {}
    for path in sorted(CORPUS.glob("*.txt")):
        docs[path.name] = path.read_text(encoding="utf-8")
    return docs


# Ask the room before moving on: "What have we already thrown away?"
# Section numbering. Part headings. The difference between a section and a
# schedule. The fact that one document is binding law and the other is policy.
# All of it is still present as characters and absent as STRUCTURE.
# That distinction is Sessions 02 and 03.


# --------------------------------------------------------------------------
# 02 · Chunk it badly                                             3:06 – 3:14
# --------------------------------------------------------------------------

def chunk(text: str, size: int = CHUNK_SIZE) -> list[str]:
    """Cut text into fixed-size pieces. No overlap. No respect for meaning."""
    return [text[i:i + size] for i in range(0, len(text), size)]


def build_chunks(docs: dict[str, str]) -> list[dict]:
    chunks = []
    for name, text in docs.items():
        for i, piece in enumerate(chunk(text)):
            chunks.append({"source": name, "index": i, "text": piece})
    return chunks


# FLAW 1: chunks cut across meaning. Owner: Session 03.
#   A cut landing between "seventy-two" and "hours" destroys the answer in both
#   halves. No overlap means no second chance.
# FLAW 5: a chunk knows it is characters 41,500–42,000 of a file. It does not know
#   it came from s.43(3), so nothing built on it can cite a source.
#   Owner: Session 03.
#
# DPA s.43: this is the passage to print aloud. A 500-character window straddling
# the section boundary carries the words "seventy-two hours" with no indication of
# whose deadline it is, or that a second, different deadline follows a few lines
# later in s.43(3).


# --------------------------------------------------------------------------
# 03 · Index it badly                                             3:14 – 3:20
# --------------------------------------------------------------------------

def build_index(chunks: list[dict]):
    """Keyword matching, nothing more. No embeddings until Session 04."""
    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix


# FLAW 2: the index matches words, not meaning. Owner: Session 04.
#   "Notify the Commissioner" and "inform the regulator" share no terms and score
#   near zero against each other. WHY keep it anyway: TF-IDF is fast, needs no
#   model, runs offline, and is genuinely good at the things embeddings are bad at
#   — statute numbers and proper nouns. Session 04's hybrid search keeps a sparse
#   component for exactly that reason.


# --------------------------------------------------------------------------
# 04 · Retrieve                                                   3:20 – 3:26
# --------------------------------------------------------------------------

def retrieve(question: str, chunks, vectorizer, matrix, k: int = TOP_K):
    """Return the k highest-scoring chunks. No re-ranking. No threshold."""
    query = vectorizer.transform([question])
    scores = cosine_similarity(query, matrix)[0]
    ranked = scores.argsort()[::-1][:k]
    return [(chunks[i], float(scores[i])) for i in ranked]


# FLAW 3: no re-ranking; the first plausible match wins. Owner: Session 05.
# FLAW 4: no confidence threshold; if every chunk scores 0.02 the system still
#   returns three of them and still answers. It has no way to say "I don't know",
#   which is the single most valuable sentence a retrieval system can produce.
#   Owner: Session 09.


# --------------------------------------------------------------------------
# 06 · Score it                                                   3:40 – 3:50
# --------------------------------------------------------------------------

def normalise_for_match(text: str) -> str:
    """Lowercase, collapse whitespace, treat hyphens as spaces.

    WHY: two ways a perfect retrieval scores MISS on a raw substring test. The PDF is
    hard-wrapped at ~80 columns, so s.56(5) reads "ninety\\ndays" and "ninety days" is
    not in it. And the Act writes "seventy-two hours" where a question writer types
    "seventy two hours". Both are typography, not retrieval. This does not soften
    Flaw 1 — a chunk boundary falling between "seventy-two" and "hours" still misses,
    because the two halves are in different chunks.
    """
    return " ".join(text.replace("-", " ").split()).lower()


def expected_strings(q: dict) -> list[str]:
    """Surface forms that count as the answer being present in a chunk.

    WHY this is not just q["answer"]: statutes spell numbers out in words. The Act
    says "seventy-two hours"; the answer written on the board is "72 hours". A
    substring test against the board answer scores MISS on a perfect retrieval.
    `expect` holds every form the corpus might actually use; `answer` stays
    human-readable. Falls back to `answer` so a question written without `expect`
    still scores rather than crashing.
    """
    return q.get("expect") or [q["answer"]]


def score(questions: list[dict], chunks, vectorizer, matrix) -> float:
    """Retrieval accuracy: did a chunk containing the answer reach the top three?

    Deliberately narrow. Not whether a model phrased a good answer — whether the
    right passage was found at all. WHY: this metric needs no model, no network and
    no API key, and it returns the identical number every run. For Sessions 01–05,
    which are entirely about Layers 1 and 2, that is the sharper instrument.
    """
    hits = 0
    for q in questions:
        results = retrieve(q["question"], chunks, vectorizer, matrix)
        wanted = [normalise_for_match(s) for s in expected_strings(q)]
        found = any(
            any(w in normalise_for_match(c["text"]) for w in wanted)
            for c, _ in results
        )
        hits += found
        print(f"{q['id']}  {'HIT ' if found else 'MISS'}  {q['question'][:52]}...")
    return hits / len(questions) if questions else 0.0


# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Session 01 · the naive pipeline")
    parser.add_argument("--score", action="store_true", help="run the evaluation set")
    parser.add_argument("--ask", metavar="QUESTION", help="retrieve against one question")
    args = parser.parse_args()

    docs = load_documents()
    if not docs:
        print(f"No .txt files in {CORPUS}. See corpus/README.md.")
        return 1
    for name, text in docs.items():
        print(f"{name:28} {len(text):>8,} characters")

    chunks = build_chunks(docs)
    print(f"{'chunks':28} {len(chunks):>8,}")
    vectorizer, matrix = build_index(chunks)

    if args.ask:
        print()
        for c, s in retrieve(args.ask, chunks, vectorizer, matrix):
            print(f"[{s:.3f}] {c['source']} #{c['index']}")
            print(f"  {c['text'][:300]}...\n")

    if args.score:
        questions = yaml.safe_load(QUESTIONS.read_text()) or []
        if not questions:
            print("\neval/questions.yaml is empty. That is expected until 3:40.")
            return 0
        print()
        accuracy = score(questions, chunks, vectorizer, matrix)
        print(f"\nBASELINE RETRIEVAL ACCURACY: {accuracy:.0%}  ({len(questions)} questions)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
