"""Module 3 — chunking + content-hash idempotency.

You write three functions. Everything else in this file (the ``Chunk`` type and
the ``chunk_document`` / ``chunk_corpus`` glue) is plumbing that *calls* your
functions — read it, don't change it.

------------------------------------------------------------------------------
REFERENCE 1 — fixed-size chunking with overlap
------------------------------------------------------------------------------
A long article is too big to embed as one vector (its meaning gets averaged into
mush, and it may exceed the model's input limit). So you slice it into fixed-size
windows of tokens, and let consecutive windows OVERLAP so a sentence that lands
on a boundary still appears whole in one chunk.

Two knobs:
  size     = how many tokens per chunk        (production default: 500)
  overlap  = how many tokens each chunk shares with the previous one (default: 50)

The window advances by ``step = size - overlap`` tokens each time:

  tokens:  [t0 t1 t2 t3 t4 t5 t6 t7 t8 t9 ...]      size=5, overlap=2, step=3
  chunk 0:  t0 t1 t2 t3 t4
  chunk 1:            t3 t4 t5 t6 t7      <- shares t3,t4 with chunk 0
  chunk 2:                      t6 t7 t8 t9 ...

("token" here = one whitespace-separated word; ``tokenize`` is provided below.
Real systems count sub-word tokens with the model's tokenizer — see the note.)

------------------------------------------------------------------------------
REFERENCE 2 — content hashing for idempotency
------------------------------------------------------------------------------
A ``content_hash`` is a short fingerprint of a chunk's text: same text -> same
hash, one character different -> completely different hash. Keep a cache of
hashes you've already embedded. Before embedding a chunk, check its hash: if you
have it, skip the (slow, paid) embed call. Re-running on unchanged input then
does ZERO embedding work — that's idempotency.

We use SHA-256 rendered as a hex string:
    import hashlib
    hashlib.sha256(text.encode("utf-8")).hexdigest()   # -> "684b617bdfeb..."
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass


def tokenize(text: str) -> list[str]:
    """Split text into tokens. PROVIDED — not the lesson.

    Here a token is just a whitespace-separated word.
    """
    return text.split()


def chunk_fixed(tokens: list[str], size: int, overlap: int) -> list[list[str]]:
    """Slice a token list into fixed-size overlapping windows.

    Input:
        tokens  — the article's tokens (e.g. from ``tokenize``)
        size    — max tokens per chunk (e.g. 500)
        overlap — tokens each chunk repeats from the previous one (e.g. 50);
                  assume 0 <= overlap < size
    Output:
        a list of chunks, each chunk a list of tokens. The last chunk may be
        shorter than ``size``. An empty ``tokens`` list yields ``[]``.

    Sub-steps:
      1. Compute how far the window advances each time: step = size - overlap.
      2. Slide a start position from 0 upward, increasing by ``step`` each time
         (a ``range(0, len(tokens), step)`` loop does exactly this).
      3. At each start, take the window tokens[start : start + size] and, if it
         isn't empty, add it to your list of chunks.
      4. Stop once a window has reached the end of the tokens
         (start + size >= len(tokens)) — otherwise the overlap keeps emitting
         ever-shorter tail windows past the end.
    """

    step = size - overlap

    result = []
    for i in range(0, len(tokens), step):
        result.append(tokens[i : i + size])
        if i + size >= len(tokens):
            break
    return result

@dataclass
class Chunk:
    """One chunk of one document. PROVIDED."""

    doc_id: str
    index: int   # position of this chunk within its document (0, 1, 2, ...)
    text: str


def chunk_document(doc, size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Tokenize a Document and turn its windows into Chunk objects. PROVIDED.

    This is the glue that uses YOUR ``chunk_fixed``.
    """
    windows = chunk_fixed(tokenize(doc.text), size, overlap)
    return [
        Chunk(doc_id=doc.id, index=i, text=" ".join(window))
        for i, window in enumerate(windows)
    ]


def chunk_corpus(docs, size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Chunk every Document in the corpus. PROVIDED."""
    chunks: list[Chunk] = []
    for doc in docs:
        chunks.extend(chunk_document(doc, size, overlap))
    return chunks


def content_hash(text: str) -> str:
    """Return a hex SHA-256 fingerprint of ``text``.

    Sub-steps:
      1. Encode the string to bytes: ``text.encode("utf-8")``.
      2. Hash it and return the hex digest:
         ``hashlib.sha256(<bytes>).hexdigest()``.
    """
    encoded_string = text.encode("utf-8")
    return hashlib.sha256(encoded_string).hexdigest()

def embed_new_chunks(chunk_texts: list[str], cache: dict, embedder) -> int:
    """Embed only the chunks we haven't embedded before. Return how many we did.

    Input:
        chunk_texts — the text of every chunk this run
        cache       — dict mapping content_hash -> embedding. It PERSISTS across
                      runs (the caller keeps it), so a hash already in it means
                      "already embedded — skip."
        embedder    — has ``.embed(text)`` (here, the call-counting StubEmbedder)
    Output:
        the number of chunks that were newly embedded this run.

    Sub-steps:
      1. Start a counter ``new = 0``.
      2. For each chunk text, compute its ``content_hash``.
      3. If that hash is NOT already a key in ``cache``: call
         ``embedder.embed(text)``, store the result in ``cache`` under that hash,
         and add 1 to ``new``. (If it IS in the cache, do nothing — that's the
         skip that makes re-runs free.)
      4. Return ``new``.
    """
    new = 0
    for chunk_text in chunk_texts:
        hash = content_hash(chunk_text)

        if hash not in cache:
            cache[hash] = embedder.embed(chunk_text)
            new += 1

    return new