"""Sprint26 Q3 · Session 05 · Remembering The Right Thing.

Question this answers:
    How do you make retrieval accurate instead of merely plausible?

Where this sits on the stack:
    Layer 2 — context and memory. Repairs FLAW 3, named on 5 August.

Everything built so far encodes the question and the passages SEPARATELY, then
compares the results. That is a bi-encoder, and it has one enormous advantage:
passages are encoded in advance, so searching 571 of them costs one encoding plus
571 cheap comparisons. It is why search is fast.

Here is what it gives up. When a passage was encoded, the model had no idea what
would be asked. It produced ONE fixed summary that has to serve every possible
question — and for s.43(1) and s.43(3) those summaries are nearly identical, because
both are about breach notification, deadlines and the parties involved. The
distinction between "controller notifies Commissioner" and "processor notifies
controller" is exactly the fine detail a single fixed summary flattens away. The
information needed to separate them was discarded at indexing time, and no
comparison of the resulting vectors can recover it.

A cross-encoder does the opposite: question and passage go into the model TOGETHER
and one relevance score comes out. Because both texts are present at once, the model
can compare individual words across them.

    bi-encoder     571 passages = 1 model pass at query time.  Fast, approximate.
    cross-encoder  571 passages = 571 model passes.            Slow, accurate.

So the cross-encoder is not a better retriever. It is a better JUDGE, and judges are
expensive, so you only bring them a shortlist.

    STAGE 1   fused retrieval      571 passages  ->  30 candidates
    STAGE 2   cross-encoder        30 candidates ->   3 passages

Stage 1's job changes accordingly. It is no longer trying to put the right answer at
rank 1 — it only has to get the answer SOMEWHERE in the shortlist, which is a much
easier job and one Session 04 measured it doing about 80% of the time.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "ms-marco-MiniLM-L-6-v2"

SHORTLIST = 30
FINAL_K = 3


def load_reranker():
    """Load the cross-encoder from disk. No network call is made."""
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    if not MODEL_PATH.exists():
        raise SystemExit(
            f"No cross-encoder at {MODEL_PATH.relative_to(ROOT)}.\n"
            "    python tools/fetch_models.py"
        )
    from sentence_transformers import CrossEncoder

    return CrossEncoder(str(MODEL_PATH))


def parent_citations(citation: str) -> list[str]:
    """'DPA s.43(1)(a)' -> ['DPA s.43(1)', 'DPA s.43'], innermost first."""
    out, current = [], citation
    while "(" in current:
        current = current.rsplit("(", 1)[0].strip()
        out.append(current)
    return out


def with_parent_stem(passage: dict, by_citation: dict[str, dict]) -> str:
    """Put back the words the cut took away.

    Structure-aware chunking cuts at the deepest marker, which means a paragraph is
    separated from the stem that governs it. In the Act that is not cosmetic:

        s.43     "...a data controller shall-"          <- the SUBJECT lives here
        s.43(1)(a)  "notify the Data Commissioner ... within seventy-two hours"

    The chunk holding the 72-hour answer does not contain the word "controller" at
    all. A judge asked "how long does a data CONTROLLER have" sees a passage that
    never mentions one, and prefers s.43(3), which mentions both roles. The
    re-ranker is not failing; it is reading a passage that was severed from its
    subject.

    Session 03 said chunking is the one decision later sophistication cannot
    compensate for. This is that sentence arriving two weeks later, in the most
    sophisticated component built so far.
    """
    stems = [by_citation[c]["text"] for c in parent_citations(passage["citation"])
             if c in by_citation]
    if not stems:
        return passage["text"]
    return " ".join(reversed(stems)) + " " + passage["text"]


def rerank(question: str, candidates: list[dict], model, k: int = FINAL_K,
           by_citation: dict[str, dict] | None = None) -> list[tuple[dict, float]]:
    """Score each (question, passage) pair by reading them together."""
    if not candidates:
        return []
    texts = ([with_parent_stem(c, by_citation) for c in candidates]
             if by_citation else [c["text"] for c in candidates])
    scores = model.predict([[question, t] for t in texts])
    ranked = sorted(zip(candidates, scores), key=lambda x: float(x[1]), reverse=True)
    return [(c, float(s)) for c, s in ranked[:k]]


def two_stage(question: str, bm25, embed_model, matrix, passages: list[dict],
              reranker, k: int = FINAL_K, shortlist: int = SHORTLIST,
              by_citation: dict[str, dict] | None = None) -> list[dict]:
    """The architecture: a wide cheap net, then a careful expensive read."""
    from src.retrieve import search_fused

    candidates = search_fused(question, bm25, embed_model, matrix, passages,
                              k=shortlist, pool=shortlist)
    return [p for p, _score in rerank(question, candidates, reranker, k, by_citation)]


def shortlist_recall(questions, shortlists, hit_fn) -> float:
    """How often is the right answer even IN the shortlist?

    This is the ceiling on what re-ranking can achieve. If recall is 80% then no
    re-ranker scores above 80% — a fifth of the time the answer was never handed to
    it. Comparing this number against the re-ranked score is what tells you whether
    to invest in Stage 1 or Stage 2 next, and it is the first measurement this
    quarter that points at what to do rather than reporting what happened.
    """
    return sum(hit_fn(q, shortlists[q["id"]]) for q in questions) / len(questions)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Session 05 · cross-encoder re-ranking")
    ap.add_argument("--check", action="store_true", help="load both models, offline")
    args = ap.parse_args()

    if args.check:
        from src.embed import load_model

        load_model()
        load_reranker()
        print("bi-encoder ok, cross-encoder ok, no network used")
        return 0
    print("Nothing to do. Use --check, or python -m src.evaluate --retriever reranked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
