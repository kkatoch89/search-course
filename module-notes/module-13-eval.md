# Module 13 — Evaluation & Observability

**Concepts:** offline eval (recall@k, precision@k, MRR, NDCG@10), labeled
query sets, **LLM-as-judge**, judge prompt design, judge bias, A/B safety,
LLM tracing.
**Time spent:** _fill in_
**Date completed:** _fill in_

## What I read

- [ ] BEIR benchmark intro
- [ ] "Judging LLM-as-a-Judge" (Zheng et al.)
- [ ] Anthropic evaluator-optimizer pattern in "Building Effective Agents"

## Codebase walk

- `merlin/src/services/embeddings.ts` — _Datadog LLMObs tracing_

## Exercises

### 1. Full pipeline comparison on 30 labeled queries

- File: `data/eval_queries.jsonl`

| Mode                               | Recall@5 | MRR | NDCG@10 |
| ---------------------------------- | -------- | --- | ------- |
| FTS                                |          |     |         |
| Vector                             |          |     |         |
| Hybrid                             |          |     |         |
| Hybrid + cross-encoder rerank      |          |     |         |
| + LLM query understanding          |          |     |         |
| Agentic                            |          |     |         |

### 2. Sweep weights + chunk size

| Chunk size | FTS/Vec weight | Recall@5 | NDCG@10 |
| ---------- | -------------- | -------- | ------- |
| 256        | 0.5/0.5        |          |         |
| 512        | 0.5/0.5        |          |         |
| 1024       | 0.5/0.5        |          |         |
| 512        | 0.7/0.3        |          |         |
| 512        | 0.3/0.7        |          |         |

Plot for portfolio: `exercises/module-13/sweep.png`

### 3. LLM-as-judge for RAG outputs

- Judge prompt drafted in: `exercises/module-13/judge_prompt.md`
- 30 RAG outputs scored on (faithfulness, relevance, citation quality), 1–5.

| Metric          | Avg score | Disagreement vs. my labels |
| --------------- | --------- | -------------------------- |
| Faithfulness    |           |                            |
| Relevance       |           |                            |
| Citation        |           |                            |

### 4. Where the judge disagreed

_Pick 3 cases where Claude-as-judge and your manual label diverged.
Hypothesize why. What does that say about deploying LLM-as-judge in prod?_

## Glossary additions

## Open questions
