# Module 7 — Ingestion Pipeline: An Oban + Ecto State Machine

> **(read-only)** sections are for understanding; **Your turn** is what you
> build. Blanks marked _fill in_ are yours.

**Goal:** Build the machinery that keeps a search index *in sync* with a changing
corpus — a **background pipeline** that runs each document through chunk → embed →
store, survives failures by **retrying**, and does no work when nothing changed.
This is the one **Elixir** module, built on the exact stack Instinct's
`chunky-kong` uses: **Oban** (Postgres-backed background jobs) + **Ecto** (a
Postgres-backed **state machine**).
**Time box:** ~2.5 hours &nbsp;|&nbsp; **Time spent:** _fill in_ &nbsp;|&nbsp; **Done when:** `mix ingest.demo` walks two articles to `status=indexed` — surviving a deliberately flaky embed step via retries — then shows that re-intaking unchanged content does nothing while an edit re-runs the pipeline.

> **This is a _satellite_, and it's _Elixir_.** Standalone folder
> (`exercises/module-7-pipeline/`), a real mix project. It doesn't touch the
> Python `wikisearch` engine, so there's **no `end-of-m7` tag**. You need Elixir
> (~1.16) and a local Postgres. Don't worry about deep Elixir — you write two tiny
> pure functions; everything else is provided and runnable.

---

## Where this fits (pulls Modules 3, 2, and 6 together)

- **You already built the three stages** this pipeline runs: **chunking**
  (Module 3), **embedding** (Module 2), and **storing** in a vector store
  (Module 6). Each was a thing you did *once, by hand, on the whole corpus*.
- **The problem this module solves:** a real corpus *changes* — articles are
  added, edited, deleted, every day. You can't re-chunk-embed-store all 226k
  every time one article changes. You need something that, per document, runs the
  stages in order, **remembers where it got to**, **retries** the flaky bits, and
  **skips work** when the content hasn't changed.
- **This module adds** that orchestration: a **state machine** stored in Postgres
  (so progress survives a crash) driven by a **background job queue** (Oban).
  The chunk/embed/store steps themselves are *stubbed* — you did the real ones
  already; the lesson here is the pipeline *around* them.
- **New words:** background job / job queue, worker, state machine, durable state,
  checkpoint, retry / max_attempts / backoff, idempotency (again, from a new angle).

---

## The idea in plain English

1. **A state machine you can crash-and-resume.** Each document is a row with a
   `status`: `:pending → :chunked → :embedded → :indexed`. The status lives in
   Postgres, not in memory, so if the server dies mid-embed, the row is still
   sitting at `:chunked` when it comes back — you resume from the last
   **checkpoint** instead of starting over.

2. **A background job does the work, off the request path.** You don't chunk-embed-
   store while a user waits. You enqueue a **job**; a **worker** (Oban) picks it up
   later and runs it. That's why indexing can be slow and flaky without anyone
   noticing — it happens in the background, with retries.

3. **Retries rewind to the last safe checkpoint.** Embedding calls a model that
   *will* occasionally time out. When a stage fails, the worker records which
   stage died and returns an error; Oban **retries** the job (up to
   `max_attempts`). On retry you don't redo the whole pipeline — you rewind to the
   checkpoint *just before* the stage that failed and run forward. Safe to replay
   because every stage is **idempotent**.

4. **Idempotency decides whether to work at all.** Before running anything, compare
   the document's **content hash** (Module 3's idea) to what you stored last time.
   Unchanged → do nothing. Changed → reset to `:pending` and run again. Re-running
   a finished document is a harmless no-op.

> **The one split worth internalizing:** the *rules* of the state machine (what
> comes after what) are **pure functions** — no database, no jobs, trivial to
> reason about. The *side effects* (DB writes, calling the embedder, enqueuing
> jobs) live in the worker. You write the pure part; the messy part is provided.

---

## Worked example (read-only)

`mix ingest.demo` intakes two articles and drains the job queue synchronously so
you can watch every transition. Real output (the embed step is rigged to time out
on attempts 1–2, then succeed):

```
== 1. Intake two new articles → run the pipeline
[Photosynthesis]   chunk: 1 chunks
[Photosynthesis] chunk ✓   pending → chunked
[Photosynthesis] embed ✗   (attempt 1) embedding service timeout (simulated, attempt 1)
[Salt water]     chunk ✓   pending → chunked
[Salt water]     embed ✗   (attempt 1) embedding service timeout (simulated, attempt 1)
[Photosynthesis] retrying: rewind from failed embed → chunked
[Photosynthesis] embed ✗   (attempt 2) embedding service timeout (simulated, attempt 2)
[Salt water]     retrying: rewind from failed embed → chunked
[Salt water]     embed ✗   (attempt 2) embedding service timeout (simulated, attempt 2)
[Photosynthesis] retrying: rewind from failed embed → chunked
[Photosynthesis] embed ✓   chunked → embedded
[Photosynthesis] store ✓   embedded → indexed
[Salt water]     embed ✓   chunked → embedded
[Salt water]     store ✓   embedded → indexed
   drain: %{discard: 0, success: 2, failure: 4}
   Photosynthesis   status=indexed attempts=2
   Salt water       status=indexed attempts=2
```

**What happened, and why it's the whole module:**

- **Each article walks the checkpoints in order:** `pending → chunked → embedded →
  indexed`. The status is persisted at every arrow, so the pipeline always knows
  where each document is.
- **The embed step failed twice and the pipeline recovered.** On each failure the
  worker rewound to `:chunked` (the checkpoint *before* embed — note it did **not**
  re-chunk) and Oban retried. On the third attempt embed succeeded and it carried
  on to `store` and `indexed`. `attempts=2` records the two failures; `failure: 4`
  in the drain summary is the two articles × two failed embeds. `discard: 0` means
  nobody gave up — every job eventually succeeded.
- **`success: 2`** — two jobs finished cleanly, despite four intermediate failures.
  That's the point of a retrying pipeline: transient failures don't lose work.

Then the demo proves **idempotency**:

```
== 2. Idempotency: re-intake the SAME content
   intake returned: :unchanged  (no job enqueued — nothing changed)
   Photosynthesis   status=indexed attempts=2

== 3. A real edit re-runs the pipeline
   intake returned: :changed  (content changed — reset to :pending)
   ... chunk ✓ / embed retries / store ✓ ...
   Photosynthesis   status=indexed attempts=2
```

- **Unchanged content ⇒ no job at all.** The content hash matched, so intake
  returned `:unchanged` and enqueued nothing. Zero work — exactly like Module 3's
  cache hit and Module 6's upsert-by-id.
- **An edit ⇒ reset to `:pending` and re-run.** A one-word change flipped the hash,
  so the document went back through the whole pipeline.

_(Every line above is real output from the code you're about to complete.)_

---

## Your turn — write the state machine

The whole project is built and runnable except **two pure functions** in
`lib/ingest/resource_pipeline.ex`. They contain the *rules* of the pipeline; the
worker (`lib/ingest/worker.ex`) calls them.

### 1. Set up (once)

```bash
cd exercises/module-7-pipeline
mix setup          # deps.get + ecto.create + ecto.migrate
mix ingest.demo
```

With the functions unwritten, the demo runs the chunk step, then every job **gives
up** and the resources stay `pending` — and it prints the reason:

```
   drain: %{discard: 2, success: 0, failure: 8}
   ↳ a job gave up. last error: ** (RuntimeError) TODO: implement advance/1 ...
   Photosynthesis   status=pending attempts=0
```

That's your starting line. (Postgres not on defaults? Set `PGUSER`/`PGPASSWORD`/
`PGHOST` — see `config/config.exs`.)

### 2. Implement `advance/1` and `retry_target/1`

Both are pure `status → status` lookups; each is **three one-line function
clauses**. The docstrings give you the exact arrows:

- `advance/1` — move forward one checkpoint after a stage succeeds
  (`:pending → :chunked → :embedded → :indexed`).
- `retry_target/1` — given the stage that failed (`:chunk` / `:embed` / `:store`),
  which checkpoint to rewind to and re-run from.

Delete the `raise "TODO..."` in each and add the clauses. If you've never written
Elixir: `def advance(:pending), do: :chunked` is a complete function clause —
"when called with `:pending`, return `:chunked`." Add one line per arrow.

**Stuck? Ask Claude** — especially for anything Elixir-syntax, not just the logic.

### 3. Check your work

`mix ingest.demo` should now reproduce the worked example: both articles reach
`status=indexed attempts=2`, `discard: 0`, and no "gave up" line. Re-run it —
because the demo resets each time, you get the same clean run.

### 4. Observe (fill in)

- **Durability.** After a run, open `psql` (`psql m7_pipeline_dev`) and
  `SELECT title, status, attempt_count FROM resources;`. The state lived in
  Postgres the whole time, not in memory. Why does that matter if the server
  crashes mid-pipeline? _fill in_
- **Retry budget.** The worker sets `max_attempts: 5`, and embed fails twice.
  Change the flaky step in `worker.ex` to fail on `attempt <= 5` instead of `<= 2`
  and re-run. What state do the resources end in, and what does the drain summary
  say now? _fill in_ &nbsp; _(you're forcing it past the retry budget.)_
- **Rewind target.** You wrote `retry_target(:embed) => :chunked`. What would break
  (or get wasteful) if it returned `:pending` instead? What about `:embedded`?
  _fill in_

There's no git tag for this satellite — you're done when step 3 passes and the
observations are filled.

---

## Concepts to capture (your words → `glossary.md`)

- background job / job queue _(why run indexing off the request path?)_
- worker _(what does a worker do with a job?)_
- state machine / checkpoint _(why store `status` in Postgres instead of a variable?)_
- retry / max_attempts / backoff _(what happens when a stage fails? when does it give up?)_
- idempotency, again _(two places it shows up here — the content-hash gate AND
  re-running a finished resource. How is this the same idea as Modules 3 and 6?)_

Ask Claude to check your wording if you're unsure a definition is right.

---

## Optional — see it in production (5 min)

Only after your demo passes. This module maps almost one-to-one onto `chunky-kong`
— you built a miniature of the real search-sync pipeline. Three files:

- **The pure state machine you just wrote** →
  `lib/instinct/search/universal/sync/resource_pipeline.ex`
  - **Notice:** its moduledoc (lines 2–5) is _"Pure functions for resource state
    transitions. Returns changesets — no database calls, no side effects."_ — the
    exact split you used. And `retry_target/1` (lines 188–191) is your function,
    grown up: `retry_target(:extracting) => :pending`,
    `retry_target(:embedding) => :extracted`, `retry_target(:storing) =>
    :extracted` — rewind to the last durable checkpoint, same as yours.
    `@max_attempts` is `5` (line 9), same as your worker.
- **The state enum** → `lib/instinct/search/universal/sync/resource.ex`
  - **Notice:** line 13, `@statuses [:pending, :extracting, :extracted, :indexed,
    :failed, :evicting, :skipped]` — your four-status machine with a few more
    states (real life needs `:evicting` for deletes and `:skipped` for
    no-indexable-content). Line 14, `@failed_stages [:extracting, :embedding,
    :storing]`, is your `failed_stage`. Same shape, persisted the same way.
- **The idempotency gate** →
  `lib/instinct/search/universal/sync/workers/intake_worker.ex`
  - **Notice:** it `use Oban.Worker, ... unique: [...]` (lines 18–20) so duplicate
    intakes dedupe, and in `upsert_resource/5` the clause that matches when both
    hashes are unchanged (lines 89–90) returns `{:ok, resource.version, false}` —
    that `false` means "not changed," so no pipeline job is enqueued. Your demo's
    `:unchanged` path is this exact decision.

---

## Open questions

- **Why a database-backed state machine instead of just a queue?** Oban already
  retries jobs. What does storing `status` on the *resource* buy you that the job
  record alone doesn't? _(Hint: the job is gone after it succeeds; the resource
  isn't. Think about a later edit, or auditing what's indexed.)_
- **Your pipeline runs one resource per job, top to bottom.** chunky-kong splits it
  across several workers (extraction, then batched indexing) connected as a
  workflow. What do you gain by breaking the stages into separate jobs — and what
  gets harder? _(Think: batching embeds across documents, back-pressure, partial
  failure.)_
- **The version guard.** chunky-kong carries a `version` and rejects a stage
  completion if the entity changed underneath it mid-pipeline (a "stale" guard).
  What race does that prevent that your simpler content-hash reset does not?
- _fill in your own_
