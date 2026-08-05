# Search & Retrieval

A 16-week course on full-text + semantic + AI-augmented search, grounded in
the production implementation in `chunky-kong/lib/instinct/search/universal/`
and `merlin/src/services/`.

## Folder layout

```
search-course/
├── README.md              ← you are here
├── search-syllabus.md     ← the 13-module curriculum + capstone
├── data-setup.md          ← Simple English Wikipedia download + subsample
├── glossary.md            ← terms-as-you-learn (grow this!)
├── module-notes/          ← one note file per module — what I read, built, learned
├── exercises/             ← scratch code for exercises (one folder per module)
└── data/                  ← downloaded corpora (gitignored)
```

## How to use

1. Read [`search-syllabus.md`](./search-syllabus.md) end-to-end once. Don't
   try to absorb it — get the shape.
2. Run [`data-setup.md`](./data-setup.md) to download Simple English Wikipedia.
3. Work through one module at a time. For each module:
   - Update [`glossary.md`](./glossary.md) with new terms.
   - Use the corresponding `module-notes/module-N-*.md` to capture what you
     read, built, and questions raised.
   - Put exercise/mini-project code in `exercises/module-N/`.

## Prerequisites

- Python 3.11+ (preferred for the course; you can also do Elixir for the
  pipeline modules)
- PostgreSQL 16 with `pgvector` extension *or* SQLite 3.45+ for FTS5
- OpenAI API key (capstone only — exercises use a free local embedder)
- Anthropic API key (Modules 9–11, capstone)
- Turbopuffer account (free tier) for Module 6 onward
- GPU is nice-to-have for Module 12 (fine-tuning); CPU works, just slower

## Portfolio demos to ship

| Module | Demo                                                |
| ------ | --------------------------------------------------- |
| 4      | Hybrid search CLI over 226k Wikipedia articles      |
| 5      | + cross-encoder reranking (extends Module 4 demo)   |
| 10     | "Ask Wikipedia" web app with citations              |
| 11     | Agentic Wikipedia researcher (multi-hop)            |
| 12     | Domain-tuned embeddings experiment + writeup        |
| Capstone | WikiSearch — full multi-namespace search + RAG    |
