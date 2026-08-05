# Plan: Search Course Redesign — Scaffolded Notes + One Growing Engine

> Source PRD: `prd/search-course-redesign.md`

## Architectural decisions

Durable decisions that apply across all phases:

- **Engine repo:** one git repository at `exercises/wikisearch/`; a git tag per
  completed spine module (`end-of-m1`, `end-of-m2`, …) gives diffable snapshots.
- **Satellites:** orthogonal topics live in sibling folders `exercises/module-N-*/`
  (chunking, storage, pipeline, fine-tuning, eval) — not inside the engine.
- **Note template (every module):** Goal → "Where this fits (builds on prior)" →
  "The idea in plain English" → read-only worked example (signals + ranking + why,
  no arithmetic) → scaffolded "your turn" → concepts-to-capture → optional production
  footnote (one verified file, one thing to notice) → open questions.
- **Prose economy:** materials carry only teaching substance and actionable
  steps — no meta-narration (sentences describing what a section just did) and no
  restating the learner's preferences or the design rationale (that lives in
  `learning-approach.md`). Wayfinding labels are fine; justifying them is not.
- **Starter code:** guided skeleton — boilerplate done and runnable; teaching
  functions carry signatures, input/output docstrings, numbered sub-step comments;
  learner writes the core logic. Reference material embedded in the scaffold
  (formula blocks, math notation) is expressed in runnable terms — required imports
  provided, notation symbols mapped to the code's identifiers, non-obvious operations
  paired with their language equivalent (`ln(x)` → `math.log(x)`). Mapping happens at
  the point of use — a sub-step referencing a symbol names its code identifier there
  (`|doc|` → `index.doc_len[doc_index]`), not only in a shared definitions block.
- **Language:** Python for the engine and all modules **except Module 7**, a
  standalone Elixir project (Oban + Ecto state machine).
- **Data:** public HuggingFace `wikimedia/wikipedia`; `setup_data` auto-downloads +
  subsamples the 5k on first run (idempotent); the full 226k is a deliberate opt-in
  from Phase 3 on.
- **Spine (grows in engine):** M1 FTS, M2 vectors, M4 hybrid, M5 rerank, M8
  query-path, M9 query understanding, M10 RAG, M11 agentic.
- **Getting unstuck:** gating is intentional (a broken module blocks the next); no
  static solution files; learner asks Claude; tags are diff references only.
- **Glossary:** learner-authored; notes name the terms and pre-explain them; no
  pre-filled definitions.
- **Meta-layer:** course-root `learning-approach.md` (Approach + Rationale authored;
  Feedback = fixed cross-course dimensions + per-strategy scorecard, learner-filled);
  a closing no-code retrospective module.
- **Governance:** public Wikipedia only (no PII/Instinct data); API keys via env
  vars; Turbopuffer on a personal free-tier namespace.
- **Build order is capability-grouped, not study order** — the learner still studies
  0→13→capstone; materials just need to exist.

---

## Phase 1: Tracer — Module 1 end-to-end (FTS/BM25)

**User stories**: 1–21, 26, 27, 35, 36, 38

### What to build

The thinnest complete slice that drives *every* layer of the course machinery
through a single module, to validate the format before any mass production. Stand up
the `wikisearch` engine repo with data bootstrap, and fully realize Module 1: the
plain-English note, a read-only worked example, a guided `bm25_cli` starter, glossary
hooks, one verified production footnote, and a completion tag.

### Acceptance criteria

- [ ] `exercises/wikisearch/` is a git repo containing a runnable Python project
- [ ] The setup step downloads + subsamples the 5k corpus idempotently (rerun = no work)
- [ ] `module-notes/module-1-fts-bm25.md` follows the full note template
- [ ] The worked example shows signals + ranking + why, and its ordering is verified
      by actually running it
- [ ] The `bm25_cli` starter runs immediately (loads data, parses args); teaching
      functions are guided TODOs
- [ ] Any formula/notation in the starter (e.g. the BM25 reference block) is expressed
      in runnable terms — required imports present, notation mapped to the code's
      constants, non-obvious operations paired with their Python equivalent
- [ ] With TODOs filled, `python bm25_cli.py "photosynthesis"` returns 5 ranked titles
- [ ] The optional footnote references a chunky-kong path verified to exist
- [ ] Engine tagged `end-of-m1`
- [ ] Learner has reviewed and confirmed the format feels right

---

## Phase 2: Framing & meta-layer

**User stories**: 2, 16, 28–32

### What to build

The course-level framing around the modules: the learning-approach document, the
reformatted no-code orientation module, the retrospective module, the closing
syllabus section, and the rewritten exercises README describing the growing-engine +
satellites layout.

### Acceptance criteria

- [ ] `learning-approach.md` exists with Approach + Rationale written and a blank
      Feedback section scaffolded (generic dimensions + per-strategy scorecard)
- [ ] `module-notes/module-0-orientation.md` reformatted to the template (no-code
      variant), preserving the learner's existing answers
- [ ] `module-notes/retrospective.md` created; its only task is completing the feedback
- [ ] `search-syllabus.md` gains a closing Retrospective section
- [ ] `exercises/README.md` rewritten for wikisearch + satellites (supersedes
      one-folder-per-module)

---

## Phase 3: Engine spine — semantic & hybrid retrieval

**User stories**: 3–5, 10–15, 24, 25, 33

### What to build

Grow the engine from keyword-only to semantic then hybrid retrieval, add cross-encoder
reranking, and build the chunking satellite that lets the engine index real article
bodies. Ends with the first two portfolio demos.

### Acceptance criteria

- [ ] Each module note follows the template with a cumulative worked example
- [ ] Engine gains vector similarity search over the 5k (local MiniLM embedder);
      demo query "a planet that has rings" surfaces Saturn
- [ ] `module-3-chunking/` satellite demonstrates content-hash idempotency
      (rerun on unchanged input = 0 re-embeds)
- [ ] Full 226k opt-in path works; engine supports `--mode fts|hybrid`
- [ ] `--rerank` retrieves hybrid top-50 → cross-encoder → top-10
- [ ] Portfolio demos runnable; tags `end-of-m2/m4/m5`; footnote paths verified

---

## Phase 4: Engine spine — query intelligence & generation

**User stories**: 4, 10, 24, 33

### What to build

Layer query-path patterns, LLM query understanding, RAG with citations, and an agentic
multi-hop loop onto the engine. Ends with the web-app and agentic portfolio demos.

### Acceptance criteria

- [ ] `excludeIds` pagination + a new sort mode added end-to-end
- [ ] Query-understanding layer (paraphrase / HyDE / router) wraps the retrieve+rerank
      engine
- [ ] "Ask Wikipedia" web app answers with article + section citations
- [ ] Agentic researcher answers a multi-hop query with a reasoning transcript + citations
- [ ] API keys read from env vars, never hardcoded
- [ ] Tags `end-of-m8/m9/m10/m11`; footnote paths verified

---

## Phase 5: Infra satellites

**User stories**: 22, 23, 25

### What to build

Two standalone studies beside the engine: a Turbopuffer namespace with filter-vs-scan
benchmarking, and an Elixir Oban + Ecto state-machine ingestion pipeline that mirrors
chunky-kong's real worker chain.

### Acceptance criteria

- [ ] `module-6-storage/` demonstrates namespace upsert + filter vs full-scan latency
- [ ] `module-7-pipeline/` is a runnable Elixir project (Oban + Ecto) with a
      `pending → … → indexed` state machine, retries, and content-hash idempotency
- [ ] Re-running the pipeline on unchanged input does zero work
- [ ] Notes follow the template; footnotes to chunky-kong's real pipeline verified

---

## Phase 6: Quality satellites

**User stories**: 25, 33

### What to build

The measurement layer: a domain-tuned embedding experiment with before/after numbers,
and an eval harness scoring the engine's retrieval and RAG output.

### Acceptance criteria

- [ ] `module-13-eval/` computes recall@5, MRR, NDCG@10 across retrieval modes over
      ≥30 labeled queries, plus LLM-as-judge faithfulness scoring
- [ ] `module-12-embeddings/` fine-tunes MiniLM and reports before/after recall/NDCG delta
- [ ] A portfolio writeup artifact (eval figure) is produced
- [ ] Notes follow the template

---

## Phase 7: Capstone + retrospective

**User stories**: 29–34

### What to build

The culminating full WikiSearch build over the *same* grown engine (multi-namespace +
hybrid + rerank + query understanding + agentic + RAG + eval), followed by the learner
completing the learning-approach feedback.

### Acceptance criteria

- [ ] Capstone note follows the template and reuses the grown engine (not a fresh start)
- [ ] A second namespace is added alongside Wikipedia
- [ ] The eval harness reports the required metrics for the capstone build
- [ ] Learner completes the Feedback section of `learning-approach.md` via the
      retrospective module
- [ ] Final tag applied
