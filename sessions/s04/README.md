# Session 04 · Giving Software Memory

> **The question this session answers**
> *How does an application recall things it was not trained on?*

| | |
|---|---|
| **Date** | Wednesday 26 August 2026 · 2:00–4:00 PM |
| **Module** | 2 · Context Engineering and Retrieval Systems |
| **Stack layer** | 2 — context and memory |
| **Start branch** | `session-04-start` (= `solution/session-03` + scaffolding) |
| **Repairs** | **Flaw 2** — the index matches words, not meaning |

---

## ⏳ The codelab for this session is not published yet

**This is deliberate, not an omission.**

The quarter fixes its ten *questions* on day one and decides the *technology* that
answers each on a rolling two-week horizon, published with that session's
announcement. Participants always know the next two sessions in full detail, and
always know the shape of all ten.

Writing this codelab now would mean choosing an embedding stack in August for a
session in late August, which is exactly the pre-commitment the design avoids — and
it would break the rule that **every technology is introduced to answer a question
posed before the technology was named.**

**Published at:** the organiser sync two sessions ahead — i.e. with the Session 03
announcement.

---

## What is already fixed

- **The question.** Above. It does not move.
- **The layer.** 2 — context and memory.
- **The flaw it repairs.** Flaw 2, from [`docs/flaws.md`](../../docs/flaws.md).
- **The measurement.** Retrieval accuracy and citation accuracy, re-run at 2:15
  against the same fixed set, compared to the **5 August** baseline.

## The shape of it

The corpus is now structured, cited, cut on meaning and cleaned. The index is still
the keyword matcher from 5 August, and it still has no idea what words mean. Ask it
about *"notifying the regulator"* when the Act says *"notify the Commissioner"* and it
returns nothing useful.

Session 04 replaces it with embeddings — and immediately complicates the story,
because **embeddings are worse than keyword matching at exact section numbers.** That
trade is why hybrid search exists, and why the honest answer is usually both.

Three threads are already known to run through it:

- Dense retrieval compared against the keyword baseline **question by question**, not
  in aggregate — the aggregate hides the trade.
- **Where the embeddings are computed**, and what s.50 of the Act has to say about
  it. This is the first session where the data sovereignty thread becomes an
  engineering decision rather than framing.
- The OWASP LLM Top 10 category covering weaknesses in vector and embedding systems
  maps directly onto this session, so the attack is taught alongside the technique.

## Prepare for it

- Add two evaluation questions **phrased in your own words**, deliberately avoiding
  the Act's vocabulary. These are the questions the keyword index fails and this
  session should fix. They are worth more than any code you could write in advance.
- Read the OWASP LLM Top 10 entry on vector and embedding weaknesses.
- Skim the retrieval chapters of *AI Engineering* (Chip Huyen, O'Reilly 2025).

← [Session 03](../s03/README.md) · [Repository guide](../../docs/repository-guide.md)
