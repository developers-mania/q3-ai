"""Sprint26 Q3 · Session 04 · Giving Software Memory.

Question this answers:
    How does an application recall things it was not trained on?

Where this sits on the stack:
    Layer 2 — context and memory.

An embedding is a list of numbers that represents a piece of text, arranged so that
text with similar meaning gets similar numbers. That is the whole idea; the rest is
detail about how the numbers are produced and how "similar" is measured.

Two things worth being precise about, because both cause confusion later:

    The numbers mean nothing on their own. No single position in the list
    corresponds to a concept you could name. Only distances between whole lists
    carry information.

    A model produced them. It learned, from a large amount of text, which words
    appear in similar contexts. That is where the sense of "meaning" comes from —
    and it is also why the model's blind spots become your blind spots.

DPA s.50: the model runs on this laptop. Most tutorials call a hosted service, which
means every passage of the corpus and every question a user asks is sent to a third
party, usually outside Kenya. Section 50 permits the Cabinet Secretary to require
that certain processing happen only through a server or data centre located in
Kenya, and the National AI Strategy puts data sovereignty among its central
concerns. Running locally is not a limitation imposed by the venue. It is the
architecture Session 08 makes permanent, and it starts here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "all-MiniLM-L6-v2"
CACHE = ROOT / "models" / "corpus-embeddings.npz"


def load_model():
    """Load the bi-encoder from disk. No network call is made.

    WHY the offline environment variables: without them a missing or half-written
    model directory silently falls back to downloading from the hub, and the session
    would appear to work while quietly doing the exact thing s.50 is about. Better to
    fail loudly.
    """
    import os

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    if not MODEL_PATH.exists():
        raise SystemExit(
            f"No model at {MODEL_PATH.relative_to(ROOT)}.\n"
            "    python tools/fetch_models.py"
        )
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(str(MODEL_PATH))


def fingerprint(passages: list[dict]) -> str:
    """Identity of the corpus AS CHUNKED, so a stale cache can be detected.

    WHY this exists at all: embeddings are a derived artifact, and Session 02 was
    about exactly this failure — a downstream copy that keeps serving answers after
    the thing it was derived from has changed, with nothing raising an error. Change
    the chunker, or the overlap, or the redaction rule, and every vector in the cache
    describes text that no longer exists. Nothing would break. The numbers would just
    quietly mean something else.
    """
    h = hashlib.sha256()
    for p in passages:
        h.update(p["passage_id"].encode("utf-8"))
        h.update(p["text"].encode("utf-8"))
    return h.hexdigest()


def embed_texts(texts: list[str], model=None) -> np.ndarray:
    """Encode texts to unit-length vectors.

    normalize_embeddings=True makes every row length 1, which means a dot product
    IS cosine similarity — no division needed at query time. That is worth the one
    flag: the search in src/retrieve_dense.py is then a single matrix multiply.
    """
    model = model or load_model()
    return model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 200,
    )


def embed_corpus(passages: list[dict], model=None, use_cache: bool = True) -> np.ndarray:
    """Embed every passage, reusing the cache when the corpus has not changed."""
    fp = fingerprint(passages)
    if use_cache and CACHE.exists():
        stored = np.load(CACHE, allow_pickle=False)
        if str(stored["fingerprint"].item()) == fp:
            return stored["matrix"]
        print("corpus changed since the embeddings were cached — re-embedding")

    matrix = embed_texts([p["text"] for p in passages], model)
    CACHE.parent.mkdir(exist_ok=True)
    np.savez_compressed(CACHE, matrix=matrix, fingerprint=np.array(fp))
    return matrix


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Session 04 · local embeddings")
    ap.add_argument("--check", action="store_true", help="load the model and report")
    args = ap.parse_args()

    if args.check:
        model = load_model()
        dims = model.get_sentence_embedding_dimension()
        print(f"model loaded, {dims} dimensions, no network used")
        return 0

    from src.evaluate import load_passages

    passages = load_passages()
    matrix = embed_corpus(passages)
    print(f"{matrix.shape[0]:,} passages embedded to {matrix.shape[1]} dimensions")
    print(f"cached in {CACHE.relative_to(ROOT)}")

    # A sanity check the room can read: similar meaning should score high, unrelated
    # text low, and neither number should need explaining.
    a, b, c = embed_texts([
        "notify the Commissioner of a personal data breach",
        "tell the regulator we have been hacked",
        "agricultural subsidies for smallholder farmers",
    ])
    print(f"\n  notify/tell      cosine {float(a @ b):.3f}   <- same meaning, no shared words")
    print(f"  notify/farming   cosine {float(a @ c):.3f}   <- unrelated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
