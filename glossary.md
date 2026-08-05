# Glossary

Grow this as you go. When you hit a term you don't know, define it here in
your own words. Don't just paste from Wikipedia — paraphrase. The act of
rephrasing is the point.

---

## Search fundamentals

- **Inverted index** — A system where each word has a database record of every doc it shows up in (id), the location within each doc and the TF within each doc
- **Tokenization** — The breaking down of raw text into individual, searchable units called tokens
- **Stemming / lemmatization** — Reduce words to their canonical version (eg. foxes -> fox)
- **Term frequency (TF)** — The frequency at which a query term appears in a document. Higher frequency results in higher weight
- **Inverse document frequency (IDF)** — A measure of how rare the term is across the corpus
- **BM25** — An algorithm for ranking documents out of a corpus based off a complex set of calculations that boil down to frequency of terms (TF) and the relevance of terms (IDF).
- **Prefix matching** —
- **Corpus** - The entire collection of documents that's being searched
- **Canonical** - The one official version that everything else is measured against or normalized to

## Vectors & embeddings

- **Embedding** —
- **Embedding dimensionality** —
- **Cosine similarity / distance** —
- **Approximate nearest neighbor (ANN)** —
- **HNSW** —
- **pgvector** —

## Hybrid search

- **Hybrid retrieval** —
- **Score normalization** —
- **Reciprocal rank fusion (RRF)** —
- **Reranking** —
- **Over-fetching** —

## Pipeline & storage

- **Chunking** —
- **Token-aware splitting** —
- **Chunk overlap** —
- **Content hashing** —
- **Idempotency** —
- **Turbopuffer** —
- **Namespace** (Turbopuffer / chunky-kong sense) —
- **Multi-tenant partitioning** —

## Chunky-kong-specific

- **Universal search** —
- **Entity type** —
- **Gate** (identity gate) —
- **Resource** (sync state) —
- **Schema** (`Universal.Schema`) —
- **Extractor** —
- **Planner / Executor / Hydrator** —

## RAG

- **Retrieval-augmented generation (RAG)** —
- **Grounding** —
- **Citation** —
- **Hallucination** —

## Evaluation

- **Recall@k** —
- **Precision@k** —
- **MRR (mean reciprocal rank)** —
- **NDCG (normalized discounted cumulative gain)** —
- **BEIR** —
