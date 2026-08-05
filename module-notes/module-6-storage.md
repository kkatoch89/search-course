# Module 6 — Storage: Turbopuffer & pgvector

**Concepts:** namespaces as partitioning, multi-tenant boundaries, upsert semantics, filter expressions.
**Time spent:** _fill in_
**Date completed:** _fill in_

## Codebase walk

- `sync/namespace.ex` — _market-scoped naming_
- `clients/turbopuffer/filters.ex` — _filter compilation_

## Exercises

### 1. Personal Turbopuffer namespace, 1k articles

- Namespace name: _your_handle_wiki_demo_
- Attributes used: `category`, `length_bucket`
- Sample filter + rank_by query: _paste_

### 2. Latency comparison

| Query                               | Latency (full scan) | Latency (filter-narrowed) |
| ----------------------------------- | ------------------- | ------------------------- |
| `"einstein"` no filter              |                     |                           |
| `"einstein"` + `category="Science"` |                     | _expected lower_          |

## Reflection: pgvector vs. Turbopuffer

- Latency: _fill in_
- Ops burden: _fill in_
- Cost: _fill in_
- Joins to other Postgres data: _fill in_

## Glossary additions

## Open questions
