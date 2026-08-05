"""Chunk the 5k corpus and prove idempotency — plumbing, written for you.

Usage:
    python chunk_cli.py                 # defaults: size=500, overlap=50
    python chunk_cli.py --size 300 --overlap 30

It chunks every article, then runs the embed step TWICE against one shared
cache:
  * run 1 starts with an empty cache  -> every chunk is embedded
  * run 2 sees the same chunks already cached -> zero embeds

That second zero is the whole point of the module: re-ingesting unchanged
content costs nothing.

This calls YOUR functions in chunking.py. Until they're written it stops at the
first NotImplementedError — that's your starting line.
"""
from __future__ import annotations

import argparse

from chunking import chunk_corpus, embed_new_chunks
from corpus import load_corpus
from embedder import StubEmbedder


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk the 5k corpus + prove idempotency.")
    parser.add_argument("--size", type=int, default=500, help="tokens per chunk")
    parser.add_argument("--overlap", type=int, default=50, help="tokens shared between chunks")
    args = parser.parse_args()

    docs = load_corpus()
    print(f"loaded {len(docs):,} articles")

    chunks = chunk_corpus(docs, size=args.size, overlap=args.overlap)
    texts = [c.text for c in chunks]
    print(f"chunked into {len(chunks):,} chunks (size={args.size}, overlap={args.overlap})")

    cache: dict = {}          # persists across the two runs below
    embedder = StubEmbedder()

    n1 = embed_new_chunks(texts, cache, embedder)
    print(f"run 1 (nothing cached yet): {n1:>7,} embeddings computed")

    n2 = embed_new_chunks(texts, cache, embedder)
    print(f"run 2 (same input, warm cache): {n2:>4,} embeddings computed   <-- should be 0")

    if n2 == 0:
        print("\nidempotent ✓  re-running on unchanged input did no embedding work.")
    else:
        print("\nnot idempotent yet ✗  run 2 should have computed 0 embeddings.")


if __name__ == "__main__":
    main()
