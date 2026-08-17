# Session 09 · Knowing It Works

> **The question this session answers**
> *How do you prove the system works, and how do you find out when it doesn't?*

| | |
|---|---|
| **Date** | Wednesday 30 September 2026 · 2:00–4:00 PM |
| **Module** | 4 · Production, Guardrails and LLMOps |
| **Stack layer** | 5 — safety and evaluation |
| **Start branch** | `session-09-start` (= `solution/session-08` + scaffolding) |
| **Repairs** | **Flaw 4** — no confidence threshold; the system never says "I don't know" |

---

## ⏳ The codelab for this session is not published yet

**Published at:** with the Session 07 announcement.

---

## What is already fixed

- **The question.** Above.
- **The layer.** 5 — safety and evaluation. Without it: *you cannot tell whether any
  change helped or hurt.*
- **The flaw it repairs.** Flaw 4, from [`docs/flaws.md`](../../docs/flaws.md), named
  on 5 August and open ever since.

## The shape of it

This session closes the loop on nine weeks of work, and it does two things:

**It formalises the measurement.** The evaluation set the room has been running by
hand since 5 August becomes an automated suite, CI-integrated. And answer quality is
added alongside retrieval accuracy — so **the number stops being a single number.**

Retrieval accuracy was the right instrument for Sessions 01–05 because it is
deterministic, needs no model, no network and no key, and returns the identical value
every run. It cannot catch a system that retrieves perfectly and then writes a bad
answer. That gap is closed here, and the cost — a metric that no longer returns the
same value twice — is paid deliberately and late.

**It attacks the system.** Everything built so far is tested *and* attacked: prompt
injection, zero-trust input/output validation, PII masking, unbounded consumption.

## Flaw 4, in full

> If every chunk scores 0.02 — meaning nothing matched — the system still returns
> three of them, and the model still answers. It has no way to say **"I do not
> know"**, which is the single most valuable sentence a retrieval system can produce.

Building abstention means choosing a threshold, and a threshold has two error rates
in exactly the way Session 03's redaction rule did. **The `docs/decisions.md` entry
from Session 03 is what makes that conversation short** — the room has already
reasoned about a safeguard measured in both directions.

## Standing references

- **OWASP Top 10 for LLM Applications** — the working engineering standard, from
  prompt injection through to unbounded consumption. *Verify the current edition
  before slides are built; category numbering has changed between revisions.*
- **NIST AI Risk Management Framework** — the governance vocabulary, and the language
  a US-affiliated partner reasons in. Read for the framing rather than the checklists.

## Prepare for it

- Bring the questions that have failed **every week since August**. They are the most
  informative items in the file, and this is the session that finally has the tools to
  ask why.
- Re-read your Session 03 redaction decision. The same argument returns as a
  threshold.

← [Session 08](../s08/README.md) · [Repository guide](../../docs/repository-guide.md)
