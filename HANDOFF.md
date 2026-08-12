# Handoff — continuing in Claude Code

Transient. `CLAUDE.md` holds the durable rules and is auto-loaded every session;
this file is the state of play as of **12 August 2026**. Delete or rewrite it once
Session 02 is built.

> **Updated 12 August 2026, after the first run against the real corpus.** The three
> blocking items below are **done**: both documents are converted from PDF, reported
> clean (75/75 sections of the Act, 4/4 landmarks) and pinned in
> `corpus/MANIFEST.sha256`. The repository was renamed to `q3-ai/` and the tooling is
> now verified end to end against the real corpus rather than a synthetic one.
>
> Session 01 **had not run** as of this date — the theory was covered, the codelab was
> not. So `eval/questions.yaml` and `eval/baseline.md` remain the room's to fill, the
> `2026-08-05` row in `eval/baseline.md` is a plan rather than a record, and
> `session-01-baseline` has deliberately not been created: it is the room's live
> demonstration to make, not a branch to hand them pre-built.
>
> Four further defects were found and fixed on that first run — listed below.

## Getting started

```bash
git clone https://github.com/developers-mania/q3-ai.git && cd q3-ai
git log --oneline && git branch -a && git tag
claude
```

The repository is hosted at `developers-mania/q3-ai`, which settles the ownership
question below: it belongs to the community, not to one account. Launch Claude Code
from the repository root so `CLAUDE.md` loads.

## What exists

Session 01 only. Three commits:

| Branch / tag | State |
|---|---|
| `session-01-start` | Everything except the two files built live |
| `solution/session-01`, `main`, `session-01-baseline` | Adds `src/pipeline.py` and `sessions/s01/lab.py` |

`git diff session-01-start main` is a 346-line diff across exactly those two files.
That diff is the Session 01 lesson, and the pattern every later session follows.

Built from the Session 01 Content Pack and Study Guide: naive pipeline (load,
chunk at 500 chars, TF-IDF, top-3), deterministic retrieval scorer, jupytext lab,
setup check, corpus checksum pin, corpus preparation tool, and the flaws /
decisions / standard / layer-ownership records.

~~**Not verified end to end**~~ — verified on 12 August 2026 against the real corpus.
`tools/check_setup.py` prints its four `OK` lines, the pipeline builds 655 chunks, and
the scorer scores. The predicted encoding issue was real; see defect 4 below.

## Defects found and fixed

Three in the Content Pack's own code — the first two would have broken the session
in the room. Worth carrying into Session 02's content pack review.

1. **The scorer would have returned near 0% regardless of retrieval quality.**
   Step 6 matches `q["answer"]` as a substring, and the eval example sets
   `answer: "72 hours"` while s.43 reads *seventy two hours*. Fixed with the
   `expect` field. The demonstration: two identical questions against an identical
   corpus, differing only in `expect`, score MISS and HIT.
2. **Step 6's `__main__` block referenced `chunks`, `vectorizer` and `matrix`,
   none of which were bound in that scope.** A `NameError` at 3:45 on a projector.
   Replaced with a real `main()` plus `--score` and `--ask`.
3. **`corpus/MANIFEST.sha256` was ignored** while the docs instructed committing
   it — the pin would not have survived a clone.

And one in the scaffold itself: `corpus/*.txt` was gitignored, contradicting the
Content Pack, which specifies `session-01-start` as containing the corpus files.
Corrected — see the non-negotiable in `CLAUDE.md`. The `.gitignore` rule and the
"not committed" prose in `README.md` and `corpus/README.md` had survived that fix and
were still contradicting it; all three now agree.

## Found on the first real run, 12 August

4. **`tools/prepare_corpus.py` could not read a PDF at all on Windows.** `pdftotext`
   was told to emit UTF-8 while `subprocess.run(text=True)` decoded with the locale
   codec, so the decode died in the reader thread, `stdout` came back `None`, and
   `normalise()` raised `TypeError`. `check=True` cannot catch this — the exit code is
   clean. Fixed with an explicit `encoding="utf-8"`.
5. **Three of the four DPA landmarks reported MISSING on a sound conversion.** Two
   were hyphens: the Act writes *seventy-two hours*, `LANDMARKS` checked *seventy two
   hours*. The third, *ninety days* at s.56(5), is split across a line break by
   `pdftotext -layout`, which wraps at ~80 columns. Both would have sent a facilitator
   hunting for a better source that did not exist.
6. **The same line wrapping silently broke the `expect` mechanism.** The scorer did a
   raw substring test, so any answer phrase straddling a wrap scored MISS on a perfect
   retrieval — defect 1 arriving by a second route nobody had seen. Fixed with
   `normalise_for_match()` in `src/pipeline.py`, and the identical rule as `flatten()`
   in `tools/prepare_corpus.py`.
7. **The corpus was written with CRLF on Windows**, against the Unix-line-endings
   target in `corpus/README.md`. Scores are unaffected — `Path.read_text()` normalises
   newlines on read — but the bytes and therefore the checksum differ by platform, so
   the pin would report `CHANGED` on a clean Windows clone. Fixed with `newline="\n"`
   and enforced by `.gitattributes`.

Defects 4 and 7 are Windows-specific, and every one of 4–7 is invisible on a clean
run against a synthetic corpus. Worth carrying into the Session 02 content pack review:
the pattern is that the tooling's *reports* were wrong, not its conversions.

## Blocking, in order

1. **Convert the corpus.** `python tools/prepare_corpus.py sources/dpa.docx --name
   dpa-2019`, then read the report. Prefer DOCX over PDF; PDF loses section
   numbering, which is what Session 03 recovers and where the largest predicted
   jump comes from. Must happen days ahead — a failed report means finding another
   source or running OCR.
2. **Then write `expect` strings**, grepping the converted text, never the
   canonical publication.
3. **Then** `tools/verify_corpus.py`, and commit text plus manifest together.

## Open questions

- **Did Session 01 run on 5 August as scheduled?** If so, the room's twenty
  questions and the baseline number exist on paper or a whiteboard photo and must
  reach `eval/questions.yaml` and `eval/baseline.md` before the corpus is frozen.
  They cannot be reconstructed later. If it has not run, ignore this.
- **The subsidiary regulations decision** (LN 263, 264, 265) is open until Session
  02. If it goes ahead it must go ahead early — every later chunk index depends on
  it.
- **`docs/layer-ownership.md` and `docs/decisions.md` are blank templates**
  awaiting the room's names and the Session 03 reason-in-one-sentence.
- ~~**Repo owner and host not named.**~~ Hosted at `developers-mania/q3-ai` as of
  12 August 2026. Q2's failure was instruments built and never operated, and an
  unowned repo is the same failure in a new form — so the *operator* is still the
  open half of this: who runs `--score` each week and records the row.
- ~~**`<repo-url>` is a placeholder.**~~ Resolved in `README.md` and
  `tools/build_notebooks.py`. Still outstanding: no `LICENSE`. The corpus is public
  domain, the code is not yet licensed.

## Suggested first prompt

> Read CLAUDE.md and HANDOFF.md. I have the DPA and AI Strategy as [DOCX/PDF] in
> ./sources. Convert them with tools/prepare_corpus.py, walk me through the report,
> and stop before we write any evaluation questions.

Then, once the corpus is pinned, Session 02 is built by branching
`session-02-start` from `solution/session-01` and adding scaffolding for structured
ingestion and source metadata — which fixes Flaw 5. Send the Session 02 Content
Pack in that session.
