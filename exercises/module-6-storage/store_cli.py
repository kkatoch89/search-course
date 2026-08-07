"""Module 6 CLI — plumbing. Upserts the corpus once, then benchmarks the SAME
nearest-neighbour query with no filter vs. a length_bucket filter.

Written for you. It calls the two functions YOU write in ``vector_store.py``
(``build_rows`` to load the store, ``search`` to query it).

    # 1. one-time: put the corpus in your personal namespace + benchmark
    python store_cli.py

    # later runs: skip the upload, just benchmark
    python store_cli.py --skip-upsert --like "Photosynthesis"

Query model: "more like this article." We use a stored article's OWN vector as
the query (nearest neighbours of it), so this module needs no embedding model —
just the vectors Module 2 already cached. ``--like`` picks the seed article.

Auth: reads ``TURBOPUFFER_API_KEY`` from the environment (never hardcode it).
Region defaults to ``gcp-us-central1`` — override with ``--region`` or
``TURBOPUFFER_REGION`` to match your namespace's region (see the dashboard).
"""
from __future__ import annotations

import argparse
import os
import statistics
import time

from corpus import Document, derive_attributes, load_corpus, load_embeddings
from vector_store import build_rows, search

UPSERT_BATCH = 1000


# --------------------------------------------------------------------------- #
# Turbopuffer connection (plumbing)
# --------------------------------------------------------------------------- #
def connect(namespace_name: str, region: str):
    """Return a Turbopuffer namespace handle, or exit with a friendly message."""
    api_key = os.environ.get("TURBOPUFFER_API_KEY")
    if not api_key:
        raise SystemExit(
            "TURBOPUFFER_API_KEY is not set.\n"
            "Get a free key at https://turbopuffer.com, then (never hardcode it):\n"
            "    export TURBOPUFFER_API_KEY='tpuf-...'\n"
            "See module-notes/module-6-storage.md for the full setup."
        )
    try:
        import turbopuffer
    except ModuleNotFoundError:
        raise SystemExit("turbopuffer not installed. Run: pip install -r requirements.txt")

    client = turbopuffer.Turbopuffer(api_key=api_key, region=region)
    return client.namespace(namespace_name)


def upsert_corpus(namespace, docs: list[Document], embeddings) -> None:
    """Build rows (YOUR code) and write them to the store in batches."""
    rows = build_rows(docs, embeddings)
    print(f"upserting {len(rows):,} rows into the namespace (batches of {UPSERT_BATCH})...")
    for start in range(0, len(rows), UPSERT_BATCH):
        batch = rows[start : start + UPSERT_BATCH]
        namespace.write(upsert_rows=batch, distance_metric="cosine_distance")
        print(f"  wrote {min(start + UPSERT_BATCH, len(rows)):,}/{len(rows):,}")
    print("upsert done.\n")


# --------------------------------------------------------------------------- #
# Reading rows back defensively (row shape varies across SDK versions)
# --------------------------------------------------------------------------- #
def _rget(row, key, default=None):
    """Read ``key`` off a result row whether it's dict-like or attribute-like."""
    try:
        return row[key]
    except (TypeError, KeyError, IndexError):
        pass
    return getattr(row, key, default)


def _rows_of(result):
    """The list of rows, whether the SDK returns an object with .rows or a list."""
    return getattr(result, "rows", result)


def _fmt(row) -> str:
    dist = _rget(row, "$dist")
    dist_s = f"{dist:.3f}" if isinstance(dist, (int, float)) else "  —  "
    bucket = _rget(row, "length_bucket", "?")
    wc = _rget(row, "word_count", "?")
    return f"    dist {dist_s}  [{str(bucket):>6} {str(wc):>4}w]  {_rget(row, 'title')}"


def show(result, seed_id: str, k: int) -> None:
    """Print up to k rows, skipping the seed article (it's its own nearest match)."""
    shown = 0
    for row in _rows_of(result):
        if str(_rget(row, "id")) == str(seed_id):
            continue
        print(_fmt(row))
        shown += 1
        if shown >= k:
            break


# --------------------------------------------------------------------------- #
# Benchmark
# --------------------------------------------------------------------------- #
def time_query(namespace, qvec, limit, bucket, repeats):
    """Run search() ``repeats`` times, return (median_ms, min_ms, last_result)."""
    # warmup (first call pays connection / cache costs we don't want to measure)
    result = search(namespace, qvec, limit=limit, length_bucket=bucket)
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = search(namespace, qvec, limit=limit, length_bucket=bucket)
        times.append((time.perf_counter() - t0) * 1000.0)
    return statistics.median(times), min(times), result


def main() -> None:
    p = argparse.ArgumentParser(description="Module 6 — vector store filter-vs-scan benchmark")
    p.add_argument("--namespace", default=f"{os.environ.get('USER', 'me')}-wiki-demo",
                   help="your PERSONAL namespace name (free-tier, not shared/prod)")
    p.add_argument("--region", default=os.environ.get("TURBOPUFFER_REGION", "gcp-us-central1"))
    p.add_argument("--like", default="Salt water",
                   help="seed article title; its vector is the query")
    p.add_argument("--bucket", default="long", choices=["short", "medium", "long"],
                   help="length_bucket to filter to in the filtered run")
    p.add_argument("--limit", type=int, default=5, help="results to show per query")
    p.add_argument("--repeats", type=int, default=20, help="timed repeats per query")
    p.add_argument("--skip-upsert", action="store_true",
                   help="don't re-upload the corpus (use after the first run)")
    args = p.parse_args()

    docs = load_corpus()
    embeddings = load_embeddings()
    if len(docs) != len(embeddings):
        raise SystemExit(f"corpus ({len(docs)}) and embeddings ({len(embeddings)}) disagree.")
    print(f"loaded {len(docs):,} articles + vectors\n")

    namespace = connect(args.namespace, args.region)
    print(f"namespace: {args.namespace}  (region {args.region})\n")

    if not args.skip_upsert:
        upsert_corpus(namespace, docs, embeddings)
    else:
        print("skipping upsert (--skip-upsert)\n")

    # Resolve the seed article -> its stored vector is the query.
    by_title = {d.title: i for i, d in enumerate(docs)}
    if args.like not in by_title:
        raise SystemExit(f"no article titled {args.like!r} in the 5k slice. Try --like 'Lake'.")
    seed_i = by_title[args.like]
    seed_id = docs[seed_i].id
    qvec = embeddings[seed_i].tolist()
    seed_bucket = derive_attributes(docs[seed_i])["length_bucket"]
    print(f"query = nearest neighbours of {args.like!r} [{seed_bucket}] "
          f"(the seed itself is dropped from results)\n")

    over = args.limit + 1  # over-fetch so dropping the seed still leaves `limit`

    print("=" * 70)
    print(f"NO FILTER  (search the whole namespace, {len(docs):,} rows)")
    med, lo, res = time_query(namespace, qvec, over, None, args.repeats)
    show(res, seed_id, args.limit)
    print(f"  latency: median {med:.1f} ms   best {lo:.1f} ms   ({args.repeats} runs)")

    print("=" * 70)
    print(f"FILTER  length_bucket == {args.bucket!r}  (narrowed candidate set)")
    med_f, lo_f, res_f = time_query(namespace, qvec, over, args.bucket, args.repeats)
    show(res_f, seed_id, args.limit)
    print(f"  latency: median {med_f:.1f} ms   best {lo_f:.1f} ms   ({args.repeats} runs)")
    print("=" * 70)

    print(f"\nfilter vs scan (median): {med_f:.1f} ms vs {med:.1f} ms")
    print("On 5k both are fast and network-dominated; the filter's win grows with")
    print("corpus size. Note how the filtered list *excludes* non-'long' matches —")
    print("a metadata filter narrows by attribute, not by relevance.")


if __name__ == "__main__":
    main()
