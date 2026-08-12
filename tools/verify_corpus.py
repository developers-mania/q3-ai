"""Sprint26 Q3 · corpus verification.

Pins the corpus by checksum so that "the index went stale" and "somebody replaced
a source file" are distinguishable failures. First run writes the manifest;
later runs check against it.

WHY this exists at Session 01 rather than Session 02: every score recorded this
quarter is only comparable to the baseline if the corpus underneath it is the same
corpus. A silently swapped source file invalidates ten weeks of measurement and
leaves no trace.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
MANIFEST = CORPUS / "MANIFEST.sha256"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    files = sorted(CORPUS.glob("*.txt"))
    if not files:
        print(f"No .txt files in {CORPUS}. See corpus/README.md.")
        return 1

    current = {p.name: digest(p) for p in files}

    if not MANIFEST.exists():
        # newline="\n" for the same reason the corpus is written with it: a manifest
        # that differs by platform is a manifest that reports false CHANGED lines.
        MANIFEST.write_text(
            "".join(f"{h}  {n}\n" for n, h in sorted(current.items())), newline="\n"
        )
        print(f"Wrote {MANIFEST.relative_to(ROOT)} for {len(current)} file(s):")
        for name, h in sorted(current.items()):
            print(f"  {h[:16]}…  {name}")
        print("\nCommit this manifest. It pins the corpus for the whole quarter.")
        return 0

    recorded = {}
    for line in MANIFEST.read_text().splitlines():
        if line.strip():
            h, name = line.split(maxsplit=1)
            recorded[name.strip()] = h

    ok = True
    for name in sorted(set(recorded) | set(current)):
        if name not in current:
            print(f"MISSING   {name}")
            ok = False
        elif name not in recorded:
            print(f"UNTRACKED {name} — new file, not in the manifest")
            ok = False
        elif recorded[name] != current[name]:
            print(f"CHANGED   {name} — content differs from the pinned revision")
            ok = False
        else:
            print(f"OK        {name}")

    if not ok:
        print("\nIf a change was intentional, delete the manifest, re-run, and record")
        print("the reason in docs/decisions.md. Scores from before the change are")
        print("not comparable to scores after it.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
