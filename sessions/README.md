# The ten sessions

Each session answers **one question**. The question is fixed and was published on day
one. The technology used to answer it is not — it is decided on a rolling two-week
horizon, so the series can track a field moving faster than any syllabus written in
July could anticipate.

Every session has a codelab guide in `sessions/sNN/README.md` telling you what to
check out, **where to look in the repository**, what the codelab aims to do, and
**how to know it worked.**

Sessions marked ✅ are built and tagged. To replay one on your own:

```bash
git fetch --tags --force
git switch -c play/your-name solution/session-NN
python sessions/sNN/lab.py
```

New here? Start with the [repository guide](../docs/repository-guide.md).

---

| # | Date | Session | Layer | Repairs | Built | Guide |
|---|---|---|---|---|---|---|
| 01 | 5 Aug | **What Changed** | 1, 2 | *creates* the flaws | ✅ `solution/session-01` | [→](s01/README.md) |
| 02 | 12 Aug | **Where The Data Comes From** | 1 | Flaw 6, half of 5 | ✅ `solution/session-02` | [→](s02/README.md) |
| 03 | 19 Aug | **Getting Data Ready** | 1→2 | Flaw 1 | — | [→](s03/README.md) |
| 04 | 26 Aug | **Giving Software Memory** | 2 | Flaw 2 | — | [→](s04/README.md) |
| 05 | 2 Sep | **Remembering The Right Thing** ◇ | 2 | Flaw 3 | — | [→](s05/README.md) |
| 06 | 9 Sep | **Handing Over The Tools** | 4 | — | — | [→](s06/README.md) |
| 07 | 16 Sep | **Letting Software Decide** | 3 | — | — | [→](s07/README.md) |
| 08 | 23 Sep | **(open slot)** ◇ | tbd | — | — | [→](s08/README.md) |
| 09 | 30 Sep | **Knowing It Works** | 5 | Flaw 4 | — | [→](s09/README.md) |
| 10 | 7 Oct | **The Standard We Set** | 5 | — | — | [→](s10/README.md) |

◇ = open slot. Sessions 03, 05 and 08 have their topics chosen during the quarter,
each with a fixed decision point: **Session 03's topic is set at Session 01,
Session 05's at Session 03, and Session 08's at Session 05.**

---

## The questions, in full

| # | The question it answers |
|---|---|
| 01 | What actually changed in how software is built, and what does it mean for the work I already do? |
| 02 | How does data get into a system reliably, and what breaks when it doesn't? |
| 03 | What shape does data need to be in before a model can use it — and what has to be stripped out first? |
| 04 | How does an application recall things it was not trained on? |
| 05 | How do you make retrieval accurate instead of merely plausible? |
| 06 | How does a model use your systems safely, through a standard interface rather than custom glue? |
| 07 | How does software choose what to do next, and where does a human stay in the loop? |
| 08 | Chosen in-quarter — decided at Session 05. |
| 09 | How do you prove the system works, and how do you find out when it doesn't? |
| 10 | What do we, as a group, hold ourselves to when we build this way? |

## The shape of the arc

**Sessions 02 and 03** establish that intelligence is only as good as the data
underneath it — the least glamorous and most consequential part of the work.

**Sessions 04 and 05** give the system memory, then make that memory trustworthy. The
distinction between retrieval that returns *something* and retrieval that returns *the
right thing* is the difference between a demo and a product.

**Sessions 06 and 07** give the system hands. This is where the quarter is most
current, and where it is most exposed to a standard that is still settling.

**Session 09** closes the loop by testing everything built so far — and by attacking
it. **Session 10** converts ten weeks of decisions into a written standard the group
adopts.

## How a session runs

```
Setup (15 min) → Talk (45 min) → Hands-on (50 min) → Commit and preview (10 min)
```

- Every session begins from a **prepared starting branch**, so the room starts level
  regardless of who kept up. Missing one Wednesday does not put you behind.
- Every session ends with **something committed** — code, a document, or an
  evaluation result.
- Every session **names the standard it earned**, in one line, for the Session 10
  workshop. That assembles the final standard incrementally rather than authoring ten
  items cold in a twenty-minute block.
- Participants without suitable hardware follow a parallel track producing the same
  conceptual output.

## Why later guides are short

Sessions 04–10 carry only what is genuinely fixed: the question, the layer, the flaw
repaired, and the decision point. Their codelabs are published two sessions ahead.

That is a discipline, not an omission. **Every technology in this quarter is
introduced to answer a question posed before the technology was named** — and
pre-building a codelab in August for a session in September would quietly reverse
that. Participants always know the next two sessions in full detail, and always know
the shape of all ten.
