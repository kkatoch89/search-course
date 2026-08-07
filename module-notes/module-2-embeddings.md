# Module 2 — Embeddings & Vector Search

> **(read-only)** sections are for understanding; **Your turn** is what you
> build. Blanks marked _fill in_ are yours.

**Goal:** Give WikiSearch a second way to find articles — by _meaning_, not just
shared words, so a query and an article can match even with no words in common.
**Time box:** ~2–3 hours &nbsp;|&nbsp; **Time spent:** 2h &nbsp;|&nbsp; **Done when:** `python vector_cli.py "a big animal with a trunk"` returns _Elephant_ on top — and the word "elephant" is nowhere in the query.

---

## Where this fits (builds on Module 1)

- **Module 1 gave you:** keyword search (BM25). It ranks by _shared words_ — it
  can only find an article that literally contains the query's terms, and it
  gets fooled by words with two meanings (the `red fox` / homonym problem you
  saw at the end of Module 1).
- **This module adds:** meaning-based retrieval. Turn text into a vector and
  rank by how _close in meaning_ the query and each document are — so "a big
  animal with a trunk" finds _Elephant_ even though the article never says
  "trunk," and "trunk" doesn't drag in tree trunks or car trunks.
- **New words:** embedding, dimension, vector, cosine similarity, nearest
  neighbor, approximate nearest neighbor (ANN).

---

## The idea in plain English

1. **Turn text into a vector — an "embedding."** A small model
   (`all-MiniLM-L6-v2`, running locally on your laptop) reads a piece of text
   and outputs a list of **384 numbers** that captures its _meaning_. Texts
   about similar things get vectors that point in similar directions. You don't
   compute these — the model does.

2. **Rank by cosine similarity.** To compare two vectors, measure the **angle**
   between them. The cosine of that angle is 1 when they point the same way
   (same meaning), 0 when unrelated, −1 when opposite. Because it's about
   _direction, not length_, a long article and a short query about the same
   topic still score as similar.

3. **This matches on meaning, not words.** That's the whole point. Keyword
   search needs the query's exact words to appear. Vector search finds the
   article whose _meaning_ is closest — even with zero shared words — and isn't
   tricked when a word (like "trunk") has more than one meaning.

---

## Worked example (read-only)

Same four-document toy corpus, one query: **`a big animal with a trunk`**.
Notice the _Elephant_ document deliberately never uses the word "trunk" — it
says "long nose and tusks."

|     doc      | text                                                                     |
| :----------: | ------------------------------------------------------------------------ |
| **Elephant** | "An elephant is an enormous mammal known for its long nose and tusks."   |
|   **Tree**   | "A tree is a tall plant with a woody trunk, branches, and green leaves." |
|   **Car**    | "The trunk of a car is a compartment at the back for storing luggage."   |
|  **Ocean**   | "The ocean is a vast body of salt water covering most of the Earth."     |

**How Module 1's BM25 ranks them** (keyword — matches shared words):

| rank | doc          |   score   |   contains "trunk"?   |
| :--: | ------------ | :-------: | :-------------------: |
|  1   | Tree         |   3.001   |    ✅ (tree trunk)    |
|  2   | Car          |   1.665   |    ✅ (car trunk)     |
|  3   | Ocean        |   0.708   | ❌ (just "a", "with") |
|  4   | **Elephant** | **0.000** |          ❌           |

**How this module's vector search ranks them** (meaning — cosine similarity):

| rank | doc          |  cosine   |
| :--: | ------------ | :-------: |
|  1   | **Elephant** | **0.514** |
|  2   | Car          |   0.451   |
|  3   | Tree         |   0.358   |
|  4   | Ocean        |   0.053   |

**Why the two disagree so sharply:**

- **BM25 puts _Elephant_ dead last (0.000).** The article never contains the
  word "trunk," and keyword search can only match words that are literally
  there. So the one right answer scores _zero_ — it isn't a weak result, it's
  not a result at all.
- **BM25 is fooled by "trunk."** It ranks _Tree_ and _Car_ on top because they
  contain the word — but a tree trunk and a car trunk have nothing to do with
  the query. This is exactly the homonym trap from Module 1.
- **Vector search puts _Elephant_ first (0.514).** "A big animal with a trunk"
  _means_ an elephant, and the embedding captures that meaning regardless of the
  exact words. _Ocean_ falls to near-zero because it's unrelated in meaning.

(These numbers are real — produced by embedding this corpus with
`all-MiniLM-L6-v2` and computing cosine similarity, the same code you're about
to write.)

---

## Your turn — give the engine semantic search

You'll implement vector search inside the same engine at `exercises/wikisearch/`.
The plumbing (loading the model, embedding + caching the 5k docs, the CLI) is
written. You write the scoring and ranking.

### 1. Set up (once)

```bash
cd exercises/wikisearch
source .venv/bin/activate
pip install -r requirements.txt   # now also installs sentence-transformers + numpy
python vector_cli.py "a big animal with a trunk"
```

The first run downloads the small embedding model (~90 MB, public HuggingFace,
no key) and embeds all 5,000 articles — a minute or two on a laptop — then
**caches** the vectors to `data/embeddings_5k.npy`, so every later run is
instant. It then stops at the first unwritten function. That's your starting
line.

### 2. Fill in `wikisearch/vectors.py`

Two functions, top to bottom. Each has a docstring (what goes in / comes out)
and numbered sub-steps. Delete each `raise NotImplementedError(...)` as you go:

- `cosine_similarity(query_vec, doc_matrix)` — given the query's vector and the
  matrix of all document vectors, return one cosine score per document. (The
  cosine formula, and its NumPy pieces, are quoted at the top of the file.)
- `search(query, index, docs, k)` — embed the query, score every doc with
  `cosine_similarity`, return the top-k as `(Document, score)` pairs.

(`VectorIndex` and `build_index` are already written for you — embedding is a
model call, not the lesson. Your work is the similarity and ranking.)

**Stuck on a sub-step? Ask Claude.**

### 3. Check your work

When it's right, `python vector_cli.py "a big animal with a trunk"` returns
(verified against the 5k slice):

```
 1. Elephant   (score 0.513)
 2. Platypus   (score 0.417)
 3. Giant      (score 0.405)
 4. Ostrich    (score 0.392)
 5. Lion       (score 0.374)
```

_Elephant_ on top from a query that never names it, and every result is an
animal. Scores may differ in the last digit depending on your NumPy version;
the ordering and the animal theme should hold.

### 4. Observe (fill in)

Run the **same** query through both engines and compare:

- `python bm25_cli.py "a big animal with a trunk"` → _result observation:_
- `python vector_cli.py "a big animal with a trunk"` → _result observation:_
  &nbsp; _(Which one finds the elephant? Why does the other miss it?)_

Now try a query that's mostly **exact keywords**, e.g. a specific title or a
rare proper noun, on both:

- BM25 result: _fill in_
- Vector result: _fill in_ &nbsp; _(Does vector search ever do **worse** than
  keywords here? Keep this in mind for Module 4.)_

### 5. Tag it

Once it works and is committed: `git tag end-of-m2`.

---

## Concepts to capture (your words → `glossary.md`)

Each was explained above; write them in your own words in `glossary.md`:

- embedding
- embedding dimensionality _(why 384 numbers? what would more/fewer buy you?)_
- cosine similarity / distance
- approximate nearest neighbor (ANN) _(you did **exact** nearest-neighbor —
  scoring every one of the 5k docs. Define ANN from the reading: what you'd
  switch to at millions of docs, and what you trade away.)_

Ask Claude to check your wording if you're unsure a definition is right.

---

## Optional — see it in production (5 min)

Only after the engine works. Same file as Module 1's footnote, one line down the
list of builders:

- **File:** `chunky-kong` → `lib/instinct/search/universal/clients/turbopuffer/ranking.ex:42`
- **Notice:** `def ann(vector), do: ["vector", "ANN", vector]`. Where Module 1's
  `bm25` builder emitted a keyword clause, this emits a **vector** clause:
  `["vector", "ANN", query_vector]`. `ANN` = _approximate_ nearest neighbor —
  production doesn't score all 5k the exact way you did; at scale it uses an
  index that finds the nearest vectors approximately, trading a little recall
  for a lot of speed. Same idea as your `cosine_similarity`, handed to the
  search store instead of computed in a loop.

---

## Open questions

- BM25 found the exact-keyword query; vector search found the by-meaning one.
  Each missed what the other caught. What would happen if you **combined** their
  scores? (That's Module 4 — hybrid search.)
- _fill in your own_
