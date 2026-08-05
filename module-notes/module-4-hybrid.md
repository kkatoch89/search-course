# Module 4 — Hybrid Search & Reranking

**Concepts:** score normalization, weighted fusion, RRF, over-fetching, when hybrid helps and hurts.
**Time spent:** _fill in_
**Date completed:** _fill in_

## What I read

- [ ] Cormack et al. "Reciprocal Rank Fusion outperforms Condorcet"

## Codebase walk

- `query/executor/retrieval.ex` — _hybrid eligibility check_
- `query/reranker.ex` — _weighted score merge formula_

## Exercises

### 1. Weighted fusion on Module 1 + 2 outputs

| Query | FTS top-1 | Vec top-1 | 0.5/0.5 | 0.7/0.3 | 0.3/0.7 |
| ----- | --------- | --------- | ------- | ------- | ------- |
|       |           |           |         |         |         |

### 2. RRF vs. weighted fusion

Observation: _fill in_

## Mini-project: hybrid CLI over full 226k Wikipedia (FIRST PORTFOLIO DEMO)

- Repo: `exercises/module-4/`
- Command: `python search.py --mode hybrid "world's largest dam"`
- 10 queries where hybrid beat FTS alone: _list_
- Side-by-side screenshot for portfolio: `exercises/module-4/demo.png`

## Glossary additions

## Open questions
