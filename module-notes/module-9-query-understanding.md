# Module 9 — LLM Query Understanding

**Concepts:** query rewriting, query expansion, HyDE, multi-query retrieval, query routing/classification.
**Time spent:** _fill in_
**Date completed:** _fill in_

## What I read

- [ ] HyDE paper (Gao et al.)
- [ ] "Step-Back Prompting" intro

## Codebase walk

- `merlin/src/services/agents/plumbs_assistant/prompts.ts` — _any query reshaping today?_

## Exercises

### 1. Multi-query retrieval via paraphrase

- 10 hard queries → Claude generates 3 paraphrases each
- Run all 4 versions through hybrid → merge via RRF
- Recall@5 vs. single-query baseline: _fill in_

### 2. HyDE

- Claude generates a hypothetical Wikipedia article for each query
- Embed the hallucination, search by vector
- Recall@5 vs. embedding the raw query: _fill in_
- When did HyDE win? When did it lose?

### 3. Query router

Claude classifies queries as `factual` / `exploratory` / `comparison`.

| Query | Predicted class | Routed to                | Result quality |
| ----- | --------------- | ------------------------ | -------------- |
|       |                 | _e.g., FTS only / hybrid_ |                |

## Mini-project: Query understanding layer

- Repo: `exercises/module-9/`
- Wraps Module 5 (hybrid + rerank) engine
- 5 hard queries where rewriting clearly helps — paste before/after results

## Cost tracking

- Avg Claude tokens per query rewrite: _fill in_
- Latency added: _ms_

## Glossary additions

## Open questions
