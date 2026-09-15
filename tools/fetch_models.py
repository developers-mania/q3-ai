"""Sprint26 Q3 · fetch the local models, once.

Sessions 04 and 05 run two models on the laptop. Neither needs a key, an account,
or a network connection — *after* this script has run once.

    python tools/fetch_models.py            # both models, ~180 MB total
    python tools/fetch_models.py --check    # verify they load, offline

WHY the models are not committed to the branch:
    The Session 04 Content Pack says "bundle the model in the branch or bring it on
    USB", and the second half of that sentence is the one this repository takes.
    Each model is roughly 90 MB. Committing both would take a 1.2 MB clone to about
    180 MB permanently, for every participant and every remaining session — and git
    stores binary blobs badly, so every re-commit adds another full copy.

    What the room was actually promised is that the session runs offline. That
    promise is kept by fetching once, not by committing. A facilitator with a slow
    venue connection copies models/ onto a USB stick and hands it round, which is
    faster than twenty laptops pulling 180 MB over the same wifi at 2:05.

WHY these two models specifically:
    all-MiniLM-L6-v2 is a BI-ENCODER: it turns one text into one vector, so passages
    can be embedded in advance and searched with a dot product. 384 dimensions,
    small enough to run on CPU.

    ms-marco-MiniLM-L-6-v2 is a CROSS-ENCODER: it reads a question and a passage
    TOGETHER and scores the pair. It cannot be pre-computed, so it is far too slow to
    search with — it is used in Session 05 to re-read a shortlist the fast retriever
    has already narrowed down.

    The difference between those two sentences is the whole of Session 05.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"

# (local directory, hub id, kind) — kind decides which loader verifies it.
WANTED = [
    ("all-MiniLM-L6-v2", "sentence-transformers/all-MiniLM-L6-v2", "bi"),
    ("ms-marco-MiniLM-L-6-v2", "cross-encoder/ms-marco-MiniLM-L-6-v2", "cross"),
]


def human(n: int) -> str:
    return f"{n / 1_048_576:.0f} MB"


def size_of(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def fetch(name: str, hub_id: str, kind: str, force: bool = False) -> bool:
    target = MODELS / name
    if target.exists() and not force:
        print(f"OK    {name:26} already present ({human(size_of(target))})")
        return True

    print(f"...   {name:26} downloading from {hub_id}")
    try:
        if kind == "bi":
            from sentence_transformers import SentenceTransformer

            SentenceTransformer(hub_id).save(str(target))
        else:
            from sentence_transformers import CrossEncoder

            model = CrossEncoder(hub_id)
            model.save(str(target))
    except ImportError:
        raise SystemExit(
            "sentence-transformers is not installed.\n"
            "    pip install -r requirements.txt"
        )
    except Exception as exc:  # noqa: BLE001 — a download failure must read as advice
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
        print(f"FAIL  {name:26} {type(exc).__name__}: {exc}")
        print("      A partial download was removed. Re-run when you have a network,")
        print("      or copy models/ from a facilitator's USB stick.")
        return False

    print(f"OK    {name:26} saved ({human(size_of(target))})")
    return True


def check() -> int:
    """Load both models from disk and prove no network was needed."""
    import os

    # These make the underlying libraries refuse to reach the network at all, so a
    # model that quietly falls back to downloading fails loudly instead of passing.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    ok = True
    for name, _hub_id, kind in WANTED:
        target = MODELS / name
        if not target.exists():
            print(f"FAIL  {name:26} not found — run: python tools/fetch_models.py")
            ok = False
            continue
        try:
            if kind == "bi":
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer(str(target))
                dims = model.get_sentence_embedding_dimension()
                print(f"OK    {name:26} loaded, {dims} dimensions, no network used")
            else:
                from sentence_transformers import CrossEncoder

                CrossEncoder(str(target)).predict([["a question", "a passage"]])
                print(f"OK    {name:26} loaded and scored a pair, no network used")
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL  {name:26} {type(exc).__name__}: {exc}")
            ok = False
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch the local models for sessions 04-05")
    ap.add_argument("--check", action="store_true", help="verify both load, offline")
    ap.add_argument("--force", action="store_true", help="re-download even if present")
    args = ap.parse_args()

    if args.check:
        return check()

    MODELS.mkdir(exist_ok=True)
    results = [fetch(n, h, k, args.force) for n, h, k in WANTED]
    print()
    if all(results):
        print(f"Both models in {MODELS.relative_to(ROOT)}/ — total {human(size_of(MODELS))}.")
        print("Nothing here leaves the machine from now on. Verify with --check.")
        return 0
    print("Something above failed. The sessions cannot run until both are present.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
