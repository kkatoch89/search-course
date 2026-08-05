# PRD: Search Course Redesign — Scaffolded Notes + One Growing Engine

## Problem Statement

I'm working through a self-authored 16-week search/retrieval course, but I'm new to
the domain (full-text search, embeddings, vector search, RAG, agentic search) and I
manage ADHD, which makes it hard to stay on task. The course material doesn't support
me:

- The `module-notes/*.md` files look like they should contain instructions, but
  they're actually terse fill-in worksheets — so I keep opening them expecting
  guidance and finding blanks.
- The exercises assume knowledge I don't have yet ("compute BM25 by hand," "run two
  queries against local chunky-kong") without explaining what a toy doc is, what
  setup is required, or what the deliverable actually is.
- The primary exercise for many modules is spelunking through `chunky-kong`, a large
  unfamiliar production codebase. When I'm new to the concept *and* fighting to stay
  focused, I can't tell what's important, and I stall.
- Reading links are descriptions, not links; the "codebase walk" paths sometimes
  point at the wrong file (e.g. the ≤8 rank_by clause invariant was attributed to the
  wrong `ranking.ex`).
- Rote work like by-hand BM25 arithmetic feels like a waste of time — the algorithm
  is tried and tested; grinding the math myself teaches me little.

I want to learn the concepts and end up with something real to show, not get lost in
someone else's code or busywork.

## Solution

Rebuild the course so each module is a **self-contained learning unit**, and so the
exercises accumulate into **one search engine I build up module by module**.

Each module note will: explain the idea in plain English; show a read-only worked
example that layers this module's new concept onto the previous modules'; give me
runnable starter code with the boring parts done and clearly-marked gaps for the
parts that teach me something; and point me (optionally, at the end) to the one place
in production code where I can see it "in the wild" — never as a blocker.

The exercises stop being 13 disconnected mini-projects and become a single
"WikiSearch" engine that grows: full-text search, then vectors, then hybrid, then
reranking, then query understanding, RAG, and agentic search. Side-topics (chunking,
storage, the ingestion pipeline, fine-tuning, eval) sit beside the engine as focused
satellite exercises. When I get stuck, I ask Claude rather than reaching for a
solutions file.

I'll also capture the *approach itself* in a `learning-approach.md` file and rate it
at the end, so I can compare strategies across all my courses and refine how I learn.

## User Stories

1. As a learner, I want each module note to clearly explain the concept in plain
   English, so that I understand the idea before touching code.
2. As a learner, I want to know at a glance whether a file is instructions or a
   worksheet, so that I stop opening notes expecting guidance and finding blanks.
3. As a learner, I want a read-only worked example in every module, so that I see the
   concept applied concretely before I attempt it myself.
4. As a learner, I want each worked example to build on the previous module's
   concepts, so that knowledge compounds instead of resetting each week.
5. As a learner, I want worked examples to show the driving signals (term frequency,
   document frequency, length) and the resulting ranking with a plain-English "why,"
   so that I see the mechanism without slogging through formula arithmetic.
6. As a learner, I do not want to compute algorithms by hand, so that I spend my
   energy on understanding rather than rote arithmetic.
7. As a learner, I want every number or ordering in an example to be verified by
   actually running it, so that I never memorize something subtly wrong.
8. As a learner, I want starter code with the boilerplate (arg parsing, data loading,
   output) already written and runnable, so that I focus on the concept, not plumbing.
9. As a learner, I want the teaching functions to come with signatures, input/output
   docstrings, and numbered sub-step comments, so that I never face a blank page but
   still write the core logic myself.
10. As a learner, I want the exercises to form one engine that grows module by module,
    so that I finish the course with a real, coherent portfolio artifact.
11. As a learner, I want a stall in one module to block the next, so that I'm forced to
    actually understand each layer before building on it.
12. As a learner, I want to ask Claude when I'm stuck rather than peek at a solution
    file, so that getting unstuck is low-friction but I don't skip the learning.
13. As a learner, I want each completed module tagged in git, so that I can diff "what
    did this module add?" and reset to a known-good state to compare against.
14. As a learner, I want the engine to auto-download the small 5k dataset on first run,
    so that early modules just work with no setup ceremony.
15. As a learner, I want the large 226k dataset to be a deliberate opt-in step, so that
    I'm not ambushed by a huge download and embedding cost before Module 1 runs.
16. As a learner, I want the chunky-kong/merlin production code demoted to an optional
    "see it in the wild" footnote, so that it enriches my learning without blocking it.
17. As a learner, I want each optional footnote to point at exactly one file and one
    thing to notice, so that I'm not lost in a large codebase.
18. As a learner, I want every production path referenced in a footnote to be verified
    to exist, so that I don't chase a wrong file path like the ranking.ex mix-up.
19. As a learner, I want to write my own glossary definitions, so that the act of
    rephrasing cements the concept.
20. As a learner, I want the module note to tell me exactly which terms to define and
    to have already explained them in the worked example, so that writing a glossary
    entry is a quick recall rep, not a research task.
21. As a learner, I want to ask Claude to check my glossary wording, so that I know
    whether I understood the term correctly.
22. As a learner, I want the ingestion-pipeline module in Elixir as a standalone
    project, so that it maps directly onto chunky-kong's real Oban/Ecto workers and my
    day job.
23. As a learner, I want the rest of the engine and exercises in Python, so that I stay
    in the language with the richest search/ML ecosystem and the lowest friction.
24. As a learner, I want the retrieval-spine modules (FTS, vectors, hybrid, rerank,
    query-path, query understanding, RAG, agentic) to live in the one engine repo, so
    that the query path evolves in one place.
25. As a learner, I want orthogonal topics (chunking, storage, pipeline, fine-tuning,
    eval) as separate satellite folders, so that studies *around* the engine don't
    clutter the query path.
26. As a learner, I want Module 1 built first as a working proof, so that I can confirm
    the format feels right before the whole course is produced against it.
27. As a learner, I want the format validated on one module before mass-production, so
    that a format problem is cheap to fix rather than discovered on the 14th file.
28. As a learner, I want a `learning-approach.md` documenting the strategies and the
    reasons behind them, so that I understand *why* the course is shaped this way.
29. As a learner, I want a feedback section in `learning-approach.md`, so that I can
    record what worked and what didn't after finishing.
30. As a learner, I want the feedback split into generic dimensions plus a
    per-strategy scorecard, so that I can compare across courses *and* capture what was
    specific to this one.
31. As a learner, I want a final no-coding retrospective module, so that I'm actually
    prompted to fill out the feedback rather than forgetting.
32. As a learner, I want to reuse `learning-approach.md` across all my course folders,
    so that I can compare approaches over time and refine how I structure future
    courses.
33. As a learner, I want the portfolio-tagged modules (hybrid, rerank, web app,
    agentic, fine-tuning, capstone) to produce demoable results, so that I have
    concrete artifacts to show.
34. As a learner, I want the capstone to be the culmination of the same engine, so that
    it feels like a finish line, not a fresh start.
35. As a learner, I want exercises to use only public Wikipedia data, so that I never
    handle customer or Instinct-sensitive data during learning.
36. As a learner, I want API keys read from environment variables, so that I never
    hardcode secrets in my exercise code.
37. As a learner, I want notes to contain only teaching substance and actionable
    steps — no sentences narrating what a section just did, and no restating my own
    preferences or the design's rationale back at me — so that reading stays dense
    and respects what I already know.
38. As a learner, I want any math or notation embedded in the starter code (formula
    blocks, symbols) expressed in runnable terms — required imports provided, each
    notation symbol mapped to the code's actual variable name, and non-obvious
    operations paired with their language equivalent (e.g. `ln(x)` → `math.log(x)`) —
    so that deciphering notation or language mechanics never blocks the concept I'm
    there to learn.

## Implementation Decisions

- **Note structure:** every module note follows one template — Goal → "Where this fits
  (builds on prior module)" → "The idea in plain English" → read-only worked example →
  scaffolded "your turn" → concepts-to-capture → optional production footnote → open
  questions.
- **Prose economy (voice):** notes carry only teaching substance and actionable
  instructions. No meta-narration — sentences that describe what a section is doing
  rather than teaching (e.g. "notice you did no arithmetic") — and no restating the
  learner's stated preferences or the pedagogy's rationale inside the materials;
  that rationale lives in `learning-approach.md`. Wayfinding labels (section
  headers, a one-line legend) are fine; justifying them is not.
- **Worked-example fidelity:** show driving signals + final ranking + plain-English
  why; no formula arithmetic; all shown values verified by running them.
- **Starter code:** guided skeleton — boilerplate done and runnable; teaching
  functions carry signatures, input/output docstrings, and numbered sub-step comments;
  learner writes the logic. Reference material embedded in the scaffold (formula
  blocks, math notation) is given in runnable terms: required imports provided, each
  notation symbol mapped to the code's actual identifier, and non-obvious operations
  paired with their language equivalent (e.g. `ln(x)` → `math.log(x)`). Deciphering
  notation or language mechanics is not the lesson. Mapping happens at the point of
  use: a sub-step that references a symbol names its code identifier right there
  (`|doc|` → `index.doc_len[doc_index]`), not only in a shared `where`/definitions
  block the learner has to cross-reference.
- **One growing engine:** a single git repository ("WikiSearch") that the
  retrieval-spine modules extend in place; a git tag marks each completed module for
  diffable snapshots.
- **Spine vs satellites:** spine modules (full-text, vectors, hybrid, rerank,
  query-path patterns, query understanding, RAG, agentic) live in the engine; chunking,
  storage, ingestion pipeline, fine-tuning, and eval are standalone satellite
  exercises.
- **Language split:** Python for the engine and all modules except the ingestion
  pipeline module, which is a standalone Elixir project using an Oban + Ecto state
  machine that mirrors chunky-kong's real worker chain. Capstone is Python-primary.
- **Gating and unstuck strategy:** an incomplete or buggy module intentionally blocks
  the next; there are no static reference-solution files; the learner asks Claude when
  stuck; end-of-module tags serve only as diff references.
- **Glossary:** learner-authored; module notes name the terms and pre-explain them in
  the worked example; Claude checks wording on request; no pre-filled definitions.
- **Data bootstrap:** an idempotent setup step auto-downloads and subsamples the 5k
  corpus on first run; the full 226k corpus is a deliberate opt-in from Module 4 on;
  both sourced from the public HuggingFace `wikimedia/wikipedia` dataset.
- **Production footnotes:** optional, one file + one thing to notice each, with every
  referenced path verified to exist in the local chunky-kong/merlin checkouts.
- **Meta-layer:** a course-root `learning-approach.md` with an Approach section and a
  Rationale section (authored during the build) and a Feedback section the learner
  fills — structured as fixed cross-course dimensions plus a per-strategy scorecard.
- **Retrospective module:** a final no-coding module added to the syllabus and rollout
  whose only task is to complete the feedback section.
- **Execution order:** build and validate Module 1 as a live proof (engine skeleton,
  data setup, note, starter, first tag) before producing the remaining modules.
- **Exercise layout:** rewrite the exercises README to describe the growing-engine +
  satellites layout, replacing the current "one standalone folder per module" model.
- **Files preserved:** the syllabus (except a new closing retrospective section), the
  data-setup guide, the glossary scaffold, the top-level README, and the data
  directory are left intact.

## Out of Scope

- Rewriting `search-syllabus.md` wholesale — only a closing retrospective section is
  added; the curriculum content stays as the authoritative instructional source.
- Rewriting `data-setup.md`, `glossary.md`, or the top-level `README.md`.
- Doing the exercises *for* the learner — the engine ships as guided scaffolds with
  gaps the learner fills; Claude assists on request but does not complete the learning.
- Any change to the actual `chunky-kong` or `merlin` production code (e.g. filing a
  real rerank ticket) — production code is reference material only.
- By-hand algorithm computation as an exercise.
- Building the full 226k pipeline or embedding run as part of setup — it stays an
  explicit, learner-triggered step.
- Hosting/deploying the portfolio demos publicly (the engine is structured to allow it
  later, but publishing is not part of this work).

## Further Notes

- A concrete bug already surfaced and was fixed during review: the Module 1 note
  attributed the ≤8 `rank_by` clause cap to the low-level builder file, when it
  actually lives in the query-executor ranking module (`@rank_by_max_clauses 8`,
  which prioritizes glob boosts then top-weighted BM25 fields rather than erroring).
  The redesign's footnote-path verification step exists specifically to prevent
  repeats of this.
- A second friction instance surfaced while building Module 1's `bm25.py`: the BM25
  reference block used `ln` (undefined for someone new to Python, and `math` was not
  imported) and lowercase `k1`/`b` that didn't match the code's `K1`/`B` constants —
  so the formula, though mathematically clear, wasn't runnable without guessing.
  Fixed by importing `math`, noting `ln(x)` = `math.log(x)`, and mapping the symbols
  to the real constants. Generalized into the starter-code rule (user story 38):
  notation embedded in a scaffold must be expressed in runnable terms.
- The growing-engine choice was made over a "standalone folders with copied prior
  code" alternative; the learner explicitly preferred true continuity and accepted
  that gating a broken module is desirable.
- The Elixir pipeline is the one deliberate exception to the single-engine model,
  justified because ingestion is orthogonal to the query path and best learned in the
  language it ships in.
- Governance: exercises use public Wikipedia only (no PII, no Instinct source data);
  Anthropic/OpenAI keys via env vars / 1Password; Turbopuffer is already in Instinct's
  approved stack, so a personal free-tier namespace is fine (no new-vendor review).
- A `feedback`-type memory should be saved capturing this learning style so future
  sessions don't drift back to the terse original format.
- `learning-approach.md` is intended as a portable template the learner will replicate
  across other course folders.
