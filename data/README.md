# data/

Downloaded corpora live here. **Not committed to git.**

Expected files (after running `data-setup.md`):

- `wiki_simple_full.parquet` — full Simple English Wikipedia, ~226k articles, ~700MB
- `wiki_simple_5k.parquet` — 5k random subsample for early modules
- `eval_queries.jsonl` — your hand-labeled (query, ideal-titles) pairs (Module 9 + capstone)

## .gitignore

Add this to your project's `.gitignore`:

```
search-course/data/*.parquet
search-course/data/*.csv
search-course/data/*.bin
search-course/data/embeddings/
```

Keep `eval_queries.jsonl` versioned — it's small and worth keeping.
