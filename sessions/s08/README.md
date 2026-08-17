# Session 08 · (open slot)

> **The question this session answers**
> *Chosen in-quarter.*

| | |
|---|---|
| **Date** | Wednesday 23 September 2026 · 2:00–4:00 PM |
| **Module** | FLEX / deep dive |
| **Start branch** | `session-08-start` (= `solution/session-07` + scaffolding) |
| **Open slot** | Topic decided at **Session 05** |

---

## ⏳ Neither the topic nor the codelab is decided yet

This is the most open of the three open slots — **the question itself is chosen
in-quarter**, not only the technology.

> A decision without a date is not a decision. The decision point is **Session 05**,
> it has a named owner, and if it passes without a choice the published default
> stands and is announced as the decision.

---

## ⚠️ A divergence to resolve at Session 05

The source documents disagree about this session, and the disagreement should be
settled explicitly rather than discovered in September:

| Source | What it says |
|---|---|
| **Concept Note** §5, §10 | Session 08 is an **open slot**, decided at Session 5 |
| **Module Breakdown** | Session 08 is *"Local Model Inference & Edge AI (or Real-Time Audio)"* |
| **Session 01 Study Guide** §1.2 | *"Session 8 on local inference exists partly because of [s.50]"* — treats it as decided |

The Concept Note is the governing document, so the slot is **open**. But the leading
candidate has already been named twice in participant-facing material, and one of
those framings gives it a legal rationale.

**Resolve this at Session 05 and record the reason in
[`docs/decisions.md`](../../docs/decisions.md).**

## The leading candidate, and why

**Local model inference and edge AI.** The argument for it is not novelty:

> **DPA s.50** permits the Cabinet Secretary to require that certain processing happen
> only through a server or data centre **located in Kenya.**

Every session from 04 onward has quietly raised the same question — where are the
embeddings computed, whose servers hold the vectors, does the text leave the country
on every request. A local inference session converts that thread from a recurring
caveat into an engineering deliverable: a pipeline with **zero third-party data
leaks**, completable on a mid-range laptop with no network and no key.

It also serves the quarter's cost commitment. **Local models are the floor** — every
codelab must be completable, at reduced quality, without a shared inference budget.
This session is where that floor is built rather than assumed.

## Prepare for it

Nothing yet. Bring the decision to Session 05 — this slot exists to serve what the
room actually needs by late September, and the strongest input is what participants
have found hardest in Sessions 04–07.

← [Session 07](../s07/README.md) · [Repository guide](../../docs/repository-guide.md)
