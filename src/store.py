"""Sprint26 Q3 · Session 05 · a vector database, honestly.

Where this sits on the stack:
    Layer 2 — context and memory.

The usual reason given for moving an index into a vector database is speed. At 571
passages that reason is false, and saying so is part of the session.

    Speed        No. Session 04's numpy dot product over 571 unit vectors is already
                 fast. A database will not beat it and does not claim to.
    Persistence  Yes. The index survives a restart instead of being rebuilt each run.
    Filtering    Yes. "Only Part IV", "exclude schedules" becomes a query rather
                 than a workaround downstream.
    Scale        Not yet. HNSW indexing matters at millions of vectors. Worth
                 understanding; not worth pretending we need it today.

HNSW — Hierarchical Navigable Small World — is the index structure most vector
databases use: a layered graph where upper layers hold long links for fast routing
and lower layers hold short links for accurate local search. Two parameters matter,
M (links per node) and efConstruction (how hard the build works), and both trade
memory and build time for recall. At this corpus size the defaults are right and
tuning them would be theatre.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
STORE_PATH = ROOT / "chroma"
COLLECTION = "q3_corpus"


def build_store(passages: list[dict], embeddings: np.ndarray, path: Path = STORE_PATH):
    """Persist the passages and THEIR OWN embeddings.

    ------------------------------------------------------------------------
    PASS `embeddings=` EXPLICITLY, OR THE SESSION BREAKS SILENTLY
    ------------------------------------------------------------------------
    If the embeddings argument is omitted, ChromaDB embeds the documents itself
    using its own default model — which it downloads, and which is NOT the model
    Session 04 used.

    Nothing would error. The index would build, queries would return results, and
    the numbers would move. You would be comparing this week's system against a
    differently-embedded index, and every conclusion drawn from the comparison
    would be wrong.

    It is worth ninety seconds of the room's attention, because it is the exact
    shape of failure this quarter keeps meeting: the pipeline reports success and
    the measurement is quietly invalid. Session 02's stale index, Session 03's
    over-redaction, Session 04's cache — same failure, new week.
    """
    import chromadb

    client = chromadb.PersistentClient(path=str(path))
    collection = client.get_or_create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"}
    )
    collection.upsert(
        ids=[p["passage_id"] for p in passages],
        documents=[p["text"] for p in passages],
        embeddings=embeddings.tolist(),  # <- the line above is about this line
        metadatas=[
            {
                "citation": p["citation"],
                "section": p["section"] or "",
                "part": p["part"] or "",
                "source": p["source"],
            }
            for p in passages
        ],
    )
    return collection


def load_store(path: Path = STORE_PATH):
    import chromadb

    client = chromadb.PersistentClient(path=str(path))
    return client.get_or_create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"}
    )


def search_store(question: str, collection, embed_model, passages: list[dict],
                 k: int = 3, where: dict | None = None) -> list[dict]:
    """Query by vector, optionally filtered on metadata.

    The filter is the feature that actually justifies the database here. Restricting
    to a Part, or excluding schedules, is one argument rather than a post-hoc filter
    that quietly returns fewer than k results.
    """
    from src.embed import embed_texts

    q = embed_texts([question], embed_model)[0]
    result = collection.query(
        query_embeddings=[q.tolist()],
        n_results=k,
        where=where or None,
    )
    by_id = {p["passage_id"]: p for p in passages}
    return [by_id[i] for i in result["ids"][0] if i in by_id]
