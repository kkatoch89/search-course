# Module 7 — Ingestion Pipeline & State Machines

**Concepts:** background jobs, queue concurrency, idempotent workers, version guards, state transitions, eviction.
**Time spent:** _fill in_
**Date completed:** _fill in_

## Codebase walk

- `sync/resource_pipeline.ex` — _state machine_
- `sync/workers/intake_worker.ex` — _hash-detect changes, route_
- `sync/workers/fts_sync_worker.ex` — _entity-level FTS upsert_
- `sync/workers/index_batch_worker.ex` — _batch embed + vector upsert_
- `sync/workers/eviction_worker.ex` — _stale chunk removal_

## Exercises

### 1. State diagram (drawn from code)

_Paste image or ASCII art:_

```
pending → ... → indexed
   ↓
  failed
```

Guards on each transition: _fill in_

### 2. Mid-extraction edit trace

What happens when a chart doc is edited after extraction starts but before
indexing finishes?

_Walk through the version-guard checks in your own words._

## Mini-project: 3-stage pipeline (Wikipedia ingestion)

- Repo: `exercises/module-7/`
- Job queue used: _RQ / Celery / BullMQ / Oban_
- Demo: re-run on same articles → 0 work (idempotent). _yes/no_
- Bonus: stale-claim reaper. _done?_

## Glossary additions

## Open questions
