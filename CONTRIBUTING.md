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
