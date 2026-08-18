"""Sprint26 Q3 · Session 02 · validation at the boundary, and the quarantine path.

Where this sits on the stack:
    Layer 1 — data infrastructure.

The rule to carry out of this session: validate at the boundary, quarantine on
failure, never coerce. A pipeline that silently repairs bad input is a pipeline
that will one day silently repair good input into something wrong — and by then
the repair will be load-bearing and nobody will remember it is there.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from src.passage import Passage

ROOT = Path(__file__).resolve().parent.parent
QUARANTINE = ROOT / "quarantine.jsonl"


def publish(candidates: list[dict], quarantine: Path = QUARANTINE) -> tuple[list[Passage], int]:
    """Validate every candidate. Accept or quarantine. Never coerce.

    Four options exist when a record fails and only one is correct:

        crash      one malformed record halts all ingestion. Tempting because it is
                   loud, disproportionate because one bad row should not stop the
                   corpus.
        skip       the record vanishes and nothing is written anywhere. The worst
                   option available: silent data loss is indistinguishable from
                   success, and you find out months later or never.
        coerce     force it into the expected shape and proceed. Worse than
                   skipping, because the bad data now looks like good data.
        quarantine reject to a dead-letter path with the reason attached, and keep
                   going. Nothing is lost, nothing is guessed, a human can look.
    """
    accepted: list[Passage] = []
    rejected = 0
    # Rewritten each run rather than appended to: a dead-letter file that only ever
    # grows stops being readable, and a quarantine nobody reads is a slightly more
    # expensive version of skipping silently.
    with quarantine.open("w", encoding="utf-8", newline="\n") as f:
        for raw in candidates:
            try:
                accepted.append(Passage(**raw))
            except ValidationError as exc:
                rejected += 1
                f.write(json.dumps({
                    "payload": {k: (v[:120] if isinstance(v, str) else v) for k, v in raw.items()},
                    "errors": [{"field": ".".join(str(x) for x in e["loc"]), "why": e["msg"]}
                               for e in exc.errors()],
                }, ensure_ascii=False) + "\n")
    return accepted, rejected
