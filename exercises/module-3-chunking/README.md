# Module 3 — Chunking & Idempotency (satellite)

Standalone exercise for **Module 3**. Unlike Modules 1–2 (which grow the
`wikisearch` engine), this folder is self-contained: it reuses the engine's 5k
Wikipedia slice but doesn't modify the engine.

**What it teaches:** splitting long articles into fixed-size overlapping chunks
before embedding, and using a SHA-256 **content hash** so re-processing unchanged
articles does zero embedding work (idempotency).

**Full walkthrough:** [`module-notes/module-3-chunking.md`](../../module-notes/module-3-chunking.md)

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python chunk_cli.py            # stops at the first TODO in chunking.py
```

Needs the shared 5k slice (`../wikisearch/data/wiki_simple_5k.parquet`). If it's
missing: `cd ../wikisearch && python setup_data.py`.

## Files

| file | role |
| ---- | ---- |
| `chunking.py` | **you write this** — `chunk_fixed`, `content_hash`, `embed_new_chunks` |
| `chunk_cli.py` | plumbing — chunks the corpus, runs the embed step twice, proves idempotency |
| `corpus.py` | plumbing — loads the shared 5k slice |
| `embedder.py` | plumbing — a call-counting stub standing in for Module 2's real embedder |

**Done when** the second run reports `0` embeddings (`idempotent ✓`).
