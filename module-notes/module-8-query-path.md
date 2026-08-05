# Module 8 — Query Path Patterns

**Concepts:** Planner/Executor/Hydrator separation, identity gates, over-fetch + rerank, excludeIds pagination, highlighting, snippets.
**Time spent:** _fill in_
**Date completed:** _fill in_

## Codebase walk

- `query/planner.ex` and `query/plan.ex`
- `query/executor/gates.ex` and `ns/patients/gates.ex`
- `query/hydrator.ex`

## Exercises

### 1. Add a `:random_sample` sort mode (in a fork — not for ship)

Layers it touched:

- [ ] `request.ex` — accept new sort value
- [ ] `executor/ranking.ex` — handle in rank_by selection
- [ ] `hydrator.ex` — input-order preservation
- [ ] _other_

### 2. excludeIds pagination on local search CLI

- Repo: `exercises/module-8/`
- Cursor version: _yes/no_
- excludeIds version: _yes/no_
- Tradeoffs observed: _fill in_

## Reflection: why is hydration separate?

_Write 1–2 paragraphs on what breaks if you fold hydration into the executor._

## Glossary additions

## Open questions
