# Capstone — WikiSearch

A hybrid + AI-augmented search + RAG engine over **full Simple English
Wikipedia (~226k articles)** plus a second namespace, mirroring chunky-kong
+ merlin in miniature.

**Time spent:** _fill in_
**Date completed:** _fill in_

## Architecture decisions

- **Second namespace:** _your notes / arXiv / Stack Exchange dump_
- **FTS backend:** _SQLite FTS5 / Turbopuffer_
- **Vector backend:** _pgvector / Turbopuffer_
- **Embedder (production demo):** _OpenAI text-embedding-3-small_
- **Embedder (training set, optional):** _domain-tuned MiniLM from Module 12_
- **Cross-encoder:** _ms-marco-MiniLM-L-6-v2_
- **LLM (RAG + agent + judge):** _claude-sonnet-4-6 / claude-opus-4-7_
- **Job queue:** _RQ / Celery / BullMQ / Oban_

## Architecture diagram

_Paste image. Steal layout from chunky-kong's universal/README.md._

## Requirements checklist

### Indexing

- [ ] Multi-namespace (Wikipedia + second corpus)
- [ ] FTS index
- [ ] Vector index
- [ ] Background ingestion pipeline with state machine
- [ ] Content-hash idempotency

### Retrieval

- [ ] Planner / Executor / Hydrator separation
- [ ] Hybrid query path (FTS + vector + score fusion)
- [ ] Cross-encoder reranking stage
- [ ] LLM query understanding layer (paraphrase or HyDE)
- [ ] Agentic mode for multi-hop queries
- [ ] excludeIds pagination

### Generation

- [ ] RAG endpoint with citations (article + section)
- [ ] Agentic endpoint with reasoning transcript

### Evaluation

- [ ] ≥30 hand-labeled (query, ideal-doc) pairs
- [ ] Recall@5 / MRR / NDCG@10 reported per stage (FTS / hybrid / +rerank /
      +query understanding / agentic)
- [ ] LLM-as-judge faithfulness scoring on RAG outputs
- [ ] *Stretch:* domain-tuned embeddings on a slice with before/after numbers

## Portfolio deliverables

- [ ] Live demo URL: _fill in_
- [ ] Public GitHub repo: _fill in_
- [ ] Blog post / writeup with eval table per stage: _fill in_
- [ ] Post-mortem comparing my choices to chunky-kong: _link to section below_

## Production-readiness notes

- [ ] All API keys in env vars (Anthropic, OpenAI, Turbopuffer)
- [ ] Iteration cap on agentic mode (cost protection)
- [ ] Rate limiting on public endpoint
- [ ] No customer / Instinct data — Wikipedia only

## Post-mortem

### What I'd do the same as chunky-kong

### What I'd do differently

### What surprised me

### What I'd build next
