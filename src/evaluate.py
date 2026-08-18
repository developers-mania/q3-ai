"""Sprint26 Q3 · Session 02 · two numbers instead of one.

Where this sits on the stack:
    Layer 1 into Layer 5 — the measurement that Layer 1 finally makes possible.

Retrieval accuracy is unchanged from Session 01 and will barely move this week.
Say that out loud before the number appears, so it lands as a prediction confirmed
rather than a disappointment. Chunking has not changed, the index has not changed,
and retrieval works the way it did on 5 August.

What Session 02 makes possible is a SECOND measure that could not previously be
computed at all. Citation accuracy needs structure, and until this week there was
none: "does the retrieved passage carry the section the answer actually came from"
is not a question a flat string can answer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.pipeline import expected_strings, normalise_for_match

ROOT = Path(__file__).resolve().parent.parent
PASSAGES = ROOT / "passages.jsonl"
QUESTIONS = ROOT / "eval" / "questions.yaml"
SEED = ROOT / "eval" / "seed-questions.yaml"

TOP_K = 3


def load_passages() -> list[dict]:
    if not PASSAGES.exists():
        raise SystemExit(f"No {PASSAGES.name}. Run:  python -m src.ingest")
    return [json.loads(line) for line in PASSAGES.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_index(passages: list[dict]):
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([p["text"] for p in passages])
    return vectorizer, matrix


def retrieve(question: str, passages, vectorizer, matrix, k: int = TOP_K) -> list[dict]:
    scores = cosine_similarity(vectorizer.transform([question]), matrix)[0]
    return [passages[i] for i in scores.argsort()[::-1][:k]]


def section_of(citation: str) -> str:
    """'DPA s.43(1)(a)' -> 'DPA s.43'. Used only for the near-miss diagnostic."""
    return citation.split("(")[0].strip()


def citable(q: dict) -> bool:
    """Is this question's answer in a document that HAS citable structure?

    WHY exclude the Strategy: it has no scheme comparable to the Act's, so every
    passage from it carries the document-level citation "AIS". Counting those as
    citation hits would hand the metric two free correct answers and flatter it;
    counting them as misses would penalise retrieval for a property of the source
    document. Neither is a measurement. They are excluded and the count is printed,
    which is the only honest option — and it is the same judgement Session 03 makes
    again when it picks a chunking strategy per document.
    """
    return q["source"].startswith("DPA")


def evaluate(questions: list[dict], passages, vectorizer, matrix) -> dict:
    retrieval_hits = citation_hits = near = 0
    citable_n = 0
    rows = []
    for q in questions:
        results = retrieve(q["question"], passages, vectorizer, matrix)
        wanted = [normalise_for_match(s) for s in expected_strings(q)]
        found = any(any(w in normalise_for_match(p["text"]) for w in wanted) for p in results)

        top = results[0]
        scored = citable(q)
        citable_n += scored
        exact = scored and top["citation"] == q["source"]
        # Right section, wrong subsection. Not scored — it is the diagnostic that
        # tells you WHY citation accuracy is low, which is what Session 03 repairs.
        nearly = scored and (not exact) and section_of(top["citation"]) == section_of(q["source"])

        retrieval_hits += found
        citation_hits += exact
        near += nearly
        rows.append((q["id"], found, exact, nearly, top["citation"], q["source"], q["question"]))

    return {
        "rows": rows,
        "retrieval": retrieval_hits / len(questions) if questions else 0.0,
        "citation": citation_hits / citable_n if citable_n else 0.0,
        "near": near,
        "n": len(questions),
        "citable_n": citable_n,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Session 02 · retrieval AND citation accuracy")
    ap.add_argument("--questions", metavar="PATH", type=Path, default=QUESTIONS)
    ap.add_argument("--quiet", action="store_true", help="numbers only, no per-question rows")
    args = ap.parse_args()

    path = args.questions
    questions = yaml.safe_load(path.read_text(encoding="utf-8")) or [] if path.exists() else []
    if not questions:
        print(f"{path.name} is empty. That is expected until 3:40 — it is the room's set.")
        print(f"Working through this alone?  python -m src.evaluate --questions {SEED.relative_to(ROOT)}")
        return 0

    passages = load_passages()
    vectorizer, matrix = build_index(passages)
    result = evaluate(questions, passages, vectorizer, matrix)

    if not args.quiet:
        print(f"{'id':<5} {'RETR':<5} {'CITE':<5} top citation      expected")
        for qid, found, exact, nearly, got, want, _ in result["rows"]:
            mark = "OK  " if exact else ("near" if nearly else ("MISS" if want.startswith("DPA") else "n/a "))
            print(f"{qid:<5} {'HIT ' if found else 'MISS':<5} {mark:<5} {got:<17} {want}")
        print()

    seed = path.name != QUESTIONS.name
    tag = "SEED SET" if seed else "BASELINE"
    print(f"{tag} RETRIEVAL ACCURACY: {result['retrieval']:.0%}  ({result['n']} questions)")
    skipped = result["n"] - result["citable_n"]
    print(f"{tag} CITATION  ACCURACY: {result['citation']:.0%}  "
          f"({result['citable_n']} citable questions"
          + (f"; {skipped} excluded — the AI Strategy has no citable sections" if skipped else "") + ")")
    if result["near"]:
        print(f"           {result['near']} more retrieved the right SECTION but the wrong")
        print("           subsection. Until Session 03 that was the fixed-width cut straddling")
        print("           a boundary; after it, the usual cause is a chunk matching on text")
        print("           borrowed from its neighbour through overlap.")
    if seed:
        print("Not the cohort baseline — that is scored against eval/questions.yaml.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
