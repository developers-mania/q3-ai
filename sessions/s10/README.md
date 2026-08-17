# Session 10 · The Standard We Set

> **The question this session answers**
> *What do we, as a group, hold ourselves to when we build this way?*

| | |
|---|---|
| **Date** | Wednesday 7 October 2026 · 2:00–4:00 PM |
| **Module** | Finale — Demo Day and Standards Workshop |
| **Stack layer** | 5 — safety and evaluation |
| **Start branch** | `session-10-start` (= `solution/session-09`) |
| **Output** | Peer engineering reviews of tagged releases; the Q3 Intelligence Baseline committed |

---

## This session has no codelab, and that is the design

Session 10 is a **workshop, not a build.** Two things happen:

1. **Peer engineering review** of tagged releases. Participants review each other's
   work against the standard the group has been assembling all quarter.
2. **The standard is adopted by vote** and committed.

---

## The standard is already being written

This is the part that makes the session work, and it depends on nine weeks of small
deposits rather than twenty minutes of cold authoring.

**Every session names the standard it earned, in one line, at the time.** They
accumulate in [`docs/standard.md`](../../docs/standard.md) — ten items, one per
session, each proposed in the session that earned it and amendable by the room.

The first three, as they stand:

| # | Session | The standard |
|---|---|---|
| 1 | 01 | *We measure before we improve. No claim about system quality is made without a score against a fixed, versioned set of questions with known answers.* |
| 2 | 02 | *Data carries its provenance. Every record knows where it came from, which version it is, and when it was retrieved — and any passage that cannot cite its own source does not reach an index.* |
| 3 | 03 | *A safeguard is measured in both directions. Any rule that removes data reports what it removed and what it removed wrongly, and no redaction step ships without a false positive rate.* |

> If `docs/standard.md` has fewer items than there have been sessions, that is the
> thing to fix **before** October — not during it. The workshop assembles a standard;
> it does not author one.

## The closing number

The quarter opened with a bad number nobody enjoyed looking at. It closes by
comparing October's score to **5 August's** — not to last week's, because the baseline
is never re-based.

> *"Retrieval accuracy moved from X% to Y% over ten weeks"* is a statement about
> outcomes that no attendance register can produce. Every participant should be able
> to name **which change moved it, and by how much.**

Bring the whole table from [`eval/baseline.md`](../../eval/baseline.md), including
the weeks the number went **down**. A change that improves retrieval on average can
lose questions that previously succeeded by luck rather than merit, and those weeks
teach more than the clean improvements do.

## What participants leave with

- A working intelligence pipeline built layer by layer, with a measured accuracy score
  they improved themselves.
- A tool interface built against a current open standard.
- An automated evaluation suite — the skill that separates people who ship AI features
  from people who demo them.
- A written engineering standard the group adopted by vote, carried forward beyond the
  quarter.

**No certificate of attendance.** Recognition, where offered, attaches to verifiable
artifacts — a working tool interface, an evaluation suite, tagged commits — rather
than to presence in a room.

← [Session 09](../s09/README.md) · [Repository guide](../../docs/repository-guide.md)
