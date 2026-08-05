# Module 10 — RAG with Search

**Concepts:** retrieval-augmented generation, grounding, agent tool use, citation, hallucination tradeoffs.
**Time spent:** _fill in_
**Date completed:** _fill in_

## Codebase walk

- `merlin/src/services/agents/plumbs_assistant/agent.ts` — _orchestration_
- `merlin/src/services/agents/plumbs_assistant/tools.ts` — _tool definitions_
- `merlin/src/services/agents/plumbs_assistant/prompts.ts` — _system prompt_

## Exercises

### 1. Tiny Wikipedia RAG, 5 factual questions

| Question | Retrieved chunks (titles) | Claude answer | Cited? | Correct? |
| -------- | ------------------------- | ------------- | ------ | -------- |
|          |                           |               |        |          |

### 2. Retrieval mode comparison

| Mode    | Avg cited correctly (out of 5) |
| ------- | ------------------------------ |
| FTS     |                                |
| Vector  |                                |
| Hybrid  |                                |

## Mini-project: "Ask Wikipedia" web app (SECOND PORTFOLIO DEMO)

- Repo: `exercises/module-10/`
- Stack: _Streamlit / Next.js / FastAPI + ?_
- Live URL: _fill in once deployed_
- Forces citation of article + section: _yes/no_
- Screenshot for portfolio: `exercises/module-10/demo.png`

## Security checklist

- [ ] Claude API key in env var (not committed)
- [ ] Rate limiting on the demo endpoint
- [ ] No customer / Instinct data in prompts (Wikipedia only)

## Glossary additions

## Open questions
