"""Sprint26 Q3 · notebook generation.

The .py labs under sessions/ are the source of truth. Notebooks are a build
artifact and are gitignored.

WHY: .ipynb is JSON carrying cell outputs and execution counts. Committed, it
diffs badly and merges worse — which would wreck the fix-forward rule the moment
a bug in Session 02 has to be propagated through eight later branches.

Usage:
    pip install jupytext
    python tools/build_notebooks.py            # all sessions
    python tools/build_notebooks.py s01        # one session
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SESSIONS = ROOT / "sessions"
OUT = ROOT / "notebooks"

# Prepended to every generated notebook so it runs in Colab, where there is no
# clone and no working directory. Kept here rather than in the lab source: it is
# a delivery concern, not part of the teaching.
COLAB_BOOTSTRAP = '''# %% [markdown]
# ### Colab setup
# Skip this cell if you are running the lab from a local clone.

# %%
import os, sys
if "google.colab" in sys.modules and not os.path.exists("q3-ai"):
    BRANCH = "{branch}"
    !git clone --quiet --branch {{BRANCH}} https://github.com/developers-mania/q3-ai.git q3-ai
    %cd q3-ai
    !pip install --quiet -r requirements.txt
'''


def build(lab: Path, branch: str) -> Path:
    OUT.mkdir(exist_ok=True)
    staged = OUT / f"{lab.parent.name}_source.py"
    staged.write_text(COLAB_BOOTSTRAP.format(branch=branch) + "\n" + lab.read_text())

    target = OUT / f"{lab.parent.name}.ipynb"
    try:
        subprocess.run(
            ["jupytext", "--to", "notebook", "--output", str(target), str(staged)],
            check=True,
        )
    except FileNotFoundError:
        # A missing build tool should read as an instruction, not a traceback.
        raise SystemExit(
            "jupytext not found. Install the facilitator tooling:\n"
            "    pip install -r requirements-dev.txt"
        ) from None
    finally:
        staged.unlink(missing_ok=True)
    return target


def main(argv: list[str]) -> int:
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True, cwd=ROOT,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        branch = "main"

    wanted = argv[1:] or None
    labs = sorted(SESSIONS.glob("*/lab.py"))
    if wanted:
        labs = [p for p in labs if p.parent.name in wanted]
    if not labs:
        print("No labs found.")
        return 1

    for lab in labs:
        print(f"{lab.relative_to(ROOT)} -> {build(lab, branch).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
