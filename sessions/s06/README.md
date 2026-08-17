# Session 06 · Handing Over The Tools

> **The question this session answers**
> *How does a model use your systems safely, through a standard interface rather than
> custom glue?*

| | |
|---|---|
| **Date** | Wednesday 9 September 2026 · 2:00–4:00 PM |
| **Module** | 3 · Protocols and Agentic Orchestration |
| **Stack layer** | 4 — protocol and execution |
| **Start branch** | `session-06-start` (= `solution/session-05` + scaffolding) |
| **Repairs** | Nothing on the flaw list. This session adds a **new layer** |

---

## ⏳ The codelab for this session is not published yet

**Published at:** with the Session 04 announcement.

This session carries a specific, known risk that shapes how it will be built.

> **Teach the specification, not the SDK.** The Model Context Protocol published a
> major specification revision on **28 July 2026** — the largest since the protocol
> launched. Session 06 falls on 9 September, roughly six weeks into the validation
> window, and **tooling may still be catching up.**
>
> Two consequences, both already decided:
> 1. The session is built against the specification itself, not against any vendor's
>    convenience wrapper.
> 2. **A working fallback branch is kept against the previous revision.**

The current specification must be read directly before this session is built. This
is the single clearest differentiator this cohort will have — and the reason it is
also the most exposed session of the quarter.

---

## What is already fixed

- **The question.** Above.
- **The layer.** 4 — protocol and execution. The first session above Layer 2.
- **The standing reference.** The MCP specification, read directly. Plus Simon
  Willison's writing on prompt injection, which becomes relevant from here on.

## The shape of it

For two years, every connection between a model and a real system was bespoke: each
team wrote its own glue, its own permission model, its own way of describing what a
tool did. Without this layer, **every tool is bespoke glue and permissions are ad
hoc.**

The deliverable is a tool interface built against a current open standard — a
portfolio artifact very few practitioners in the region currently hold.

## A note on what arrives with it

Security formally sits at Session 09, but participants start giving software autonomy
at Session 07. Two weeks of building agents with no defensive frame is a **known
risk**, and the mitigation is already decided:

> **Plant the weaknesses.** Session 07's starter code ships with an over-permissive
> tool interface and a resource that can be manipulated through injected
> instructions, and the room finds them.
>
> Excessive autonomy is far more memorable when it is discovered in code the cohort
> already trusted.

Which means the reading for that begins here.

## Prepare for it

- Read the **MCP specification** directly — not a vendor SDK's documentation.
- Read Simon Willison on prompt injection. The clearest sustained explanation of why
  the problem is structural rather than a bug to be patched.

← [Session 05](../s05/README.md) · [Repository guide](../../docs/repository-guide.md)
