"""Sprint26 Q3 · Session 03 · what has to come out.

Where this sits on the stack:
    Layer 1 — data infrastructure, in the ingestion path.

DPA s.41: data protection by design and by default, naming pseudonymisation
explicitly. "By design" is a TIMING requirement, and that is why this module runs
before indexing rather than filtering retrieval results. A filter on results still
means the index holds the identifiers, and the index is the copy that persists —
it outlives its source, is queried by people who never saw the original, and may be
sent to a model provider outside Kenya.

DPA s.25: the principles. Purpose limitation and storage limitation are the two
teams overlook. An index is not a view of the source; it is a copy with its own
lifecycle, its own access pattern and its own retention. Deleting a record from a
database does not delete it from the index built last month.

A redaction rule has TWO error rates and almost every implementation measures only
one:

    recall     of the personal data present, how much was removed?
               measured against a fixture with known identifiers planted in it
    precision  of what was removed, how much was actually personal data?
               measured against a corpus known to contain none — every hit is,
               by construction, a false positive

This corpus gives an unusually clean precision measurement, and the result is the
counter-intuitive finding of the quarter: here the dangerous failure is not leaking
personal data. It is destroying the statute.
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------------
# Well-shaped patterns. Specific enough that accidental matches are rare.
# --------------------------------------------------------------------------
PATTERNS: dict[str, tuple[str, str]] = {
    "PHONE_KE": (r"(?:\+254|0)[17]\d{8}\b", "[REDACTED_PHONE]"),
    "EMAIL": (r"[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]"),
    "ID_KE": (r"(?i)\b(?:national\s+id|id\s+(?:no|number))\D{0,10}(\d{7,8})\b", "[REDACTED_ID]"),
}

# --------------------------------------------------------------------------
# The rule that destroys this corpus.
# --------------------------------------------------------------------------
# A name has no fixed shape. There is no regular expression for "this string is a
# person", and capitalisation is not enough — the Act capitalises Data Commissioner,
# Cabinet Secretary, Data Protection and First Schedule. Two capitalised words is
# the naive reach for it, and on this corpus it fires 201 times on the Act alone,
# 80 of them on "Data Commissioner" — a term most of the evaluation set depends on.
#
# Every one of those hits is a false positive: the Act names an OFFICE, not a person.
NAME_NAIVE = (r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", "[REDACTED_NAME]")

# The narrowed version: require the context a person is actually introduced in.
#
# WHY the case-insensitive flag is NOT used here, having been tried first: written
# as r"(?i)\b(?:complainant|mr|dr)\.?,?\s+([A-Z][a-z]+...)", the (?i) applies to the
# WHOLE pattern, so [A-Z][a-z]+ silently matches lowercase too. On this corpus that
# turned the phrase "applicant is false or" into a person named "is false or". An
# inline flag quietly widening the half of a pattern you meant to keep strict is an
# easy thing to ship and a hard thing to see — and the only reason it surfaced here
# is that the false-positive count was being read rather than assumed.
NAME_NARROW = (
    r"\b(?:[Cc]omplainant|[Aa]pplicant|[Pp]etitioner|Mr|Mrs|Ms|Dr)\.?,?\s+"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})",
    "[REDACTED_NAME]",
)


def redact(text: str, patterns: dict[str, tuple[str, str]] | None = None) -> tuple[str, dict[str, int]]:
    """Return sanitised text and a count of hits per pattern.

    Note re.subn rather than re.sub. The count is not a nicety — measuring the
    false positive rate depends on knowing how many times each pattern fired.
    """
    counts: dict[str, int] = {}
    for name, (pattern, replacement) in (patterns or PATTERNS).items():
        text, n = re.subn(pattern, replacement, text)
        counts[name] = n
    return text, counts


def false_positive_rate(clean_corpus: str, pattern: str) -> tuple[float, int]:
    """Precision, measured against a corpus known to contain no personal data.

    The Act and the Strategy are public documents. The Data Commissioner is named by
    office, not by name. There are no phone numbers, no email addresses of data
    subjects and no identity numbers.

    Therefore every hit on this corpus is a false positive BY CONSTRUCTION, and the
    rate is 1.0 whenever the pattern fires at all. That is a stronger statement than
    it looks: it means the count IS the damage, and the damage is measurable exactly.
    """
    hits = re.findall(pattern, clean_corpus)
    return (1.0 if hits else 0.0), len(hits)


def report(text: str, label: str, patterns: dict[str, tuple[str, str]] | None = None) -> dict[str, int]:
    """Print per-pattern hit counts. Used by the lab and by --redact runs."""
    _, counts = redact(text, patterns)
    print(f"{label}:")
    for name, n in counts.items():
        print(f"    {name:12} {n:5}")
    return counts
