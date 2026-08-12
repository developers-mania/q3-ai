"""Sprint26 Q3 · setup check.

Implements the four checks in the Session 01 Content Pack. Prints one line per
check so a participant can see at a glance what is wrong, rather than reading a
traceback. Exits non-zero if anything failed.

Session 01 needs no API key, no account and no network — so nothing here looks
for credentials. Sessions that need inference will extend this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"


def _line(ok: bool, name: str, detail: str) -> bool:
    print(f"{'OK  ' if ok else 'FAIL'}  {name:24} {detail}")
    return ok


def main() -> int:
    results = []

    # 1 · Python version
    v = sys.version_info
    results.append(
        _line(v >= (3, 10), "Python version", f"{v.major}.{v.minor}.{v.micro} (need 3.10+)")
    )

    # 2 · Dependencies. Imported here rather than at module top so that a missing
    #     package reports as a failed check instead of an ImportError on line 1.
    try:
        import sklearn  # noqa: F401
        import yaml  # noqa: F401

        results.append(_line(True, "Dependencies", "scikit-learn and PyYAML importable"))
    except ImportError as exc:
        results.append(_line(False, "Dependencies", f"{exc} — run: pip install -r requirements.txt"))

    # 3 · Corpus present and non-empty
    texts = sorted(CORPUS.glob("*.txt"))
    non_empty = [p for p in texts if p.stat().st_size > 0]
    results.append(
        _line(
            len(non_empty) >= 2,
            "Corpus present",
            f"{len(non_empty)} non-empty .txt in corpus/ (need 2 — see corpus/README.md)",
        )
    )

    # 4 · Evaluation set parses. Empty is fine on session-01-start; malformed is not.
    try:
        import yaml

        loaded = yaml.safe_load((ROOT / "eval" / "questions.yaml").read_text()) or []
        results.append(_line(True, "Evaluation set", f"parses, {len(loaded)} question(s)"))
    except Exception as exc:  # noqa: BLE001 — any parse failure is a failed check
        results.append(_line(False, "Evaluation set", f"will not parse: {exc}"))

    print()
    if all(results):
        print("Ready. The projector check is the facilitator's, not this script's.")
        return 0
    print("Something above needs fixing before the session.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
