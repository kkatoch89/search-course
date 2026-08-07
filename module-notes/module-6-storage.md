# Module 6 — Storage: A Real Vector Store (Turbopuffer)

> **(read-only)** sections are for understanding; **Your turn** is what you
> build. Blanks marked _fill in_ are yours.

**Goal:** Move your vectors out of an in-memory NumPy array and into a real
**vector store** (Turbopuffer, the same one Instinct's production search runs on).
Store each article as a row — vector + filterable attributes — then benchmark the
one thing a store gives you that a flat array can't cheaply do: a query
**narrowed by a metadata filter** vs. an unfiltered full scan.
**Time box:** ~2 hours &nbsp;|&nbsp; **Time spent:** _fill in_ &nbsp;|&nbsp; **Done when:** `python store_cli.py` upserts the 5k corpus into your namespace and prints two latency blocks — a no-filter scan and a `length_bucket` filter — and the filtered list visibly **excludes** the non-matching articles.

> **This is a _satellite_, not the engine.** Like Module 3, it's a standalone
> folder (`exercises/module-6-storage/`) that reuses the engine's data but doesn't
> modify it — so there's **no `end-of-m6` engine tag**. It takes the vectors you
> built in Module 2 and shows where they'd really live. You'll wire a store into
> the actual ingestion pipeline in Module 7.

---

## Where this fits (builds on Module 2)

- **Module 2 gave you** vector search over a NumPy array: all 5,000 embeddings in
  RAM, and every query does a full `matrix @ query` scan of the whole array.
- **The limits of that array**, all of which a database fixes:
  - **It's gone on restart** — nothing is persisted; you rebuild it every run.
  - **It's capped by RAM** — 5k fits; 226k is snug; millions don't.
  - **It's one process** — no other service can query it.
  - **Filtering is your problem** — in Module 2 you masked the NumPy array by hand
    to restrict a search. A store does that server-side, as part of the query.
- **This module adds** a **vector store**: a database purpose-built to persist
  vectors and answer "nearest neighbours of this vector, optionally filtered by
  these attributes" — without you holding anything in memory or scanning by hand.
- **New words:** vector store, namespace, upsert, attribute / metadata filter,
  ANN (approximate nearest neighbour), filtered query vs. full scan.

---

## The idea in plain English

1. **A namespace is one isolated collection of rows.** Each row is a `{id,
   vector, ...attributes}` dict. You point the client at a namespace by name and
   read/write only that. It's also the **isolation boundary**: you'll use one
   personal namespace; production scopes a *separate* namespace per environment
   and per customer so no query can ever cross tenants (see the footnote).

2. **You store attributes right next to the vector.** Alongside each 384-dim
   vector you attach plain scalars — here `title`, `word_count`, `length_bucket`,
   `title_initial`. They aren't part of the similarity math; they exist so you can
   later say "only search rows where `length_bucket` is `long`."

3. **Upsert = insert-or-replace by `id`.** Writing a row whose `id` already exists
   overwrites it. So re-running the load is safe and repeatable — the same
   **idempotency** idea from Module 3, now enforced by the store's primary key.

4. **A filter narrows the candidate set; the ANN ranks what's left.** A query has
   two parts: `rank_by=("vector","ANN", q)` ("find the nearest neighbours of `q`")
   and an optional `filters=("field","Eq",value)` ("but only among rows matching
   this"). No filter = search the whole namespace (a full scan). A selective
   filter = the store considers far fewer rows, so it does less work. The catch:
   **a filter narrows by *attribute*, not by *relevance*** — it can exclude a row
   that was actually the best match. (You'll see exactly that below.)

---

## Worked example (read-only)

We use a **"more like this article"** query: take one stored article's own vector
as the query and ask for its nearest neighbours (so this module needs no embedding
model — just the vectors Module 2 cached). Seed article: **`Salt water`** (a
medium-length, 194-word article). Its own row is dropped from the results.

**NO FILTER — nearest neighbours across all 5,000 rows:**

| rank | doc | length_bucket | words | |
| :--: | --- | :---: | :---: | --- |
| 1 | **Table salt** | medium | 330 | ← the single closest neighbour |
| 2 | Salt | long | 454 | |
| 3 | Sodium | long | 642 | |
| 4 | Lake | long | 569 | |
| 5 | Drinking water | medium | 180 | |

**FILTER `length_bucket == "long"` — same query, narrowed candidate set:**

| rank | doc | length_bucket | words | |
| :--: | --- | :---: | :---: | --- |
| 1 | Salt | long | 454 | |
| 2 | Sodium | long | 642 | |
| 3 | Lake | long | 569 | |
| 4 | **Water** | long | 1689 | ← pulled up from deeper once the mediums are gone |
| 5 | **Jellyfish** | long | 816 | ← ditto |

**What the filter did:**

- **It dropped rows by attribute, not by score.** *Table salt* was the **closest
  neighbour of all** — but it's a *medium* article, so the `length_bucket ==
  "long"` filter removed it. *Drinking water* (medium) went too. That's the core
  trade-off: **the filter narrows by a property you chose, and doesn't care that
  the row it dropped was the best match.** Filter on the wrong attribute and you
  hurt relevance.
- **What was already there stays in order.** Salt/Sodium/Lake were long, so they
  keep their places; *Water* and *Jellyfish* rise into the freed slots.
- **This is the mechanism the benchmark measures.** "long" is ~2,100 of the 5,000
  rows, so the store scores fewer candidates. On a 5k namespace the time
  difference is small and mostly network; the point is that the work scales with
  *how many rows survive the filter*, not the corpus size — which is why filtering
  matters enormously at 226k, or at production's millions.

_(The orderings above are verified against the 5k slice — an exhaustive cosine
scan, which on 5k is exactly what Turbopuffer's ANN returns. Your live run shows a
`$dist` — a cosine **distance**, smaller = nearer — next to each; ANN is
approximate, so a far-down tie may reorder slightly.)_

---

## Your turn — put the corpus in a store and benchmark it

The plumbing (`store_cli.py`) connects to Turbopuffer, calls **your** `build_rows`
to upsert the corpus once, then calls **your** `search` many times to time a
filtered query against a full scan. You write the two functions in
`vector_store.py`.

### 1. Get a key and set up (once)

Turbopuffer is already in Instinct's approved stack — this is **not** a new-vendor
review — but treat the key like any credential.

```bash
cd exercises/module-6-storage
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Free personal key from https://turbopuffer.com — never hardcode it:
export TURBOPUFFER_API_KEY='tpuf-...'
export TURBOPUFFER_REGION='gcp-us-central1'   # match your namespace's region (dashboard)

python store_cli.py
```

This reuses the engine's 5k parquet **and** the `embeddings_5k.npy` you cached in
Module 2 (both in `../wikisearch/data/`). If it says either is missing, run
`cd ../wikisearch && python setup_data.py && python vector_cli.py "test"` once,
then come back. With the functions unwritten, it stops at the first TODO — your
starting line.

> **Governance (read once):** the namespace holds **public Wikipedia only** — no
> customer, patient, or Instinct data. Use a **personal free-tier** namespace
> (the default name is `<you>-wiki-demo`), never a shared or production one. The
> key lives in your env / 1Password, never in code or chat.

### 2. Fill in `vector_store.py`

Two functions, each with a docstring and numbered sub-steps; delete each
`raise NotImplementedError` as you go:

- `build_rows(docs, embeddings)` — turn documents + vectors into upsert rows
  (`id`, `vector`, and the attributes from `derive_attributes`). This is the
  "what does one stored record look like" step.
- `search(namespace, query_vector, limit, length_bucket=None)` — issue the ANN
  query, adding a `("length_bucket","Eq",...)` filter when a bucket is given.
  This is the whole lesson: one line decides scan vs. filtered.

**Stuck on a sub-step? Ask Claude.**

### 3. Check your work

`python store_cli.py` uploads the 5k rows (first run only), then prints the two
blocks from the worked example — *Table salt* and *Drinking water* present in the
no-filter list and **absent** from the filtered one. After the first upload, add
`--skip-upsert` to re-run instantly without re-uploading.

### 4. Record the benchmark (fill in)

The latency numbers are **yours to capture** — they depend on your region and
network, so there's no "correct" number to match, only a direction to explain.
Run it a few times and fill this in:

| query | median latency | rows searched (≈) |
| ----- | -------------- | ----------------- |
| no filter (full scan) | _fill in_ ms | ~5,000 |
| `length_bucket = "long"` | _fill in_ ms | ~2,100 |

- **Which was faster, and by how much?** Is the gap big or barely there at 5k?
  _fill in_
- **Selectivity.** Re-run with `--bucket short` (only ~991 rows match) vs the
  default `--bucket long` (~2,100). Does the *more selective* filter widen the
  latency gap? _fill in_ &nbsp; _(hint: the store scores only the surviving rows.)_
- **The relevance cost.** With `--bucket long`, the best overall match (*Table
  salt*) disappeared. In your own words: when is filtering by an attribute like
  this worth losing a top hit — and when would it quietly wreck your results?
  _fill in_

There's no git tag for this satellite — you're done when the two blocks print and
the table above is filled.

---

## Concepts to capture (your words → `glossary.md`)

- vector store _(what does it give you that a NumPy array of vectors doesn't?)_
- namespace _(what is it the boundary of — and why does production use many?)_
- upsert _(how does it relate to Module 3's idempotency?)_
- attribute / metadata filter _(is it part of the similarity math? what does it act on?)_
- ANN — approximate nearest neighbour _(what is traded away vs. your exact Module 2 scan?)_
- filtered query vs. full scan _(what determines how much a filter speeds a query up?)_

Ask Claude to check your wording if you're unsure a definition is right.

---

## Optional — see it in production (5 min)

Only after your benchmark prints. Two real files in `chunky-kong`, one per idea:

- **Namespaces as the tenant boundary** →
  `lib/instinct/search/universal/sync/namespace.ex`
  - **Notice:** your one `<you>-wiki-demo` namespace is production's many. Line 16,
    `def vectors(entity_domain), do: "#{prefix()}-#{entity_domain}-vectors"`,
    builds a namespace name, and `prefix/0` (line 59) is
    `"#{env}-mkt-#{market.id}"` — so every namespace is scoped by **environment**
    *and* **market** *and* **entity domain**. The moduledoc (lines 4–7) states the
    reason outright: _"it is not possible to access or modify namespaces belonging
    to other markets."_ The namespace *is* the multi-tenant wall — exactly the
    isolation you're leaning on by keeping demo data in your own namespace.
- **Filter compilation** →
  `lib/instinct/search/universal/clients/turbopuffer/filters.ex`
  - **Notice:** the tuple you wrote by hand, `("length_bucket", "Eq", "long")`, is
    one row of production's translator. `@op_strings` (lines 9–34) maps every
    supported operator (`eq → "Eq"`, `in → "In"`, `gte → "Gte"`,
    `contains → "Contains"`, …), and `compile/1` (line 47),
    `def compile({op, field, value}), do: [field, Map.fetch!(@op_strings, op), value]`,
    emits exactly `[field, "Eq", value]` — the same wire shape. Production just
    composes them with `And`/`Or`/`Not` (lines 44–46) for arbitrarily complex
    filters. You wrote one clause; this compiles thousands.

---

## Open questions

- **How selective must a filter be to pay off?** Filtering to ~2,100 of 5,000
  barely helps; filtering to a handful helps a lot. Where's the break-even — and
  does it depend on whether the store filters *before* or *during* the ANN walk?
- **Filter vs. relevance, again.** A `word_count >= 2000` numeric filter (the
  store supports `Gt`/`Gte`/`Lt`/… on integers, per the footnote's op table) would
  keep only long-form articles. When is a hard attribute filter the right tool,
  and when should the attribute instead just *influence* ranking rather than
  gate it?
- **ANN is approximate.** Your Module 2 scan was exact. What does a store trade
  for speed, and how would you even measure what you lost? _(That's `recall@k` —
  Module 13's job.)_
- **When would you keep vectors in Postgres (`pgvector`) instead of a dedicated
  store like Turbopuffer?** Think latency, ops burden, cost, and whether you need
  to `JOIN` the vectors against other relational data. _fill in your take_
- _fill in your own_
