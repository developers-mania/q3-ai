"""Sprint26 Q3 · Session 02 · Where The Data Comes From.

Question this answers:
    How does data get into a system reliably, and what breaks when it doesn't?

Where this sits on the stack:
    Layer 1 — data infrastructure.

Session 01 loaded the Act as one string. Every piece of structure it contained —
parts, sections, subsections, paragraphs — was still present as characters and
entirely absent as structure. This module recovers it.

WHY that matters more than it sounds: citation accuracy cannot be computed at all
without this. "Did the retrieved passage carry the section the answer actually came
from" is not a question a flat string can answer, and it is the metric that will
justify Session 03.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"

# --------------------------------------------------------------------------
# Page furniture
# --------------------------------------------------------------------------
# WHY strip before parsing: the running header sits INSIDE section text — it lands
# between s.38(1)(b) and s.38(6) — so a parser that keeps it will attach a page
# banner to a subsection and a chunker will index it as content.
RUNNING_HEADER = re.compile(r"^\s*\x0c?\s*Data Protection Act \(Cap\. 411C\)\s+Kenya\s*$")
PAGE_NUMBER = re.compile(r"^\s*\x0c?\s*\d{1,3}\s*$")

# --------------------------------------------------------------------------
# Structure. Every one of these is anchored with ^\s* rather than ^.
# --------------------------------------------------------------------------
# WHY not ^: the Act's Part headings are CENTRED, with indentation running from 0
# to 44 spaces depending on the heading's length. The Content Pack's draft regex
# was ^PART\s+([IVXL]+)\s*[—-] — uppercase, em-dash, column zero — and it matches
# nothing at all in this text, which reads "    Part IV - PRINCIPLES...".
PART_RE = re.compile(r"^\s*Part\s+([IVXL]+)\s*-\s*(.+?)\s*$")
SECTION_RE = re.compile(r"^\s*(\d{1,3})\.\s+(.+?)\s*$")
SUBSEC_RE = re.compile(r"^\s*\((\d{1,2})\)\s+(.+?)\s*$")
PARA_RE = re.compile(r"^\s*\(([a-z]{1,2})\)\s+(.+?)\s*$")
SCHEDULE_RE = re.compile(r"^\s*(FIRST|SECOND|THIRD)\s+SCHEDULE\b.*$")

# The Strategy has no scheme comparable to the Act's. See parse_strategy().
AIS_HEADING_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\.?\s+([A-Z][^.]{3,70})\s*$")


@dataclass
class Node:
    """One addressable unit of a document."""

    kind: str  # "part" | "section" | "subsection" | "paragraph" | "schedule"
    number: str  # "IV", "43", "1", "a"
    heading: str = ""
    citation: str = ""
    start: int = 0  # character offset into the cleaned document text
    end: int = 0
    children: list["Node"] = field(default_factory=list)

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()


def citation(prefix: str, section=None, subsection=None, paragraph=None, part=None) -> str:
    """Produce the reference a lawyer would recognise: DPA s.43(1)(a).

    DPA s.43 · DPA s.43(1) · DPA s.43(1)(a) · DPA Part IV
    """
    if section is None:
        return f"{prefix} Part {part}" if part else prefix
    ref = f"{prefix} s.{section}"
    if subsection:
        ref += f"({subsection})"
    if paragraph:
        ref += f"({paragraph})"
    return ref


def strip_furniture(text: str) -> tuple[str, int]:
    """Remove running headers and page numbers. Returns (text, lines_removed)."""
    kept, dropped = [], 0
    for line in text.split("\n"):
        if RUNNING_HEADER.match(line) or PAGE_NUMBER.match(line):
            dropped += 1
            continue
        kept.append(line.replace("\x0c", ""))
    return "\n".join(kept), dropped


def find_body_start(lines: list[str]) -> int:
    """First line of the Act proper, skipping the cover and the contents page.

    WHY this is needed: every section number in the Act appears TWICE — once in the
    contents with dot leaders, once in the body. A parser that does not skip the
    contents finds 150 section markers for 75 sections, and the first "43." it hits
    is a table-of-contents entry with no text under it.

    Dot leaders alone are not a safe test: the First Schedule's oath template is
    full of them ("I, ......., make oath"). The contents block is bounded instead —
    it ends at the first Part heading that is NOT a contents entry.
    """
    for i, line in enumerate(lines):
        if PART_RE.match(line) and "...." not in line:
            return i
    return 0


def parse_act(text: str, prefix: str = "DPA") -> tuple[Node, str]:
    """Parse the Act into Part > Section > Subsection > Paragraph.

    Returns (root, cleaned_text). Offsets on every node index into cleaned_text,
    so a chunker can map any character position back to a citation.
    """
    cleaned, _ = strip_furniture(text)
    lines = cleaned.split("\n")
    body_start = find_body_start(lines)

    root = Node(kind="document", number=prefix, heading="Kenya Data Protection Act")
    part = section = subsection = None
    offset = 0
    # Character offset of the start of each line, so nodes can carry real spans.
    starts = []
    for line in lines:
        starts.append(offset)
        offset += len(line) + 1

    def close(node: Node | None, end: int) -> None:
        if node is not None and node.end == 0:
            node.end = end

    for i in range(body_start, len(lines)):
        line = lines[i]
        pos = starts[i]
        if not line.strip():
            continue

        if m := SCHEDULE_RE.match(line):
            close(subsection, pos), close(section, pos), close(part, pos)
            part = Node("schedule", m.group(1).title(), line.strip(), f"{prefix} {m.group(1).title()} Schedule", pos)
            root.children.append(part)
            section = subsection = None
            continue

        if m := PART_RE.match(line):
            close(subsection, pos), close(section, pos), close(part, pos)
            part = Node("part", m.group(1), m.group(2), citation(prefix, part=m.group(1)), pos)
            root.children.append(part)
            section = subsection = None
            continue

        if m := SECTION_RE.match(line):
            close(subsection, pos), close(section, pos)
            section = Node("section", m.group(1), m.group(2), citation(prefix, m.group(1)), pos)
            (part.children if part else root.children).append(section)
            subsection = None
            continue

        if section is not None and (m := SUBSEC_RE.match(line)):
            close(subsection, pos)
            subsection = Node(
                "subsection", m.group(1), "",
                citation(prefix, section.number, m.group(1)), pos,
            )
            section.children.append(subsection)
            continue

        # A paragraph belongs to the subsection above it, or to the section when a
        # section has paragraphs directly. DPA s.43: (1)(a) and (1)(b) are the
        # 72-hour and communication limbs.
        if (m := PARA_RE.match(line)) and (subsection is not None or section is not None):
            parent = subsection or section
            para = Node(
                "paragraph", m.group(1), "",
                citation(prefix, section.number,
                         subsection.number if subsection else None, m.group(1)),
                pos,
            )
            parent.children.append(para)
            continue

    # Ends, in one pass: a node runs until the next structural marker at any depth.
    # Approximate by design — Session 02 keeps chunking naive, and the only thing
    # that consumes a span is the citation lookup below, which uses starts.
    nodes = sorted((n for n in root.walk() if n.kind != "document"), key=lambda n: n.start)
    for a, b in zip(nodes, nodes[1:]):
        a.end = b.start
    if nodes:
        nodes[-1].end = len(cleaned)
    return root, cleaned


def anchors(root: Node) -> list[tuple[int, str]]:
    """Flat (offset, citation) list, sorted. The deepest marker at each position wins."""
    seen: dict[int, str] = {}
    for node in root.walk():
        if node.kind == "document" or not node.citation:
            continue
        # A subsection and its paragraph can open at different lines; later (deeper)
        # markers at a greater offset naturally supersede earlier ones.
        seen[node.start] = node.citation
    return sorted(seen.items())


def citation_at(offset: int, anchor_list: list[tuple[int, str]]) -> str | None:
    """The citation in force at a character offset.

    WHY the most recent marker rather than a containing span: this is what makes
    Session 02's central failure visible. A fixed-width chunk that straddles a
    section boundary starts inside one section and ends inside the next, and gets
    tagged with only the first. Citation accuracy measures exactly that damage,
    and Session 03 repairs it by cutting on the boundary instead of across it.
    """
    import bisect

    i = bisect.bisect_right(anchor_list, (offset, chr(0x10FFFF)))
    return anchor_list[i - 1][1] if i else None


def parse_strategy(text: str, prefix: str = "AIS") -> tuple[Node, str]:
    """The Strategy, which does NOT have a scheme comparable to the Act's.

    This function is deliberately thin, and saying why is part of the session.

    The Act is a statute: numbered sections, numbered subsections, a stable
    citation form that a lawyer would recognise. The Strategy is a policy paper.
    Its numbered headings live in a contents block that the two-column extraction
    interleaved, its body headings are inconsistently numbered, and several of its
    "sections" are figures and tables. Building a Part/Section/Subsection tree over
    it would produce citations that look precise and are not.

    So the Strategy gets a document-level citation and no false precision. That is
    a finding, not a shortcut: structure-aware handling only works on documents that
    have structure, and knowing which kind you are holding is Layer 1 work. Session
    03 makes the same call again when it chooses a chunking strategy per document.
    """
    cleaned, _ = strip_furniture(text)
    root = Node(kind="document", number=prefix,
                heading="Kenya National AI Strategy 2025-2030", citation=prefix,
                start=0, end=len(cleaned))
    return root, cleaned
