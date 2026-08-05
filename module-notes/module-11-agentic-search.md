# Module 11 — Agentic Search

**Concepts:** ReAct loop, tool use, multi-step retrieval, self-correction, search planner as agent, when to stop iterating.
**Time spent:** _fill in_
**Date completed:** _fill in_

## What I read

- [ ] Anthropic "Building Effective Agents"
- [ ] Plumbs_assistant `agent.ts` and `tools.ts`

## Codebase walk

- `merlin/src/services/agents/plumbs_assistant/agent.ts` — _orchestration loop_
- `merlin/src/services/agents/plumbs_assistant/tools.ts` — _tool schemas_

## Exercises

### 1. ReAct loop with 3 tools

Tools defined:

- `search_fts(query: str)` → top 10 article titles
- `search_vector(query: str)` → top 10 chunks
- `read_full_article(title: str)` → full article text

- Anthropic SDK loop implemented: _yes/no_
- Stopping condition: _fill in_

### 2. Multi-hop test queries

Example: _"What language did the country that won FIFA World Cup 1998
colonize the most countries with?"_

| Query | # tool calls | Final answer | Correct? | Trace path |
| ----- | ------------ | ------------ | -------- | ---------- |
|       |              |              |          |            |

### 3. Single-pass RAG vs. agentic — 10 queries

| Metric          | RAG  | Agentic |
| --------------- | ---- | ------- |
| Avg latency     |      |         |
| Avg cost ($)    |      |         |
| Avg correctness |      |         |

## Mini-project: Agentic Wikipedia researcher (THIRD PORTFOLIO DEMO)

- Repo: `exercises/module-11/`
- Outputs: answer + citations + reasoning transcript
- Live URL: _fill in_
- Demo screenshot: `exercises/module-11/demo.png`

## Security checklist

- [ ] Anthropic API key in env var
- [ ] Tool input sanitization (no prompt injection in retrieved content)
- [ ] Iteration cap to prevent runaway loops
- [ ] Cost cap per request

## Glossary additions

## Open questions
