# Exercises

One folder per module. Treat each as a tiny standalone project — its own
`README.md`, dependency file, and runnable entry point. The ones marked
**portfolio** become public demos.

```
exercises/
├── module-1/    BM25 CLI over 5k Wikipedia
├── module-2/    Vector similarity search over 5k Wikipedia
├── module-3/    Chunker + content hash
├── module-4/    Hybrid search CLI over 226k Wikipedia          ← portfolio
├── module-5/    + cross-encoder reranking                       ← portfolio
├── module-6/    Turbopuffer namespace + filter benchmarks
├── module-7/    3-stage ingestion pipeline with retries
├── module-8/    excludeIds pagination + new sort mode
├── module-9/    LLM query rewriting + HyDE + router
├── module-10/   "Ask Wikipedia" web app                          ← portfolio
├── module-11/   Agentic Wikipedia researcher                     ← portfolio
├── module-12/   Domain-tuned embedding fine-tune + eval          ← portfolio
└── module-13/   Eval harness + LLM-as-judge + sweep plots
```

## Per-folder template

```
module-N/
├── README.md          # what this exercise is, how to run, what was learned
├── requirements.txt   # or pyproject.toml / package.json
├── src/               # actual code
└── results/           # screenshots, plots, sample outputs
```

## Tips

- Commit your exercise repos publicly — recruiters click through code.
- Every README should answer: what does this do, why does it matter, what
  did I learn.
- Don't over-engineer the early ones — BM25-by-hand doesn't need a class
  hierarchy.
- Save large data files in `../data/` (gitignored) and reference relative
  paths.
- For Modules 9–11 + capstone: never hardcode API keys, always env-var.
