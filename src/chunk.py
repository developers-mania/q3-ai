"""Sprint26 Q3 · Session 03 · Getting Data Ready.

Question this answers:
    What shape does data need to be in before a model can use it?

Where this sits on the stack:
    Layer 1 into Layer 2.

Session 01 cut the corpus every 500 characters, a number chosen for no reason at
all. Session 02 built a parser that knows where every subsection begins and ends,
and deliberately left the cutting alone. Today they meet.

The chunk is the smallest addressable unit in the whole system. Nothing smaller can
ever be returned, and every later stage — embedding, retrieval, re-ranking,
generation — operates on units whose boundaries were fixed here. A chunk cut through
the middle of an answer cannot be repaired by a better embedding model, a better
re-ranker or a better prompt. The information is not in there.

    Chunking is the one decision that later sophistication cannot compensate for.
"""

from __future__ import annotations

import re

from src.parse import Node

MAX_CHARS = 1200  # a CEILING, not a target — see below
MIN_CHARS = 80    # below this, merge with siblings under the same section

# WHY MAX_CHARS is a ceiling and not a target: in fixed-size chunking the size
# parameter governs every chunk, so raising it from 1,200 to 2,000 changes all of
# them. Here most subsections are naturally short and never approach it, so the
# parameter only governs the handful of oversized sections. That is a much smaller
# and more predictable effect, and it changes how you tune it.

SENTENCE_END = re.compile(r"(?<=[.;:])\s+")


def section_key(citation: str) -> str:
    """'DPA s.43(1)(a)' -> 'DPA s.43'. Two units may merge only if these match."""
    return citation.split("(")[0].strip()


def split_oversized(text: str, limit: int) -> list[str]:
    """Split within a unit that does not fit. Every piece keeps the citation.

    This is why structure-aware chunking is not simply "one chunk per section".
    Some sections run to pages — s.25, the eight data protection principles, is the
    obvious one. A chunk larger than what the model can be given is useless however
    clean its boundaries are.

    The rule that makes subdivision safe: the pieces INHERIT the citation. A section
    25 split into three produces three chunks all correctly cited DPA s.25. That is
    less precise than a subsection, and enormously better than three chunks cited to
    nothing — or worse, cited to whichever section happened to be nearest.
    """
    pieces, current = [], ""
    for sentence in SENTENCE_END.split(text):
        if current and len(current) + len(sentence) + 1 > limit:
            pieces.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip() if current else sentence
    if current.strip():
        pieces.append(current.strip())
    return pieces or [text.strip()]


def chunk_tree(root: Node, cleaned: str, max_chars: int = MAX_CHARS,
               min_chars: int = MIN_CHARS, overlap: int = 0) -> list[dict]:
    """Cut on the document's own boundaries rather than by the character.

    Session 02 gave every node a [start, end) span that partitions the document, so
    a node's own text is exactly its span. Emitting one chunk per node therefore
    cuts precisely where the Act says one idea ends and another begins.

    Three cases arise and only the third is difficult:

        fits comfortably   s.43(3), one sentence      emit as one chunk
        too small          a one-line definition      merge with siblings, NEVER
                                                      across sections
        too large          s.25, the eight principles subdivide, keeping the citation
    """
    nodes = sorted((n for n in root.walk() if n.kind != "document"), key=lambda n: n.start)
    if not nodes:
        return chunk_flat(cleaned, root.citation or root.number, max_chars, overlap)

    units: list[dict] = []

    # Front matter — the cover and contents, before the first structural marker.
    # It is real text and gets the document citation rather than being silently
    # dropped: an index that quietly loses content is the Session 02 lesson again.
    head = cleaned[: nodes[0].start]
    if head.strip():
        units.append({"citation": root.citation or root.number,
                      "text": head.strip(), "offset": 0})

    for node in nodes:
        text = cleaned[node.start:node.end]
        if not text.strip():
            continue
        units.append({"citation": node.citation, "text": text.strip(), "offset": node.start})

    merged: list[dict] = []
    for unit in units:
        prev = merged[-1] if merged else None
        can_merge = (
            prev is not None
            and len(prev["text"]) < min_chars
            and section_key(prev["citation"]) == section_key(unit["citation"])
            and len(prev["text"]) + len(unit["text"]) <= max_chars
        )
        # WHY never across sections: the merged chunk can carry only one citation,
        # so joining s.43(3) to s.44(1) would cite half its content wrongly — which
        # is the exact failure Session 02 measured and this session repairs.
        if can_merge:
            prev["text"] = f"{prev['text']}\n{unit['text']}"
        else:
            merged.append(dict(unit))

    chunks: list[dict] = []
    for unit in merged:
        if len(unit["text"]) <= max_chars:
            chunks.append(unit)
            continue
        for piece in split_oversized(unit["text"], max_chars):
            chunks.append({"citation": unit["citation"], "text": piece, "offset": unit["offset"]})

    return _apply_overlap(chunks, overlap)


def chunk_flat(text: str, citation: str, size: int = 500, overlap: int = 0) -> list[dict]:
    """Fixed-width cutting, for a document with no structure to be aware of.

    The AI Strategy gets this and the Act does not, and that is a decision rather
    than a fallback. Structure-aware chunking is rated best for legal texts and its
    only stated drawback is that it needs parsed structure. The Act has it; the
    Strategy genuinely does not. A corpus of support tickets or scraped pages would
    take this same treatment for the same reason.
    """
    step = max(1, size - overlap)
    return [{"citation": citation, "text": text[i:i + size].strip(), "offset": i}
            for i in range(0, len(text), step) if text[i:i + size].strip()]


def _apply_overlap(chunks: list[dict], overlap: int) -> list[dict]:
    """Repeat the tail of one chunk at the head of the next.

    WHY this is measured in the session rather than defaulted: overlap is insurance
    against a boundary falling in a bad place. Once cutting is semantic the
    boundaries fall where the document itself says one idea ends, so an answer
    straddling one is rare — and the cost does not fall with the benefit. A 20%
    overlap still inflates the corpus by 20% and still returns near-duplicates that
    crowd out genuinely different passages. The right answer here may well be zero,
    which would have been clearly wrong two weeks ago.
    """
    if overlap <= 0:
        return chunks
    out = []
    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        if i:
            text = chunks[i - 1]["text"][-overlap:] + " " + text
        out.append({**chunk, "text": text})
    return out
