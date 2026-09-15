"""Sprint26 Q3 · Session 04 · two retrievers, then one.

Where this sits on the stack:
    Layer 2 — context and memory. Repairs FLAW 2, named on 5 August.

The easy version of this session is "embeddings are better than keyword search, so
we switch". That version is wrong, and the room proves it wrong inside twenty
minutes. Embeddings understand meaning and are bad at exact numbers and section
references — which is most of what this corpus contains. Keyword search is the
reverse.

So this module holds three retrievers, not one:

    search_sparse   BM25 over tokens          wins on s.43(3), "five million"
    search_dense    cosine over embeddings    wins on "how fast must we report a leak"
    search_fused    reciprocal rank fusion    wins on both, usually

The interesting engineering is in the combining.
"""

from __future__ import annotations

import re

import numpy as np

# --------------------------------------------------------------------------
# Sparse — BM25
# --------------------------------------------------------------------------
# WHY BM25 rather than the TF-IDF from Session 01. Two fixes, both of which matter
# on this corpus:
#
#   Saturation.  In TF-IDF a word appearing twenty times scores twenty times as
#                high. BM25 recognises that after a few occurrences more repetition
#                tells you very little, so the score levels off.
#   Length norm. A long passage contains more words and so matches more queries by
#                accident. BM25 discounts length so short precise passages compete.
#
# s.25 is long and mentions many terms; s.43(3) is one sentence and is the right
# answer more often. TF-IDF quietly favours the long one.

TOKEN = re.compile(r"\w+")


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def build_sparse(passages: list[dict]):
    from rank_bm25 import BM25Okapi

    return BM25Okapi([tokenize(p["text"]) for p in passages])


def search_sparse(question: str, bm25, passages: list[dict], k: int = 3) -> list[dict]:
    scores = bm25.get_scores(tokenize(question))
    order = np.argsort(scores)[::-1][:k]
    return [passages[i] for i in order]


# --------------------------------------------------------------------------
# Dense — cosine over embeddings
# --------------------------------------------------------------------------

def search_dense(question: str, model, matrix: np.ndarray, passages: list[dict],
                 k: int = 3) -> list[dict]:
    """Rows of `matrix` are unit length, so a dot product IS cosine similarity."""
    from src.embed import embed_texts

    q = embed_texts([question], model)[0]
    scores = matrix @ q
    order = np.argsort(scores)[::-1][:k]
    return [passages[i] for i in order]


# --------------------------------------------------------------------------
# Fusion — reciprocal rank fusion
# --------------------------------------------------------------------------
RRF_K = 60


def fuse(rankings: list[list[str]], k: int = RRF_K) -> list[tuple[str, float]]:
    """Combine ranked lists of passage ids using positions only.

    WHY the scores are thrown away rather than added. Cosine similarity runs 0 to 1.
    BM25 is unbounded and depends on corpus size and term rarity — a BM25 score of
    14.2 is meaningful only against other BM25 scores in the same run. Adding 0.83 to
    14.2 produces a number with no meaning, and the keyword side would dominate every
    result purely because its numbers are bigger.

    Positions are comparable across any two retrievers. Rank 1 is rank 1.

        rank 1 in both        1/61 + 1/61  = 0.0328
        rank 1 in one only    1/61         = 0.0164
        rank 3 in both        1/63 + 1/63  = 0.0317

    Read the last two lines together. A passage ranked third by BOTH retrievers beats
    one ranked first by only one of them — agreement between two different methods is
    stronger evidence than enthusiasm from one. That is the behaviour we want, and it
    is why k exists: it flattens the top of the curve so rank 1 cannot run away with
    the result.

    Cormack, Clarke and Buettcher (2009). Two pages, and the reason k=60 is the
    default everyone uses.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for position, passage_id in enumerate(ranking, start=1):
            scores[passage_id] = scores.get(passage_id, 0.0) + 1.0 / (k + position)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def search_fused(question: str, bm25, model, matrix, passages: list[dict],
                 k: int = 3, pool: int = 30) -> list[dict]:
    """Fuse BM25 and dense rankings.

    `pool` is how many candidates each retriever contributes. Rank fusion assumes
    comparable list lengths — if one retriever returns 30 and the other 3, the short
    list cannot express agreement past its third item and the long one dominates by
    default rather than by merit.
    """
    by_id = {p["passage_id"]: p for p in passages}
    sparse_ids = [p["passage_id"] for p in search_sparse(question, bm25, passages, pool)]
    dense_ids = [p["passage_id"] for p in search_dense(question, model, matrix, passages, pool)]
    ranked = fuse([sparse_ids, dense_ids])
    return [by_id[pid] for pid, _score in ranked[:k]]
