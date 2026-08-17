# Session 07 · Letting Software Decide

> **The question this session answers**
> *How does software choose what to do next, and where does a human stay in the loop?*

| | |
|---|---|
| **Date** | Wednesday 16 September 2026 · 2:00–4:00 PM |
| **Module** | 3 · Protocols and Agentic Orchestration |
| **Stack layer** | 3 — orchestration and state |
| **Start branch** | `session-07-start` (= `solution/session-06` + **deliberately weakened** scaffolding) |
| **Repairs** | Nothing on the flaw list. Adds Layer 3 |

---

## ⏳ The codelab for this session is not published yet

**Published at:** with the Session 05 announcement.

---

## ⚠️ The starter branch for this session ships with planted weaknesses

**This is the one session where the start branch is deliberately unsafe**, and
participants are told so in advance.

`session-07-start` ships with an over-permissive tool interface and a resource that
can be manipulated through injected instructions. **The room finds them.**

The reasoning: security formally sits at Session 09, but autonomy starts here. Two
weeks of building agents with no defensive frame is a known risk, and the mitigation
that worked best in the previous quarter was to plant the weaknesses rather than
lecture about them.

> Excessive autonomy is far more memorable when it is discovered in code the cohort
> already trusted.

Do not deploy anything from this branch.

---

## What is already fixed

- **The question.** Above.
- **The layer.** 3 — orchestration and state. Without it: single-shot answers only,
  no multi-step work.
- **The failure mode it addresses.** *Loop exhaustion* — an autonomous process
  repeats a step, or ping-pongs between two, until a budget runs out. State and step
  limits belong to orchestration.

## The legal anchor

This session is not only an engineering exercise.

> **DPA s.35 — automated individual decision-making.** A data subject has the right
> not to be subject to a decision based solely on automated processing where it
> produces legal effects or significantly affects them — with exceptions for contract
> necessity, statutory authorisation, and consent. Where it applies, the controller
> **must notify the person in writing** that the decision was made that way, and the
> person may request that it be **reconsidered or retaken not solely automatically.**

That is the legal basis for the human-in-the-loop checkpoint this session builds. **It
is not a design preference; in scope it is a requirement.** Expect `# DPA s.35:`
anchors in the code, and expect to be able to point at the line that satisfies it.

## Prepare for it

- Read **section 35 of the Act** in full. It is short.
- Come with an answer to: in a system you work on, where *should* a human be in the
  loop, and is one there now?
- Recorded traces and deterministic mocks are prepared for every session involving
  autonomous behaviour — live agent demos fail unpredictably, and the fallback is
  planned rather than improvised.

← [Session 06](../s06/README.md) · [Repository guide](../../docs/repository-guide.md)
