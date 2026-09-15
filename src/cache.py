"""Sprint26 Q3 · Session 04 · a semantic cache, and how it serves a wrong answer.

Where this sits on the stack:
    Layer 2 — context and memory.

A semantic cache stores past queries with their results. A new query close enough to
a stored one gets the stored answer without searching. It is a good idea and it is
genuinely faster.

It is also the clearest demonstration this quarter of a system doing exactly what it
was built to do and being wrong because of it. The near-miss pair the room wrote on
5 August — controller notifies the Commissioner in 72 hours, processor notifies the
controller in 48 — are two questions that mean almost the same thing. That is
precisely why they were written. A cache keyed on meaning cannot tell them apart,
and once the first is cached the second gets its answer.

Nothing errors. The wrong answer arrives FASTER than the right one used to.
"""

from __future__ import annotations

import numpy as np

THRESHOLD = 0.95


class SemanticCache:
    """Return a stored result when a new query is close enough to an old one."""

    def __init__(self, threshold: float = THRESHOLD):
        self.threshold = threshold
        self.entries: list[tuple[np.ndarray, str, list]] = []
        self.hits = 0
        self.misses = 0

    def get(self, query_vec: np.ndarray):
        """Nearest stored query above the threshold, or None.

        A linear scan, and honestly so. Fine for a demonstration; at ten thousand
        cached queries this compares against ten thousand vectors on every request,
        which costs more than the search it was avoiding. A real one uses the same
        kind of index as the corpus.
        """
        best, best_score, best_query = None, -1.0, ""
        for stored_vec, stored_query, results in self.entries:
            score = float(stored_vec @ query_vec)
            if score > best_score:
                best, best_score, best_query = results, score, stored_query
        if best is not None and best_score >= self.threshold:
            self.hits += 1
            return best, best_score, best_query
        self.misses += 1
        return None

    def put(self, query_vec: np.ndarray, query: str, results: list) -> None:
        self.entries.append((query_vec, query, results))


def cached_search(question, cache, model, search_fn, k=3):
    """Check the cache, then search. Returns (results, was_cached, evidence).

    Note the order, because it is the first honest correction of this step: the query
    must be EMBEDDED before the cache can be checked at all. Locally the embedding is
    the slow part. The cache saves the search, not the embedding — which is much less
    than people assume they are buying.
    """
    from src.embed import embed_texts

    q_vec = embed_texts([question], model)[0]
    hit = cache.get(q_vec)
    if hit is not None:
        results, score, source_query = hit
        return results, True, (score, source_query)
    results = search_fn(question, k)
    cache.put(q_vec, question, results)
    return results, False, (1.0, question)
