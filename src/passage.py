"""Sprint26 Q3 · Session 02 · the passage record.

Where this sits on the stack:
    Layer 1 — data infrastructure. This is the contract at the pipeline boundary.

Anything reaching the index from now on is a Passage or it does not reach the index.
"""

from __future__ import annotations

import hashlib

from pydantic import BaseModel, Field, field_validator


class Passage(BaseModel):
    """One indexable unit, and everything needed to cite it.

    Note what this model makes structurally impossible: a passage with no source, a
    passage with no citation, and a passage of pure whitespace. Session 01's
    pipeline produced all three without complaint, and they are still sitting in
    that index.
    """

    passage_id: str
    source: str  # "dpa-2019.txt"
    source_version: str  # "as revised 31 December 2022"
    part: str | None = None  # "IV"
    section: str | None = None  # "43"
    subsection: str | None = None  # "1"
    citation: str  # "DPA s.43(1)"
    offset: int = Field(ge=0)
    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("passage text is empty after stripping")
        return v

    @field_validator("citation")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("passage has no citation")
        return v


def passage_id(source: str, citation: str, offset: int, text: str) -> str:
    """Stable identity: the same content at the same position yields the same id.

    WHY not uuid4(): a fresh identifier every run doubles the corpus on a re-run,
    retrieval returns duplicates, and the evaluation score moves for a reason that
    has nothing to do with quality. Retries are inevitable — a network fails
    mid-run, a process is killed, somebody runs the command twice because they were
    not sure the first one worked.

    WHY citation rather than section alone: citation already encodes part, section
    and subsection, and it is the stabler key. Offset is included because two
    passages in the same subsection must not collapse into one — but note the cost,
    and it is a real one: inserting a paragraph near the top of the Act shifts every
    offset below it and re-identifies the whole corpus. An incremental index would
    rewrite everything. That trade is the design decision, and knowing which cost
    you are paying is the point.
    """
    key = f"{source}:{citation}:{offset}:{text}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
