"""Sprint26 Q3 · Session 02 · Where The Data Comes From.

Question this answers:
    How does data get into a system reliably, and what breaks when it doesn't?

Where this sits on the stack:
    Layer 1 — data infrastructure.

Ingestion has four jobs and Session 01's pipeline did exactly one of them.

    Acquire    get the bytes from a known location, repeatably   a person clicked a link
    Verify     confirm they are what was expected, notice change  not done
    Structure  turn a document into parts, sections, identity     not done
    Publish    emit records downstream in a shape consumers rely on   not done

This module is the remaining three. Acquire becomes a manifest recording source,
publisher, version and content hash. Verify becomes a comparison against that hash.
Structure is src/parse.py. Publish is src/publish.py.

The failure this session is about produces NO SYMPTOM. When a source changes and
the index does not, the system keeps answering — fluently, confidently, in the same
tone it uses when it is right — from a version of the truth that no longer exists.
Nothing logs it. No test catches it. And the evaluation score does not move,
because the evaluation set was written against the old version too.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from src.chunk import chunk_flat, chunk_tree
from src.parse import parse_act, parse_strategy
from src.passage import passage_id
from src.publish import publish

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
MANIFEST = ROOT / "manifest.json"
PASSAGES = ROOT / "passages.jsonl"

CHUNK_SIZE = 500  # Session 01/02 only. Session 03 cuts on the tree — see src/chunk.py.

# WHY chunking stays naive this week: cutting on section boundaries is Session 03's
# job, and separating the two is what makes next week's improvement measurable in
# isolation. If both changed in the same week the movement in the score could not be
# attributed to either. It also produces the specific, visible failure that
# motivates Session 03 — a 500-character chunk straddling s.43(1) and s.43(2) can
# only be tagged with one of them.

PARSERS = {"dpa-2019.txt": (parse_act, "DPA"), "ai-strategy-2025.txt": (parse_strategy, "AIS")}


def fingerprint(path: Path) -> str:
    """Content hash. Same bytes in, same hash out, always."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict:
    if not MANIFEST.exists():
        raise SystemExit(
            f"No {MANIFEST.name}. The verification step cannot run without its "
            "reference,\nand proceeding would mean ingesting unverified sources "
            "while appearing to\nhave verified them. See sessions/s02/README.md."
        )
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def verify() -> list[str]:
    """Names of sources whose content no longer matches the manifest."""
    manifest = load_manifest()
    drifted = []
    for name, record in sorted(manifest["sources"].items()):
        path = CORPUS / name
        if not path.exists():
            drifted.append(f"{name} (MISSING)")
            continue
        if fingerprint(path) != record["sha256"]:
            drifted.append(name)
    return drifted


def stamp() -> None:
    """Write current hashes into the manifest. For a DELIBERATE corpus change only."""
    manifest = load_manifest()
    for name, record in manifest["sources"].items():
        record["sha256"] = fingerprint(CORPUS / name)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")
    print(f"Stamped {len(manifest['sources'])} source(s) into {MANIFEST.name}.")
    print("Record the reason in docs/decisions.md. Scores from before the change")
    print("are not comparable to scores after it.")


def build_candidates(overlap: int = 100, redact_fn=None) -> list[dict]:
    """Cut each source on its own boundaries, and give every passage its citation.

    Session 02 cut every 500 characters and tagged each chunk with whichever
    subsection it happened to START in. Session 03 cuts where the document says to
    cut, so the citation describes the whole chunk rather than its first line.
    """
    manifest = load_manifest()
    candidates: list[dict] = []
    for name, record in sorted(manifest["sources"].items()):
        parser, prefix = PARSERS[name]
        text = (CORPUS / name).read_text(encoding="utf-8")
        root, cleaned = parser(text, prefix)
        by_citation = {n.citation: n for n in root.walk() if n.citation}
        pieces = chunk_tree(root, cleaned, overlap=overlap)
        for piece in pieces:
            cite = piece["citation"]
            node = by_citation.get(cite)
            # WHY redaction is applied HERE and not to `cleaned` before chunking:
            # every node offset from src/parse.py indexes into `cleaned`, and a
            # substitution changes the text LENGTH — "[REDACTED_EMAIL]" is 16
            # characters where "info@kenyalaw.org" was 17. Redacting first shifts
            # every offset after the first hit, so the chunker cuts in the wrong
            # places and passages get citations belonging to their neighbours. It
            # cost exactly one evaluation question and looked like a redaction
            # side-effect rather than the offset bug it was.
            #
            # This still satisfies s.41's timing requirement: redaction runs in the
            # ingestion path, before anything reaches the index. A filter applied to
            # retrieval RESULTS would not — the index would still hold the
            # identifiers, and the index is the copy that persists.
            if redact_fn is not None:
                piece["text"], _ = redact_fn(piece["text"])
            if not piece["text"].strip():
                continue
            candidates.append({
                "passage_id": passage_id(name, cite, piece["offset"], piece["text"]),
                "source": name,
                "source_version": record["version"],
                "part": _ancestor_number(root, node, "part"),
                "section": node.number if node is not None and node.kind == "section"
                           else _ancestor_number(root, node, "section"),
                "subsection": node.number if node is not None and node.kind == "subsection" else None,
                "citation": cite,
                "offset": piece["offset"],
                "text": piece["text"],
            })
    return candidates


def _ancestor_number(root, node, kind: str) -> str | None:
    """Walk down from root to find the `kind` ancestor of `node`."""
    if node is None:
        return None

    def search(current, trail):
        if current is node:
            return trail
        for child in current.children:
            found = search(child, trail + [current])
            if found is not None:
                return found
        return None

    trail = search(root, [])
    if trail is None:
        return None
    for ancestor in reversed(trail):
        if ancestor.kind == kind:
            return ancestor.number
    return None


def write_passages(passages) -> None:
    """Idempotent write: same input, byte-identical output."""
    with PASSAGES.open("w", encoding="utf-8", newline="\n") as f:
        for p in passages:
            f.write(json.dumps(p.model_dump(), ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Session 02 · ingestion with provenance")
    ap.add_argument("--verify", action="store_true", help="check sources against the manifest")
    ap.add_argument("--stamp", action="store_true", help="rewrite manifest hashes (deliberate change only)")
    ap.add_argument("--overlap", type=int, default=100, metavar="N",
                    help="characters repeated between adjacent chunks (session 03)")
    ap.add_argument("--redact", action="store_true", help="run the sanitiser before indexing (session 03)")
    args = ap.parse_args()

    if args.stamp:
        stamp()
        return 0

    drifted = verify()
    if drifted:
        print("DRIFTED — the source no longer matches the manifest:")
        for name in drifted:
            print(f"  {name}")
        print("\nThe index would have been built from bytes nobody recorded. If the")
        print("change was intended, run:  python -m src.ingest --stamp")
        return 1
    print(f"OK        all sources match {MANIFEST.name}")
    if args.verify:
        return 0

    redact_fn = None
    if args.redact:
        from src.redact import redact
        redact_fn = redact
    candidates = build_candidates(overlap=args.overlap, redact_fn=redact_fn)
    accepted, rejected = publish(candidates)
    write_passages(accepted)
    print(f"accepted  {len(accepted):,} passages")
    print(f"quarantined {rejected:,}" + ("  <- read quarantine.jsonl" if rejected else ""))
    cited = sum(1 for p in accepted if p.section is not None)
    print(f"of those, {cited:,} carry a section number ({cited / len(accepted):.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
