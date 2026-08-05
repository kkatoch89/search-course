# Module 5 — Cross-Encoder Reranking

**Concepts:** bi-encoder vs. cross-encoder, late interaction, two-stage retrieval, MS MARCO models, latency/quality tradeoff.
**Time spent:** _fill in_
**Date completed:** _fill in_

## What I read

- [ ] Sentence-Transformers cross-encoder docs
- [ ] "Pretrained Transformers for Text Ranking" (rerank sections)

## Codebase walk

Not yet in chunky-kong. Where would I insert a rerank step?

- File I'd modify: `query/executor/retrieval.ex` — _which line, why_
- Latency budget: _ms I'd allocate to rerank_

## Exercises

### 1. Rerank 20 hybrid results

- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Top-5 before/after on 5 queries — observations: _fill in_

### 2. Latency on my machine

- ms per (query, doc) pair: _fill in_
- ms for top-50 rerank: _fill in_

## Mini-project: --rerank flag on Module 4 CLI

- Repo: `exercises/module-5/`
- Pipeline: hybrid retrieve top-50 → cross-encoder rerank → return top-10
- Updated portfolio screenshot showing FTS / hybrid / hybrid+rerank: `exercises/module-5/demo.png`
- Quality delta on my 30 labeled queries: _fill in_

## Reflection

When is rerank worth the latency? When isn't it?

## Glossary additions

## Open questions
