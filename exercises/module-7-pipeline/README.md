# Module 7 — Ingestion Pipeline: Oban + Ecto state machine (satellite, **Elixir**)

The one Elixir module. A tiny but real **background ingestion pipeline** — the
shape production uses to keep a search index in sync — built on the same stack as
Instinct's `chunky-kong`: **Oban** (Postgres-backed background jobs) + **Ecto**
(a Postgres-backed state machine) + **retries**.

It doesn't recompute vectors (you did the real chunk/embed/store in Modules 3/2/6).
The chunk/embed/store steps are **stubbed** — this module is about the *pipeline*:
durable state, retries, and idempotency.

**Full walkthrough:** [`module-notes/module-7-pipeline.md`](../../module-notes/module-7-pipeline.md)

## Setup

Needs **Elixir** (~1.16) and a local **Postgres** you can create databases in.

```bash
mix setup          # deps.get + ecto.create + ecto.migrate
mix ingest.demo    # runs the pipeline; stops at the first TODO until you implement it
```

If your Postgres uses a non-default user/password, set `PGUSER` / `PGPASSWORD` /
`PGHOST` / `PGDATABASE` (see `config/config.exs`). To wipe and start over:
`mix ecto.reset`.

## Files

| file | role |
| ---- | ---- |
| `lib/ingest/resource_pipeline.ex` | **you write this** — the pure state machine: `advance/1` + `retry_target/1` |
| `lib/ingest/resource.ex` | plumbing — the Ecto schema (statuses, failed_stage, attempt_count, content_hash) |
| `lib/ingest/worker.ex` | plumbing — the Oban worker: runs stubbed stages, calls your functions, retries on failure |
| `lib/ingest/demo.ex` | plumbing — resets, intakes articles, drains the queue, narrates every transition |
| `config/config.exs`, `priv/repo/migrations/` | plumbing — Repo + Oban config and tables |

**Done when** `mix ingest.demo` walks two articles to `status=indexed` (surviving
the deliberately flaky embed step via retries), then shows that re-intaking
unchanged content is a no-op while an edit re-runs the pipeline.

## Note

This is a **satellite** — it doesn't touch the Python `wikisearch` engine, so
there's no `end-of-m7` tag. It's a standalone Elixir project. All data is the few
public sample articles in `demo.ex`; nothing here talks to a real embedder or
vector store, and no credentials are involved.
