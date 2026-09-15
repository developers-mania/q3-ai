"""Sprint26 Q3 · Session 04 · which retriever wins which question.

"Which retriever is better" has no answer. "Which questions does each one win" has
a very clear one, and it falls out of the corpus rather than out of an opinion.

    keyword wins   section references, deadlines, monetary amounts, proper nouns
    dense wins     paraphrased and conceptual questions

The corpus is a statute. Its content is section numbers, deadlines and amounts —
the exact categories where embeddings are weakest. A room that switched wholesale
from keyword to dense today would watch questions that passed on 19 August start
failing. That is not hypothetical; it is what this module prints.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from src.evaluate import evaluate_with, load_passages
from src.pipeline import expected_strings, normalise_for_match

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "eval" / "questions.yaml"
TOP_K = 3


def hit(question: dict, results: list[dict]) -> bool:
    wanted = [normalise_for_match(s) for s in expected_strings(question)]
    return any(any(w in normalise_for_match(p["text"]) for w in wanted) for p in results)


def build_all(passages):
    """Return the three search functions, each closed over its own index."""
    from src.embed import embed_corpus, load_model
    from src.retrieve import build_sparse, search_dense, search_fused, search_sparse

    model = load_model()
    matrix = embed_corpus(passages, model)
    bm25 = build_sparse(passages)

    return {
        "sparse": lambda q, k=TOP_K: search_sparse(q, bm25, passages, k),
        "dense": lambda q, k=TOP_K: search_dense(q, model, matrix, passages, k),
        "fused": lambda q, k=TOP_K: search_fused(q, bm25, model, matrix, passages, k),
    }, model, matrix, bm25


def main() -> int:
    ap = argparse.ArgumentParser(description="Session 04 · compare retrievers per question")
    ap.add_argument("--questions", type=Path, default=QUESTIONS)
    args = ap.parse_args()

    questions = yaml.safe_load(args.questions.read_text(encoding="utf-8")) or []
    passages = load_passages()
    searchers, *_ = build_all(passages)

    results = {name: {q["id"]: hit(q, fn(q["question"])) for q in questions}
               for name, fn in searchers.items()}

    print(f"{'id':<5} {'keyword':<9} {'dense':<7} {'fused':<7} question")
    print("-" * 78)
    only_sparse, only_dense, neither = [], [], []
    for q in questions:
        s, d, f = (results[n][q["id"]] for n in ("sparse", "dense", "fused"))
        mark = lambda b: "HIT " if b else "MISS"  # noqa: E731
        flag = ""
        if s and not d:
            only_sparse.append(q["id"]); flag = "  <- keyword only"
        elif d and not s:
            only_dense.append(q["id"]); flag = "  <- dense only"
        elif not s and not d:
            neither.append(q["id"]); flag = "  <- neither"
        print(f"{q['id']:<5} {mark(s):<9} {mark(d):<7} {mark(f):<7} {q['question'][:38]}…{flag}")

    print()
    for name, fn in searchers.items():
        r = evaluate_with(questions, passages, fn)
        print(f"{name:<8} retrieval {r['retrieval']:>4.0%}   citation {r['citation']:>4.0%}")

    print(f"\nkeyword won alone : {only_sparse or 'none'}")
    print(f"dense won alone   : {only_dense or 'none'}")
    print(f"neither found it  : {neither or 'none'}")
    print("\nAsk the room to name the pattern before you do.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
