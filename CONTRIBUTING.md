# Working in this repository

## Branches are teaching checkpoints

| Branch | Contains |
|---|---|
| `session-NN-start` | Everything completed through Session NN-1, working, plus Session NN's scaffolding and TODOs |
| `session-NN-baseline` | *(Session 01 only)* the branch the room creates and pushes live, as a demonstration of the commit workflow |
| `main` | Tracks the most recently completed session |

Checking out `session-04-start` puts you exactly where the room is at 2:00 PM on the
day of Session 04.

## Tags mark completed states

`solution/session-NN` points at the commit where Session NN's work was finished —
the parent of Session NN+1's scaffolding commit. Facilitators prep from the tag.

**These tags are movable.** When a bug in an early session is fixed weeks later, the
tag is re-pointed at the corrected commit. A tag here means "the completed state of
Session NN as it now stands", not "an immutable historical commit".

Tags are **annotated**, not lightweight, for two reasons: `git push --follow-tags`
ignores lightweight tags and would silently publish nothing, and an annotated tag
carries a message — which is where the reason for a re-point gets recorded.

### A solution/ tag may be a reconstruction, not a commit main passed through

`solution/session-01` and `solution/session-02` are **assembled** states: the current
`session-NN-start` branch, plus the files the room builds live, committed on top.
They are not ancestors of `main`.

That is deliberate. When `eval/questions.yaml` was written in August, the earlier
tags pointed at commits made before it existed, so anyone self-studying from them got
an empty evaluation set. Re-pointing them at a reconstruction is what makes the tag
mean what this file says it means — *the completed state of Session NN as it now
stands*. Making them ancestors of `main` instead would have meant merging Session
02's `src/ingest.py` into a `main` that has deliberately replaced it, which is a
conflict with no correct resolution.

Consequences worth knowing:

- `git log main` will not show these tags. `git checkout`, `git fetch --tags` and
  GitHub's tag list all work normally.
- `git diff session-NN-start solution/session-NN` is still exactly the session's
  lesson, which is the property that actually matters.
- Rebuilding one is cheap: branch from `session-NN-start`, `git checkout` the
  built-live files from the branch that holds them, commit, re-point the tag. Verify
  by re-running the evaluation set — a reconstruction that does not reproduce its own
  row in `eval/baseline.md` is wrong.

### Publishing a tag

`git push` does not push tags. Ever. It has to be explicit, and re-pointing one
needs `--force` because the tag already exists on the remote:

```bash
git tag -a -f solution/session-02 -m "Session 02 complete — <what changed, and why if re-pointed>"
git push -f origin solution/session-02
```

A `solution/` tag that was never pushed is the failure to watch for: every
participant instruction that says "check out `solution/session-NN`" fails for
everyone but you, and it fails at home where nobody can ask.

```bash
git ls-remote --tags origin      # what participants can actually see
```

### Re-pointing a tag people already have

`git fetch` will **not** update an existing local tag, and reports nothing when it
declines. Announce a re-point, and tell people to run:

```bash
git fetch --tags --force
```

Otherwise they keep the version they first cloned, bug included, and neither side
finds out.

## Fix forward, never rebase

Branches are published and cloned. Rebasing the chain breaks every clone.

When an error in Session 02 surfaces during Session 06: commit the fix on
`session-02-start`, then merge forward through each later branch in order, then
re-point the affected `solution/` tags. Tedious, non-destructive, and the only
option once people have the code.

## Comment conventions

The code is teaching material. Comments carry the content that would otherwise live
only in a facilitator's head — but they stay short, or the code stops being readable.

| Convention | Use |
|---|---|
| Module docstring | Session number, the plain-language question it answers, the layer of the stack |
| `# WHY:` | Design rationale — especially for choices that are deliberately bad |
| `# FLAW n:` | A named flaw from the running list, with the session that repairs it |
| `# DPA s.43:` | This line implements or reflects a specific statutory requirement |
| `# TODO(session-NN):` | A live-coding gap to be filled in the room |

One line each. Anything longer belongs in `sessions/sNN/README.md`.

The `# DPA s.NN` convention is the one worth being strict about. It is what keeps the
legal layer concrete rather than framing: a reader can trace a retention rule or a
notification deadline from the statute to the line of code that honours it.

## The evaluation set

`eval/questions.yaml` grows and never shrinks. Additions go through pull requests.
A question that has failed for nine weeks is the most informative item in the file —
it is not removed for being inconvenient.
