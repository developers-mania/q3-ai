"""Sprint26 Q3 · Session 05 · the graph already in the Act.

Where this sits on the stack:
    Layer 2 — context and memory.

One more source of context, and it needs no new data. The Act refers to itself
constantly:

    s.48   "...subject to section 49, a data controller may transfer..."
    s.31   "...an assessment under subsection (1) shall be submitted..."
    s.63   "...in accordance with Part VIII..."

Those references are edges. Section 48 points at section 49, so if a question is
answered from s.48 and s.48 says "subject to section 49", then s.49 probably matters
to the answer — and a retriever scoring passages independently will never notice.

WHY this is the honest version of a knowledge graph:
    Most demonstrations of graph-augmented retrieval invent an entity graph -
    customers, orders, products - that has to be built and maintained separately
    from the documents, and kept in step with them forever. The Act's
    cross-references are already written in the text. Extracting them is a parsing
    job, not a data-modelling project, and following them adds context that is
    genuinely relevant rather than merely connected.
"""

from __future__ import annotations

import re

# "section 49", "sections 48 and 49", "section 43(3)". Deliberately explicit:
# an earlier draft matched every node label against every chunk by substring, which
# is quadratic and false-positives heavily on short identifiers - "section 2" would
# match inside "section 25".
SECTION_REF = re.compile(r"\bsections?\s+(\d{1,3})(?:\s*\(\d+\))?", re.I)


def section_of(citation: str) -> str | None:
    """'DPA s.43(1)(a)' -> '43'. None for anything without a section."""
    if " s." not in citation:
        return None
    return citation.split(" s.")[1].split("(")[0].strip() or None


def build_graph(passages: list[dict]):
    """A directed edge from each section to every section it mentions."""
    import networkx as nx

    graph = nx.DiGraph()
    for passage in passages:
        source = passage.get("section") or section_of(passage["citation"])
        if not source:
            continue
        graph.add_node(source)
        for target in SECTION_REF.findall(passage["text"]):
            if target != source:
                graph.add_edge(source, target)
    return graph


def expand(citation: str, graph, passages: list[dict], hops: int = 1) -> list[dict]:
    """Passages from the sections this one points at."""
    source = section_of(citation)
    if not source or source not in graph:
        return []
    reachable: set[str] = set()
    frontier = {source}
    for _ in range(hops):
        nxt: set[str] = set()
        for node in frontier:
            nxt |= set(graph.successors(node))
        nxt -= reachable | {source}
        reachable |= nxt
        frontier = nxt
    return [p for p in passages
            if (p.get("section") or section_of(p["citation"])) in reachable]


def has_reference(passage: dict) -> bool:
    """Does this passage actually cite another section?

    The rule that makes expansion worth having. Expanding EVERY result adds context
    to passages that never asked for any, and Session 04 established that irrelevant
    context degrades results. Expanding only when the retrieved passage genuinely
    contains a cross-reference is one line of code and a much better rule.
    """
    own = passage.get("section") or section_of(passage["citation"])
    return any(t != own for t in SECTION_REF.findall(passage["text"]))
