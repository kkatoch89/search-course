# Module 3 — Chunking & Idempotency

> **(read-only)** sections are for understanding; **Your turn** is what you
> build. Blanks marked _fill in_ are yours.

**Goal:** Prepare articles for embedding the way real ingestion pipelines do —
split long ones into overlapping chunks, and use a content hash so re-processing
unchanged articles costs nothing.
**Time box:** ~2 hours  |  **Time spent:** _1.5h_  |  **Done when:** `python chunk_cli.py` reports `0` **embeddings** on its second run (`idempotent ✓`).

> **Note — this is a _satellite_, not the engine.** Modules 1 and 2 grew the
> `wikisearch` engine. This module is a standalone folder
> (`exercises/module-3-chunking/`) that reuses the same 5k corpus but doesn't
> touch the engine — so there's no `end-of-m3` engine tag. It's the "ingestion
> prep" idea in isolation; you'll fold chunking into the real pipeline in
> Module 7.

---

## Where this fits (builds on Module 2)

- **Module 2 gave you:** vector search. You embedded each article as **one**
  vector — `f"{title}. {text}"` straight into the model.
- **Two problems that creates:**
  1. **One vector per long article is blurry.** A 5,000-word article on
     "Evolution" touches genetics, fossils, natural selection… averaged into a
     single point, no part is represented sharply, so a query about one
     sub-topic matches weakly. Embedding models also **cap their input length** —
     past it, the tail is silently dropped.
  2. **Re-embedding everything, every time, is wasteful.** Wikipedia changes a
     little each day. Re-embedding all 5k (or 226k) articles on every sync burns
     time and, with a paid model, money — to recompute vectors that didn't change.
- **This module adds:** **chunking** (split each article into embeddable pieces
  _before_ embedding) and **content-hash idempotency** (skip any piece whose
  text hasn't changed).
- **New words:** chunk, chunk size, overlap, content hash / digest, idempotency.

---

## The idea in plain English

1. **Split long text into fixed-size windows of tokens.** Pick a size (say 500
   tokens) and cut the article into consecutive windows of that size. Each window
   becomes one chunk, gets its own embedding, and is retrieved on its own.
2. **Let consecutive windows overlap.** If you cut cleanly at token 500, a
   sentence straddling that boundary is torn in half — neither chunk holds the
   whole thought. So each chunk repeats the last N tokens of the one before it
   (say 50). The window advances by `size − overlap` tokens, not the full `size`.
3. **Fingerprint each chunk, and only embed new fingerprints.** Run each chunk's
   text through a **content hash** — a short string where identical text gives an
   identical hash and any edit gives a totally different one. Keep a cache of
   hashes you've already embedded. Before embedding a chunk, look up its hash: if
   it's there, skip the (slow, paid) embed call. Re-run on unchanged input →
   every hash is already cached → **zero** embeds. That property is called
   **idempotency**: running it again changes nothing and does no extra work.

---

## Worked example (read-only)

### Part A — chunking with overlap

Take this 20-token passage (a "token" here is just a word):

> _"Photosynthesis lets plants turn sunlight into food. Leaves capture light,
> and the plant stores energy as sugar for later growth."_

Chunk it with **size = 10, overlap = 3** (so the window advances `10 − 3 = 7`
tokens each step). You get **3 chunks**:

| chunk | tokens | text                                                                        | hash (first 12) |
| ----- | ------ | --------------------------------------------------------------------------- | --------------- |
| **0** | 1–10   | "Photosynthesis lets plants turn sunlight into food. Leaves capture light," | `684b617bdfeb`  |
| **1** | 8–17   | "Leaves capture light, and the plant stores energy as sugar"                | `56a9944d7f6e`  |
| **2** | 15–20  | "energy as sugar for later growth."                                         | `d76cd47c03a5`  |

**Why it lands this way:**

- **The overlap is visible.** "Leaves capture light," ends chunk 0 **and** starts
  chunk 1; "energy as sugar" ends chunk 1 **and** starts chunk 2. Those repeated
  tokens are the overlap — a phrase on a boundary survives whole in a chunk
  instead of being split.
- **The last chunk is short** (6 tokens). That's fine — the window just runs out
  of article. You stop once a window reaches the end; you don't keep emitting
  ever-tinier tail chunks.

### Part B — the content hash earns its keep

Now edit **one word** in that passage: `sugar` → `starch`. Re-chunk and compare
hashes to the run above:

| chunk | before         | after          | re-embed?                           |
| ----- | -------------- | -------------- | ----------------------------------- |
| 0     | `684b617bdfeb` | `684b617bdfeb` | **no** — identical text, cached hit |
| 1     | `56a9944d7f6e` | `7fa23c37a158` | **yes** — text changed              |
| 2     | `d76cd47c03a5` | `235fff64892b` | **yes** — text changed              |

**Why two chunks changed from a one-word edit:** the word `sugar` (token 17) sits
in the **overlap region** shared by chunks 1 and 2, so editing it touches both.
Chunk 0 never saw that word, so its hash is unchanged and it's skipped. That's the
payoff — you re-embed **2 chunks, not the whole article**, and untouched articles
cost nothing at all.

_(Every hash above is real — produced by SHA-256 over the chunk text, the same
code you're about to write.)_

---

## Your turn — build the chunker + idempotency check

Standalone folder `exercises/module-3-chunking/`. The plumbing (corpus loading,
a call-counting stub embedder, the CLI, and the glue that turns your chunks into
`Chunk` objects) is written. You write the chunking and hashing.

### 1. Set up (once)

```bash
cd exercises/module-3-chunking
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python chunk_cli.py
```

This reuses the **same 5k slice** Module 1 downloaded (in `../wikisearch/data/`).
If it says the corpus is missing, run `cd ../wikisearch && python setup_data.py`
once, then come back. `chunk_cli.py` will stop at the first unwritten function —
that's your starting line.

> There's **no embedding model** in this folder. The "embedder" is a stub that
> just counts how many times it's called — because the lesson is _not calling it_
> when nothing changed, not recomputing vectors (you did that in Module 2).

### 2. Fill in `chunking.py`

Three functions. Each has a docstring and numbered sub-steps; delete each
`raise NotImplementedError(...)` as you go:

- `chunk_fixed(tokens, size, overlap)` — slice a token list into fixed-size
  overlapping windows (the core of Part A).
- `content_hash(text)` — a hex SHA-256 fingerprint of a string (Part B).
- `embed_new_chunks(chunk_texts, cache, embedder)` — embed only the chunks whose
  hash isn't already in the cache; return how many you embedded. This is what
  makes re-runs free.

(`tokenize`, the `Chunk` type, and `chunk_document` / `chunk_corpus` are provided
— they _call_ your functions.)

**Stuck on a sub-step? Ask Claude.**

### 3. Check your work

When it's right, `python chunk_cli.py` prints (verified against the 5k slice):

```
loaded 5,000 articles
chunked into 10,299 chunks (size=500, overlap=50)
run 1 (nothing cached yet):  10,299 embeddings computed
run 2 (same input, warm cache):    0 embeddings computed   <-- should be 0

idempotent ✓  re-running on unchanged input did no embedding work.
```

Run 1 embeds every chunk; run 2 sees them all cached and does **nothing**. That
zero is the module.

### 4. Observe (fill in)

- `python chunk_cli.py --overlap 0` vs the default `--overlap 50` → does the
  **chunk count** change? Why? _fill in_
- `python chunk_cli.py --size 200` → more chunks or fewer? _fill in_
- In your own words: if an editor fixes a typo in the **middle** of a long
  article, roughly how many of that article's chunks re-embed — and how many of
  the _other 4,999 articles_ do? _fill in_

---

## Concepts to capture (your words → `glossary.md`)

- chunk
- chunk size & overlap _(what does more overlap buy you, and what does it cost?)_
- content hash / digest
- idempotency
- token vs. word _(you split on whitespace; note what a "real" token is — see the
  production footnote — and why the distinction matters for a model's input limit)_

Ask Claude to check your wording if you're unsure a definition is right.

---

## Optional — see it in production (5 min)

Only after your CLI reports `idempotent ✓`. Same repo as the earlier footnotes;
this module maps to **two** real files, one per idea:

- **Chunking** → `chunky-kong` →
  `lib/instinct/search/universal/sync/chunker.ex:16`
  - **Notice:** `@default_opts [target_tokens: 500, overlap_tokens: 50]` — the
    exact 500/50 you used as defaults. A few lines up (`:5`) it also notes
    _"Token estimation: 1 token ≈ 4 characters"_ — production doesn't run a full
    tokenizer either; it **approximates** tokens (by character count) just like
    you approximated them with words. Same windowing idea, same shortcut.
- **Content hashing** → `chunky-kong` →
  `lib/instinct/search/universal/sync/digest.ex:6`
  - **Notice:** inside `def sha256_hex(data)`, the whole implementation is one
    line: `:crypto.hash(:sha256, data) |> Base.encode16(case: :lower)` — the
    production digest is literally SHA-256 rendered as lowercase hex, the same
    fingerprint your `content_hash` returns. The sync pipeline compares these
    digests to decide whether a resource needs re-embedding at all.

---

## Open questions

- Even with overlap, a fixed window can cut across a section boundary. The raw
  Wikipedia text has blank-line (`\n\n`) breaks between sections — what would
  **section-aware** chunking (split on those first, then size-limit each section)
  buy you over blind fixed windows? What would it cost?
- You hashed each **chunk**. Production (`digest.ex`) also hashes the **whole
  resource**. When would a per-document digest save more work than per-chunk
  hashes, and when would it save less?
- _fill in your own_
