# Opening hook — pre-recorded transcript

**Content Pack, 2:15–2:20.** The only moment in Session 01 that touches a model.
This file exists so the hook runs when the network does not.

> **RECORD THIS BEFORE THE SESSION.** The transcript below is a placeholder
> showing the required shape — it is *not* a real model response and must not be
> read to the room as one. Ask both questions of whichever model will be cited,
> paste the actual replies here, and record the model name and date.

| Field | Value |
|---|---|
| Model | _to be recorded_ |
| Date recorded | _to be recorded_ |
| Retrieval | None. No documents, no context, nothing but the question. |

---

## Question 1

```
Under the Kenya Data Protection Act, within how many hours must a data
controller notify the Data Commissioner of a personal data breach?
```

**Verified answer:** seventy-two hours — DPA s.43(1)(a)

**Recorded response:**

```
_paste the actual response here_
```

## Question 2

```
And within how many hours must a data processor notify the data controller
of the same breach?
```

**Verified answer:** forty-eight hours — DPA s.43(3)

**Recorded response:**

```
_paste the actual response here_
```

---

## Landing the point

The model may get the first one right. It may also say 24, or 48, or hedge. The
point is not which it does — it is that **nothing about the answer was flagged as
uncertain**. No exception, no error code, no stack trace. A fluent, well-formatted,
plausible sentence that may be wrong.

> Deterministic systems fail loudly. Systems with a model in them fail quietly and
> confidently. Every layer built from here exists to convert a quiet failure into a
> loud one.

**If the model answers both correctly**, the hook still works — say so plainly and
ask the room the follow-up: *how would you know?* Nothing in the output
distinguishes recall from invention. That is the same point arrived at from the
other side, and it is the more honest version of it.

## Why this is not scored

Generation appears once today, here, where its job is to fail memorably rather
than to be measured. Today's number scores **retrieval** — whether the pipeline
finds the right passage — which needs no model, no key and no network, and returns
the identical number every run.
