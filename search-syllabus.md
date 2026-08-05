# Search & Retrieval Learning Syllabus

A self-paced course on full-text + semantic + AI-augmented search, grounded
in the chunky-kong (`lib/instinct/search/universal/`) and merlin
(`src/services/`) implementations.

**Pacing:** ~5–8 hrs/week, total ~16 weeks.
**Per module:** Concepts → Read → Codebase walk → Exercises → Mini-project.

---

## Course Data: Simple English Wikipedia

A single corpus is used across the whole course so the capstone is a natural
culmination, not a fresh start.

- **Primary corpus:** Simple English Wikipedia (~226k articles)
  - Hugging Face: `wikimedia/wikipedia`, config `20231101.simple`
  - Schema: `id`, `url`, `title`, `text`
- **Early modules (1–3):** subsample to **~5k random articles** so prototyping
  stays fast and free.
- **Modules 4+:** full ~226k set. Embedding cost with
  `text-embedding-3-small`: ~$2–5.
- **Capstone:** full set + a second namespace of your choice to demo
  multi-namespace architecture.

See [`data-setup.md`](./data-setup.md) for download + subsample scripts.

> **Cost tip:** for exercises, swap OpenAI for a local embedder
> (`sentence-transformers/all-MiniLM-L6-v2`, 384-dim, free, runs on your
> laptop). Save OpenAI for the capstone demo.

---

## Module 0 — Orientation (½ week)

**Goal:** see the whole system before zooming in.

- **Read:** `chunky-kong/lib/instinct/search/universal/README.md` end-to-end.
  Don't try to understand it all — just absorb vocabulary.
- **Walk:** trace one query call path from `universal.ex` → `planner.ex` →
  `executor.ex` → `hydrator.ex`. Don't read implementations, just note
  function signatures.
- **Exercise:** in your own words, write a 1-paragraph answer to "what
  happens when a user types 'amoxicillin' into search?"
- **Output:** a glossary file (markdown) you'll grow as you go: namespace,
  gate, chunk, BM25, ANN, hybrid, etc.

---

## Module 1 — Full-Text Search & BM25 (1 week)

**Concepts:** inverted index, tokenization, stemming, term frequency, IDF,
BM25 scoring, prefix matching.

- **Read:**
  - Elastic's "what is BM25" intro (any blog post, ~10 min)
  - Turbopuffer FTS docs: query, rank_by, BM25
- **Codebase walk:**
  - `lib/instinct/search/universal/clients/fts_store/turbopuffer.ex`
  - `lib/instinct/search/universal/clients/turbopuffer/ranking.ex`
- **Exercises:**
  1. Compute BM25 by hand for 3 toy docs and a 2-word query.
  2. Run two FTS queries against your local chunky-kong: one short word, one
     with a typo. Note which docs come back and why.
- **Mini-project:** Build a tiny CLI that indexes the **5k Simple English
  Wikipedia subset** and ranks queries with BM25.

---

## Module 2 — Embeddings & Vector Search (1 week)

**Concepts:** embeddings, dimensionality, cosine similarity vs. distance,
ANN vs. exact search, recall/latency tradeoff.

- **Read:** OpenAI embeddings guide; HNSW high-level overview.
- **Codebase walk:**
  - `merlin/src/services/embeddings.ts`
  - `merlin/src/services/storage/plumbsVectorSearch.ts`
  - `chunky-kong/.../clients/vector_store/turbopuffer.ex`
- **Exercises:**
  1. Embed 200 Wikipedia titles with `all-MiniLM-L6-v2`. Pairwise cosine in a
     notebook. Confirm semantic clusters.
  2. Visualize embeddings in 2D via PCA or UMAP.
- **Mini-project:** "Search by similarity" over the **5k Wikipedia subset**.
  Demo query: `"a planet that has rings"` → expects Saturn.

---

## Module 3 — Chunking & Text Extraction (½ week)

**Concepts:** chunking strategies, token-aware splitting, overlap,
section-based vs. recursive splitting, content hashing, idempotency.

- **Codebase walk:**
  - `chunky-kong/.../sync/chunker.ex` (500 tokens, 50 overlap)
  - `merlin/src/services/plumbsIngestion.ts` (section-based)
  - `chunky-kong/.../sync/digest.ex` (content hashing)
- **Exercises:**
  1. Pick 10 long Wikipedia articles. Chunk three ways: 500 tokens / 500 with
     overlap / by section heading. Compare retrieval on 5 queries.
  2. Hash → edit one paragraph → re-hash → confirm digest changed; re-hash
     unchanged → confirm idempotent.
- **Mini-project:** Chunker + content hash on the 5k subset. Re-running on
  unchanged input → 0 re-embed calls.

---

## Module 4 — Hybrid Search & Score Fusion (1 week)

**Concepts:** score normalization, weighted fusion, RRF, over-fetching, when
hybrid helps and when it hurts.

- **Read:** Cormack et al. "Reciprocal Rank Fusion outperforms Condorcet"
  (skim).
- **Codebase walk:**
  - `query/executor/retrieval.ex` (hybrid eligibility)
  - `query/reranker.ex` (weighted score merge)
- **Exercises:**
  1. Combine Module 1 + 2 outputs: normalize scores, fuse with weights
     0.5/0.5, 0.7/0.3, 0.3/0.7. Tabulate which queries change rank.
  2. Implement RRF; compare to weighted fusion on the same dataset.
- **Mini-project:** Hybrid CLI over **full 226k Wikipedia** with
  `--mode fts | hybrid` flags. **First portfolio demo** — link from your site.

---

## Module 5 — Cross-Encoder Reranking (1 week)

**Concepts:** bi-encoder vs. cross-encoder, late interaction, two-stage
retrieval (retrieve → rerank), MS MARCO trained models, latency/quality
tradeoff.

> The weighted fusion in Module 4 is fast but blunt. Cross-encoders read
> query + doc together — much better quality on hard queries, at higher
> latency. This is the standard production rerank stage.

- **Read:**
  - Sentence-Transformers cross-encoder docs
  - "Pretrained Transformers for Text Ranking: BERT and Beyond" (skim
    rerank sections)
- **Codebase walk:** not yet in chunky-kong. Reflect on where in
  `query/executor/retrieval.ex` you'd insert a rerank step. Could this be a
  ticket you eventually file?
- **Exercises:**
  1. Take 20 hybrid results from Module 4. Rerank with
     `cross-encoder/ms-marco-MiniLM-L-6-v2`. Compare top-5 before/after.
  2. Measure latency: ms per (query, doc) pair on your machine.
- **Mini-project:** Add a `--rerank` flag to the Module 4 CLI: hybrid
  retrieve top-50 → cross-encoder rerank → return top-10. Update your
  portfolio screenshot to show three modes (FTS / hybrid / hybrid+rerank).

---

## Module 6 — Storage: Turbopuffer & pgvector (½ week)

**Concepts:** namespaces as partitioning, multi-tenant boundaries, write
semantics (upsert + version), filter expressions on indexed attributes.

- **Codebase walk:**
  - `lib/instinct/search/universal/sync/namespace.ex`
  - `lib/instinct/search/universal/clients/turbopuffer/filters.ex`
- **Exercises:**
  1. Create a personal Turbopuffer namespace. Upsert 1k Wikipedia articles
     with attributes (`category`, `length_bucket`). Run filter + rank_by.
  2. Compare query latency: full namespace scan vs. filter-narrowed.
- **Reflection:** when would you use pgvector vs. Turbopuffer? Short doc on
  tradeoffs (latency, ops, cost, joins).

---

## Module 7 — Ingestion Pipeline & State Machines (1 week)

**Concepts:** background jobs, queue concurrency tuning, idempotent workers,
version guards, state transitions, failure isolation, eviction.

- **Codebase walk:**
  - `lib/instinct/search/universal/sync/resource_pipeline.ex`
  - `sync/workers/intake_worker.ex` → `fts_sync_worker.ex` →
    `index_batch_worker.ex` → `eviction_worker.ex`
- **Exercises:**
  1. Draw the state diagram from the pipeline code: which transitions, which
     guards.
  2. Trace what happens when an article is edited mid-extraction. Where does
     the version guard fire?
- **Mini-project:** 3-stage pipeline (fetch Wikipedia → chunk + embed →
  index) using a real job queue. Retries + content-hash idempotency. Demo:
  re-running on the same articles does zero work.

---

## Module 8 — Query Path Patterns (1 week)

**Concepts:** Planner/Executor/Hydrator separation, identity gates, over-fetch
+ rerank, pagination via excludeIds (vs. cursors), highlighting, snippet
generation.

- **Codebase walk:**
  - `query/planner.ex` and `query/plan.ex`
  - `query/executor/gates.ex` and `ns/patients/gates.ex`
  - `query/hydrator.ex`
- **Exercises:**
  1. Add a new sort mode (e.g., `:random_sample`) end-to-end in a fork.
     Don't ship — just learn the layers.
  2. Implement `excludeIds` pagination on your local search CLI. Compare
     with cursor-based.
- **Reflection:** why is hydration a separate phase? What breaks if you fold
  it into the executor?

---

## Module 9 — LLM Query Understanding (1 week)

**Concepts:** query rewriting, query expansion via LLM, HyDE (Hypothetical
Document Embeddings), multi-query retrieval, query routing/classification.

> A great retriever can't fix a poorly-phrased query. LLMs let you reshape
> the query before retrieval — paraphrase, expand, or hallucinate-then-search.

- **Read:**
  - HyDE paper (Gao et al., "Precise Zero-Shot Dense Retrieval without
    Relevance Labels") — short, very readable
  - "Step-Back Prompting" intro
- **Codebase walk:** check `merlin/src/services/agents/plumbs_assistant/prompts.ts`
  to see if any query reshaping happens today.
- **Exercises:**
  1. Take 10 hard queries. Use Claude to generate 3 paraphrases each. Run
     all 4 through hybrid search; merge via RRF. Compare vs. single-query.
  2. Implement HyDE: ask Claude to write a hypothetical Wikipedia article
     answering the query, embed *that*, search by vector. Compare to direct
     query embedding.
  3. Build a query router with Claude: classify as "factual" / "exploratory"
     / "comparison", route to different retrieval strategies.
- **Mini-project:** Wrap your Module 5 (hybrid + rerank) engine with an LLM
  query understanding layer. Demo on 5 hard queries where rewriting clearly
  helps.

---

## Module 10 — RAG with Search (1 week)

**Concepts:** retrieval-augmented generation, grounding, citation, prompt
construction, hallucination tradeoffs, context-window budgeting.

- **Codebase walk:**
  - `merlin/src/services/agents/plumbs_assistant/{agent.ts, tools.ts, prompts.ts}`
- **Exercises:**
  1. Tiny RAG over Wikipedia: top-3 chunks → Claude prompt with citation
     instructions → answer 5 factual questions. Measure groundedness manually.
  2. Repeat with FTS-only / vector-only / hybrid retrieval. Which produces
     better-cited answers?
- **Mini-project:** "Ask Wikipedia" web app (Streamlit / Next.js) using your
  full search stack. Force citation of article + section. **Second portfolio
  demo** — host it.

---

## Module 11 — Agentic Search (1 week)

**Concepts:** ReAct loop, tool use, multi-step retrieval, self-correction,
search planner as agent, when to stop iterating, tradeoffs vs. single-pass
RAG.

> Single-pass RAG can't answer multi-hop questions. Agents can search,
> read, reformulate, and search again. Production-grade pattern that
> mirrors merlin's `plumbs_assistant`.

- **Read:**
  - Anthropic "Building Effective Agents" guide
  - Plumbs_assistant `agent.ts` and `tools.ts` in merlin
- **Codebase walk:**
  - `merlin/src/services/agents/plumbs_assistant/agent.ts` (orchestration)
  - `merlin/src/services/agents/plumbs_assistant/tools.ts` (tool definitions)
- **Exercises:**
  1. Define 3 tools for Claude: `search_fts(query)`, `search_vector(query)`,
     `read_full_article(title)`. Wire up a ReAct loop with the Anthropic SDK.
  2. Test on multi-hop queries (e.g., "What language did the country that
     won FIFA World Cup 1998 colonize the most countries with?") that
     require chained retrieval.
  3. Compare cost + latency: single-pass RAG vs. agentic on 10 queries.
- **Mini-project:** "Agentic Wikipedia researcher" — takes a complex
  question, iterates search → read → search → answer with citations *and*
  a transcript of its reasoning. **Third portfolio demo.**

---

## Module 12 — Domain-Tuned Embeddings (1.5 weeks)

**Concepts:** contrastive learning, triplet / InfoNCE loss, hard-negative
mining, fine-tuning sentence-transformers, when fine-tuning helps and when
it doesn't, evaluating embedding improvements.

> Off-the-shelf embeddings are a generalist's tool. Fine-tuning on your
> domain's queries can lift recall meaningfully — and shows real ML chops on
> a resume.

- **Read:**
  - Sentence-Transformers training docs
  - "Sentence-BERT" paper (skim)
- **Codebase walk:** none — production uses off-the-shelf embeddings.
  Reflect on whether Instinct's veterinary corpus would benefit from
  domain-tuned embeddings.
- **Exercises:**
  1. Build a training set from your eval queries: (query, positive doc, hard
     negative) triplets. Mine hard negatives from BM25 high-scoring but
     irrelevant docs.
  2. Fine-tune `all-MiniLM-L6-v2` for 3 epochs with
     `MultipleNegativesRankingLoss`.
  3. Re-run Module 13 eval with fine-tuned embeddings. Plot recall@5 / NDCG
     delta.
- **Mini-project:** Document the experiment in `exercises/module-12/` —
  training script, before/after eval, and a writeup ("Did it help? Why?
  When would I do this in production?"). Serious resume piece.

---

## Module 13 — Evaluation & Observability (1 week)

**Concepts:** offline eval (recall@k, precision@k, MRR, NDCG@10), labeled
query sets, **LLM-as-judge** for groundedness/faithfulness, judge prompt
design, judge bias, A/B safety, LLM tracing, regression detection.

- **Read:**
  - BEIR benchmark intro
  - "Judging LLM-as-a-Judge" (Zheng et al.)
  - Anthropic's evaluator-optimizer pattern in "Building Effective Agents"
- **Codebase walk:** Datadog LLMObs wiring in
  `merlin/src/services/embeddings.ts`.
- **Exercises:**
  1. Hand-label 30 (query, ideal-Wikipedia-article) pairs. Compute recall@5,
     MRR, NDCG@10 for FTS / vector / hybrid / hybrid+rerank / +query
     understanding / +agentic. Tabulate.
  2. Sweep weights and chunk sizes. Plot recall@5 vs. config.
  3. Write a Claude prompt that grades RAG answers on (faithfulness,
     relevance, citation quality), 1–5 scale. Run on 30 RAG outputs.
  4. Compare LLM-judge scores vs. your manual labels. Where does the judge
     disagree? What does that tell you?
- **Output:** evaluation report figure for portfolio writeup.

---

## Capstone (2 weeks)

**Build:** "WikiSearch" — a hybrid + AI-augmented search + RAG engine over
**full Simple English Wikipedia (~226k articles)** plus a second namespace.
End-to-end mirror of chunky-kong + merlin in miniature.

### Requirements

- **Multi-namespace:** Wikipedia + a second corpus (notes / arXiv / SE dump)
- **FTS** via SQLite FTS5 *or* Turbopuffer
- **Vectors** via pgvector *or* Turbopuffer
- **Background ingestion pipeline** with state machine + content hashing
- **Two-stage retrieval:** hybrid → cross-encoder rerank
- **LLM query understanding layer** (paraphrase or HyDE)
- **Agentic mode** for complex multi-hop queries
- **RAG endpoint** with citations
- **Eval harness** with ≥30 labeled queries reporting recall@5, MRR,
  NDCG@10 + LLM-as-judge faithfulness scores
- *Optional stretch:* domain-tuned embeddings on a slice of your eval set,
  with before/after numbers

### Portfolio deliverables

1. Live demo URL
2. Public GitHub repo with README explaining architecture
3. Blog post / writeup comparing each retrieval stage with real numbers
4. Post-mortem comparing your design to chunky-kong's

---

## Suggested cadence

| Week  | Module(s)                          |
| ----- | ---------------------------------- |
| 1     | 0 + 1                              |
| 2     | 2                                  |
| 3     | 3 + 4 (start)                      |
| 4     | 4 (finish) + 5 (start)             |
| 5     | 5 (finish)                         |
| 6     | 6 + 7 (start)                      |
| 7     | 7 (finish)                         |
| 8     | 8                                  |
| 9     | 9                                  |
| 10    | 10                                 |
| 11    | 11                                 |
| 12–13 | 12                                 |
| 14    | 13                                 |
| 15–16 | Capstone                           |
