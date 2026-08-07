# Module 5 — Cross-Encoder Reranking

> **(read-only)** sections are for understanding; **Your turn** is what you
> build. Blanks marked _fill in_ are yours.

**Goal:** Add a second, smarter pass to WikiSearch: after Module 4's fast hybrid
ranker narrows 5,000 docs to a short candidate list, a **cross-encoder** re-reads
each candidate *alongside the query* and re-sorts them — the "retrieve then
rerank" pattern that powers modern search. ★ portfolio demo.
**Time box:** ~2 hours &nbsp;|&nbsp; **Time spent:** _fill in_ &nbsp;|&nbsp; **Done when:** `python rerank_cli.py "how do plants make food from sunlight"` shows _Photosynthesis_ jump from #2 (hybrid) to **#1** after reranking — the article that actually answers the question rises to the top.

---

## Where this fits (builds on Module 4)

- **Module 4 gave you** a fast hybrid ranker that scans all 5,000 docs in
  milliseconds using *cheap* signals: keyword overlap (BM25) and pre-computed
  vector similarity. It's a great **retriever** — good at pulling a handful of
  plausible candidates out of thousands.
- **The limit of cheap signals:** neither ranker ever looked at the query and a
  document *together*. BM25 counts shared words; the vector score compares two
  summaries (embeddings) that were computed *separately, in advance*. So hybrid
  can rank a generic article above the one that precisely answers the question.
- **This module adds:** a **rerank** pass — a slower, more accurate model that
  reads each (query, document) pair jointly and re-scores just the top
  candidates. The engine now runs in two stages: **retrieve** (Module 4, over
  all docs) → **rerank** (this module, over ~50 candidates).
- **New words:** cross-encoder, bi-encoder, retrieve-then-rerank (two-stage
  retrieval), candidate set / candidate depth, reranking latency-cost tradeoff.

> **This is an engine module.** You add to `exercises/wikisearch/` and finish
> with `git tag end-of-m5`.

---

## The idea in plain English

1. **Two stages, two speeds.** Running the accurate-but-slow model over all
   5,000 docs on every query would be far too slow. So you don't: a *cheap*
   ranker (Module 4 hybrid) first narrows 5,000 → ~50 candidates in
   milliseconds, and the *expensive* model only re-scores those 50. Cheap-and-
   wide then accurate-and-narrow. This is how almost every serious search system
   is built.

2. **Bi-encoder vs. cross-encoder — the key distinction.** Module 2's embedder
   is a **bi-encoder**: query → one vector, each document → its own vector,
   *separately*, and you compare the vectors afterward. Fast, because you embed
   the docs once up front — but the model never sees the query and a document at
   the same time. A **cross-encoder** feeds the query and one document into the
   model **together** as a single input and reads out one relevance score.
   Because it can weigh "does *this* passage actually answer *this* query?", it's
   much more accurate — but it can't precompute anything, so it costs one model
   call *per candidate, per query*. That's exactly why you only run it on the
   short candidate list, never the whole corpus.

3. **The score is a raw relevance logit — only the order matters.** Unlike
   cosine (−1..1) or your normalized fusion scores (0..1), a cross-encoder
   returns an unbounded number that can be **negative**. Don't read it as a
   probability. It exists only to *sort* the candidates. (You'll see #1 score
   `+2.07` while #3 scores `−1.6` in the example below — the negatives are fine.)

---

## Worked example (read-only)

One real query against the 5k slice: **`how do plants make food from sunlight`**.
The retriever (Module 4 hybrid, weighted 0.5/0.5) hands over 50 candidates; here
are its top 5, then what the cross-encoder does to them.

**BEFORE — hybrid retriever order** (normalized fusion scores, 0..1):

| rank | doc | score | |
| :--: | --- | :---: | --- |
| 1 | **Plant** | 0.851 | 🤔 generic — *about* plants, doesn't answer "how" |
| 2 | Photosynthesis | 0.777 | ✅ the actual answer, but stuck at #2 |
| 3 | Seed | 0.669 | 🤔 related, not the answer |
| 4 | Tropical rainforest | 0.457 | 🤔 |
| 5 | Food | 0.439 | ❌ matches the word "food" |

**AFTER — cross-encoder rerank** (raw relevance scores; note the negatives):

| rank | doc | ce score | |
| :--: | --- | :----: | --- |
| 1 | **Photosynthesis** | 2.067 | ✅ promoted #2 → #1 |
| 2 | Plant | 0.474 | ✅ still relevant, but demoted below the real answer |
| 3 | Tree | −1.605 | ✅ pulled in from deeper in the candidates |
| 4 | Carbon dioxide | −1.753 | ✅ a photosynthesis input — genuinely on-topic |
| 5 | Seed | −1.787 | |

**Why the reranked list is better:**

- **It promotes the article that answers the question.** Hybrid ranked the
  generic *Plant* above *Photosynthesis* — "plants" is a strong keyword and
  vector match for the *topic*. But the query asks *how plants make food from
  sunlight*, and the cross-encoder, reading query and passage together,
  recognizes that *Photosynthesis* is what actually answers it. It floats to #1
  with a score (`2.067`) far clear of everything else.
- **It reshapes the whole list, not just the top swap.** *Tree* and *Carbon
  dioxide* — both genuinely tied to photosynthesis — are pulled up from deeper in
  the 50 candidates, displacing "Tropical rainforest" and the bare keyword match
  "Food."
- **The gap is legible.** #1 sits at `+2.07`; the rest drop off a cliff into
  negatives. The cross-encoder is *confident* about the winner in a way the
  bunched-up fusion scores (0.85, 0.78, 0.67…) weren't.

**Why this needed a cross-encoder and hybrid couldn't do it:** to hybrid,
"Plant" and "Photosynthesis" look almost equally on-topic — both are dense with
plant/sunlight/food words and vectors. Telling apart *the topic* from *the
answer to the question* needs a model that reads the query and the passage
**together**. That's the one thing a bi-encoder structurally can't do, and the
one thing a cross-encoder is for.

_(Every number above is real — produced by the same rerank code you're about to
write, over the 5k slice.)_

---

## Your turn — give the engine a rerank pass

The plumbing is written: `rerank_cli.py` runs the Module 4 hybrid retriever to
get 50 candidates, prints them (BEFORE), then hands them to **your** function and
prints the result (AFTER). The cross-encoder model is wrapped for you in
`wikisearch/cross_encoder.py` — you just call `model.score(pairs)`.

### 1. See what the retriever hands you (no code yet)

```bash
cd exercises/wikisearch
source .venv/bin/activate
python rerank_cli.py "how do plants make food from sunlight"
```

It prints the BEFORE list (hybrid's top 5), then — because you haven't written
the rerank yet — stops at the one unwritten function and says so. That's your
starting line. (The first run also downloads the cross-encoder, ~80 MB, once.
Public HuggingFace model, no API key.)

> Hybrid mode reuses your Module 4 `fusion.py`. If the BEFORE list errors instead
> of printing, finish Module 4 first — the gating is intentional.

### 2. Fill in `wikisearch/rerank.py`

One function, `rerank(query, candidates, model, k)`. It has a reference block, a
docstring, and numbered sub-steps; delete the `raise NotImplementedError` when
done. The shape:

1. Build one `(query, doc.text)` pair per candidate — the cross-encoder reads the
   **actual passage**, not just the title, and reads it **with** the query.
2. Score all the pairs in one `model.score(pairs)` call (one number per pair,
   same order).
3. Re-pair each document with its **new** score (throw away the retriever score —
   replacing it with a better one is the whole point).
4. Sort by the new score, highest first, keep the top `k`.

**Stuck on a sub-step? Ask Claude.**

### 3. Check your work

When it's right, the default query prints (verified on the 5k slice):

```
BEFORE rerank — top 5 of 50 candidates (retriever order):
   1. Plant  (retriever score 0.851)
   2. Photosynthesis  (retriever score 0.777)
   3. Seed  (retriever score 0.669)
   4. Tropical rainforest  (retriever score 0.457)
   5. Food  (retriever score 0.439)

AFTER cross-encoder rerank — top 5:
   1. Photosynthesis  (ce score 2.067)
   2. Plant  (ce score 0.474)
   3. Tree  (ce score -1.605)
   4. Carbon dioxide  (ce score -1.753)
   5. Seed  (ce score -1.787)
```

_Photosynthesis_ moved from #2 to #1, and the list is now denser with genuinely
on-topic articles. That top swap is the whole module in one line.

### 4. Observe (fill in)

- **Rerank rescues a wrong #1.** Run:
  ```bash
  python rerank_cli.py "a large body of salt water"
  ```
  Hybrid's BEFORE list puts *Table salt* at #1 (strong keyword/vector match for
  "salt water" — but table salt isn't a body of water). Where does *Salt water*
  land before vs. after reranking, and what happened to *Table salt*? _fill in_
- **Candidate depth.** Rerun the plants query with `--candidates 10` and then
  `--candidates 100`. Does the top result change? What are you trading when you
  rerank more candidates? _fill in_ &nbsp; _(hint: the cross-encoder runs once
  per candidate — time it.)_
- **When rerank *hurts* (or can't help).** Try:
  ```bash
  python rerank_cli.py "a reptile that can change color"
  ```
  There's no great answer in the 5k slice (no *Chameleon* article), so watch what
  the cross-encoder promotes. What does this tell you about the limit of
  reranking — what can it *not* fix? _fill in_ &nbsp; _(A reranker only reorders
  what retrieval already found. Garbage in, garbage out.)_

### 5. Commit & tag

Once it works and is committed: `git tag end-of-m5`.

---

## Concepts to capture (your words → `glossary.md`)

- cross-encoder _(what does it see that a bi-encoder can't?)_
- bi-encoder _(why is it fast enough to run over the whole corpus?)_
- retrieve-then-rerank / two-stage retrieval _(why not just run the accurate
  model over everything?)_
- candidate set / candidate depth _(what does reranking more candidates buy, and
  cost?)_
- reranking latency-cost tradeoff _(where does the cross-encoder's cost come
  from — per query? per doc?)_

Ask Claude to check your wording if you're unsure a definition is right.

---

## Optional — see it in production (5 min)

Only after your CLI works. This one's a plot twist worth the click:

- **File:** `chunky-kong` →
  `lib/instinct/search/universal/query/executor/retrieval.ex`
- **Notice:** production has a two-stage retrieve-then-rerank shape *just like
  yours* — the module doc (line 3, "vector rerank") and lines 5–8 describe the
  `:fts_then_vector` strategy: pass 1 runs FTS, then **"pass 2 runs a vector ANN
  rerank scoped to pass-1 candidate IDs,"** and **"pass 1 over-fetches
  (`limit * 2`) when reranking is expected so pass 2 has headroom."** That
  over-fetch-before-rerank is exactly your `--candidates 50`. **But the plot
  twist:** production's "rerank" is *not* a cross-encoder — it's the same
  bi-encoder vector similarity from Module 2, just applied to the narrowed FTS
  candidate set. (The `reranker.ex` you met in Module 4 then fuses the two
  scores.) So production chose the *cheaper* reranker. Same two-stage **shape**,
  different pass-2 **model** — which sets up the open question below.

---

## Open questions

- **Cross-encoder vs. cheaper reranker — when is the accuracy worth it?** Your
  engine reranks with a cross-encoder (most accurate, but one model call per
  candidate at query time). Production reranks with a bi-encoder vector pass (no
  extra model, no extra latency, slightly less accurate). What would push you
  toward the cross-encoder — query volume, latency budget, how often the top
  result is subtly wrong? When is "good enough and fast" the right call?
- **How deep should the candidate set be?** Rerank the top 10, 50, or 200? Too
  shallow and a great doc the retriever buried never gets a second look; too deep
  and you pay the cross-encoder cost for junk. What decides the number?
- **The cross-encoder only sees the first ~512 tokens** of each article (it
  truncates long passages). For a long Wikipedia article, the answer might be
  further down. How does this connect back to **Module 3 chunking** — should you
  rerank whole documents, or their best chunk? _(Hint: real systems rerank
  chunks.)_
- _fill in your own_
