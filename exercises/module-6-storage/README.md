# Module 6 — Storage: Turbopuffer (satellite)

Standalone exercise for **Module 6**. Like Module 3, this folder is
self-contained: it reuses the engine's 5k Wikipedia slice **and** the vectors you
cached in Module 2, but doesn't modify the engine — so there's no `end-of-m6`
engine tag.

**What it teaches:** moving your vectors out of an in-memory NumPy array into a
real **vector store** (Turbopuffer) — namespaces, upsert semantics, and metadata
**filters** — then benchmarking a filtered query against an unfiltered full scan.

**Full walkthrough:** [`module-notes/module-6-storage.md`](../../module-notes/module-6-storage.md)

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# A free Turbopuffer key (personal free-tier, NOT a shared/prod namespace):
export TURBOPUFFER_API_KEY='tpuf-...'          # never hardcode this
export TURBOPUFFER_REGION='gcp-us-central1'    # match your namespace's region

python store_cli.py            # stops at the first TODO in vector_store.py
```

Needs the shared 5k slice **and** the cached embeddings, both in
`../wikisearch/data/`. If they're missing:
`cd ../wikisearch && python setup_data.py && python vector_cli.py "test"`.

## Files

| file | role |
| ---- | ---- |
| `vector_store.py` | **you write this** — `build_rows` (upsert records) + `search` (ANN query ± filter) |
| `store_cli.py` | plumbing — connects, upserts once, benchmarks filter vs. scan |
| `corpus.py` | plumbing — loads the shared 5k slice + cached vectors, derives filter attributes |

**Done when** `python store_cli.py` upserts the corpus and prints two latency
blocks (no-filter vs. `length_bucket` filter), with the filtered list visibly
excluding non-matching articles.

## Security notes

- **Public data only** — Simple English Wikipedia. No customer/patient data, no
  Instinct source data goes into your namespace.
- **Personal free-tier namespace**, never a shared or production one. Turbopuffer
  is already in Instinct's approved stack, so this isn't a new-vendor review —
  but keep your demo data isolated.
- **Key hygiene** — `TURBOPUFFER_API_KEY` lives in your env / 1Password, never in
  code, never pasted into chat. It grants write access to your namespaces.
