"""Talking to the vector store — THIS IS THE MODULE 6 EXERCISE.

So far your vectors have lived in a NumPy array in memory: every search loads all
5,000 of them and scans the whole array. That doesn't survive a restart, doesn't
scale past what fits in RAM, and can't be queried by more than one process. A
**vector store** is a database built for vectors: it persists them, and it can
answer "nearest neighbours of this vector" (an ANN query) *and* narrow that
search by ordinary metadata **filters** — without you scanning anything yourself.

This module uses **Turbopuffer** (the same store Instinct's production search
runs on). You write the two functions below; the plumbing (``store_cli.py``)
connects to Turbopuffer, calls ``build_rows`` to upsert the corpus once, then
calls ``search`` many times to benchmark **filtered vs. unfiltered** queries.

The module note (``module-notes/module-6-storage.md``) explains every concept and
walks a worked example, and covers getting your API key. Read it first. Stuck on
a sub-step? Ask Claude.

------------------------------------------------------------------------------
REFERENCE 1 — an upsert row (what one stored record looks like)
------------------------------------------------------------------------------
Turbopuffer stores rows. Each row is a plain dict: a required ``id``, a
``vector``, and any number of flat scalar **attributes** you want to filter on
later. You hand a list of these to ``ns.write(upsert_rows=[...],
distance_metric="cosine_distance")``. "Upsert" = insert-or-replace by ``id``, so
re-writing the same id just overwrites it (writes are idempotent by id):

    {"id": "42", "vector": [0.01, -0.03, ...], "title": "Lake",
     "word_count": 569, "length_bucket": "long", "title_initial": "L"}

``derive_attributes(doc)`` (in ``corpus.py``) already returns the
``title`` / ``word_count`` / ``length_bucket`` / ``title_initial`` dict — you
just attach ``id`` and ``vector`` to it.

------------------------------------------------------------------------------
REFERENCE 2 — an ANN query, with and without a filter
------------------------------------------------------------------------------
You ask the store for the nearest neighbours of a query vector:

    result = ns.query(
        rank_by=("vector", "ANN", query_vector),   # nearest by vector distance
        limit=limit,                                # how many rows to return
        include_attributes=["title", "length_bucket", "word_count"],
        filters=filters,                            # None = search everything
    )

``filters`` is a tuple ``(field, op, value)`` — e.g.
``("length_bucket", "Eq", "long")`` means "only consider rows whose
length_bucket equals 'long'". Pass ``filters=None`` to search the whole
namespace (an unfiltered "full scan"). ``result.rows`` is the list of matches,
each already sorted nearest-first; the plumbing handles displaying them.

The whole point of the benchmark: the SAME query, once with ``filters=None`` and
once with a selective filter, so you can see what narrowing the candidate set
does to the results (and time it).
"""
from __future__ import annotations

from corpus import Document, derive_attributes  # noqa: F401  (used in build_rows)


def build_rows(docs: list[Document], embeddings) -> list[dict]:
    """Turn documents + their vectors into Turbopuffer upsert rows.

    In:  docs        — [Document, ...]
         embeddings  — an (n_docs, 384) matrix; row i is docs[i]'s vector,
                        aligned by position (a NumPy array)
    Out: [ {"id": ..., "vector": [...], + attributes}, ... ] — one dict per doc

    Sub-steps:
      1. Make an empty list ``rows``.
      2. For each position ``i`` (use ``enumerate(docs)`` so you have both the
         index and the doc), build one row dict:
           - ``"id"``: the document's id (``doc.id``).
           - ``"vector"``: ``embeddings[i]`` as a plain Python list of floats.
             The matrix row is a NumPy array — call ``.tolist()`` on it so it
             serialises cleanly over the wire.
           - the attributes: merge in everything ``derive_attributes(doc)``
             returns (title, word_count, length_bucket, title_initial). A clean
             way is ``{"id": doc.id, "vector": ..., **derive_attributes(doc)}``.
      3. Append each row and return the list.
    """
    raise NotImplementedError("Implement build_rows (see sub-steps above).")


def search(namespace, query_vector, limit: int = 5, length_bucket: str | None = None):
    """Nearest-neighbour query against the store, optionally narrowed by a filter.

    In:  namespace     — a Turbopuffer namespace handle (the plumbing hands it to
                          you; call ``namespace.query(...)`` on it)
         query_vector  — the vector to find neighbours of (a list of floats)
         limit         — how many rows to return
         length_bucket — if given (e.g. "long"), restrict the search to rows with
                          that length_bucket; if None, search the whole namespace

    Out: the query result (its ``.rows`` is the nearest-first matches). Return
         whatever ``namespace.query(...)`` gives back — the plumbing reads it.

    Sub-steps:
      1. Turn ``length_bucket`` into a Turbopuffer filter:
           - if it's None, use ``filters = None`` (search everything).
           - otherwise ``filters = ("length_bucket", "Eq", length_bucket)`` —
             the (field, op, value) tuple that means "length_bucket == this".
      2. Call and return the query:
             return namespace.query(
                 rank_by=("vector", "ANN", query_vector),
                 limit=limit,
                 include_attributes=["title", "length_bucket", "word_count"],
                 filters=filters,
             )
         (``rank_by=("vector", "ANN", ...)`` asks for the nearest neighbours of
         your vector; ``include_attributes`` asks the store to send those fields
         back so the results are readable.)
    """
    raise NotImplementedError("Implement search (see sub-steps above).")
