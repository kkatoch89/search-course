# Module 4 — Hybrid Search & Score Fusion

> **(read-only)** sections are for understanding; **Your turn** is what you
> build. Blanks marked _fill in_ are yours.

**Goal:** Make WikiSearch run BM25 and vector search _together_ and fuse their
results into one ranking that's better than either alone — the first version of
the engine you'd actually show someone. ★ portfolio demo.
**Time box:** ~2–3 hours &nbsp;|&nbsp; **Time spent:** _fill in_ &nbsp;|&nbsp; **Done when:** `python hybrid_cli.py "big cat that lives in the jungle"` returns five big cats with _Leopard_ on top — and the keyword junk ("Canadian Broadcasting Corporation") that plain BM25 shows is gone.

---

## Where this fits (builds on Modules 1 & 2)

- **Module 1 gave you** keyword search (BM25): great when the query's exact
  words appear, but blind to meaning and easily fooled by common words.
- **Module 2 gave you** vector search: great at meaning, but it can rank things
  by "vibe" and miss an obvious exact-keyword hit.
- **You already saw them disagree.** In Module 2's closing question you ran the
  same query through both and each missed what the other caught. This module
  answers that question: **run both, then fuse.**
- **This module adds:** score **fusion** — one ranking built from two. Two
  standard recipes: **weighted fusion** (rescale both score lists to a common
  range, then average) and **reciprocal rank fusion / RRF** (fuse on rank
  position, ignoring the raw scores).
- **New words:** hybrid search, score fusion, score normalization (min-max),
  weighted fusion, reciprocal rank fusion (RRF), over-fetching.

> **This is an engine module** (unlike the Module 3 satellite). You add to
> `exercises/wikisearch/` and finish with `git tag end-of-m4`.

---

## The idea in plain English

1. **Two rankers, two blind spots — so use both.** Hybrid search runs BM25 and
   vector search on the same query and combines their two result lists into one.
   Where they agree, you get a strong signal; where one is fooled, the other can
   pull the ranking back toward sense.

2. **You can't just add the two scores.** A BM25 score might be **15.0** while a
   cosine similarity is **0.48** — completely different scales. Add them raw and
   BM25 utterly dominates; the vector score barely moves the total. Two fixes:
   - **Weighted fusion:** first **normalize** each list to a common 0–1 range
     (min-max: smallest → 0, largest → 1), _then_ take a weighted average,
     `weight·fts + (1−weight)·vec`. The weight is a knob for how much you trust
     keywords vs. meaning.
   - **RRF:** throw the raw scores away entirely and fuse on **rank position** —
     a doc at rank _r_ contributes `1 / (60 + r)`, summed across the lists it
     appears in. Because it only looks at ranks, the incompatible 15.0-vs-0.48
     scales never come up. It's simple and surprisingly hard to beat.

3. **Over-fetch before you fuse.** A doc can be #1 for one ranker and _absent_
   from the other's top 5. So ask each ranker for a deep list (the engine
   fetches **50** from each), union them, fuse, and only _then_ cut to the final
   k. Fuse on tiny top-5 lists and you'd never even see the doc one ranker
   buried.

---

## Worked example (read-only)

One real query against the 5k slice: **`big cat that lives in the jungle`**.
Here's the top 5 from each ranker on its own, then fused.

**Module 1 — BM25 alone** (keyword; raw scores):

| rank | doc                                   | score |                                        |
| :--: | ------------------------------------- | :---: | -------------------------------------- |
|  1   | Leopard                               | 15.00 | ✅ a jungle cat                        |
|  2   | Jaguar                                | 14.64 | ✅ a jungle cat                        |
|  3   | **Cartoonist**                        | 13.69 | ❌ junk — matches "big"/"that"/"lives" |
|  4   | **Canadian Broadcasting Corporation** | 13.49 | ❌ junk                                |
|  5   | Cheetah                               | 12.84 | ✅                                     |

**Module 2 — vector alone** (meaning; cosine):

| rank | doc      | cosine |                                       |
| :--: | -------- | :----: | ------------------------------------- |
|  1   | **Lion** | 0.482  | 🤔 a big cat, but savanna, not jungle |
|  2   | Leopard  | 0.481  | ✅                                    |
|  3   | Tiger    | 0.477  | ✅                                    |
|  4   | Jaguar   | 0.475  | ✅                                    |
|  5   | Cat      | 0.474  | 🤔 not "big"                          |

**Hybrid — weighted fusion, 0.5 / 0.5** (what you'll build):

| rank | doc         | fused |     |
| :--: | ----------- | :---: | --- |
|  1   | **Leopard** | 0.999 | ✅  |
|  2   | Jaguar      | 0.965 | ✅  |
|  3   | Cheetah     | 0.842 | ✅  |
|  4   | Tiger       | 0.789 | ✅  |
|  5   | Cat         | 0.772 | ✅  |

**Why the fused list beats both:**

- **It purges BM25's junk.** "Cartoonist" and "Canadian Broadcasting
  Corporation" scored high on keywords alone (they contain common words like
  "big", "that", "lives"), but they mean _nothing_ like the query, so their
  vector score is near zero and the average drops them out of the top 5.
- **It fixes vector's ordering.** Vector alone put _Lion_ first — a big cat, but
  not a jungle one. BM25 strongly favors the jungle-dwelling Leopard and Jaguar
  (they're the best keyword matches too), so fusion floats them back to the top.
- **The winners are the docs both rankers liked.** Leopard and Jaguar are top-2
  for _both_ signals; agreement is what fusion rewards.

**Why you can't skip normalization:** look at Leopard — BM25 **15.00**, cosine
**0.481**. If you added those raw, the BM25 number is ~30× bigger, so the cosine
would be rounding error and "hybrid" would just be BM25 with extra steps.
Min-max rescales both lists to 0–1 _first_, so a top keyword hit and a top
meaning hit carry comparable weight.

_(Every number above is real — produced by the same fusion code you're about to
write, over the 5k slice.)_

---

## Your turn — give the engine hybrid search

You implement the fusion inside the same engine at `exercises/wikisearch/`. The
plumbing is written: `hybrid.py` runs both searches, over-fetches 50 from each,
and hands the two lists to **your** functions; `hybrid_cli.py` prints results.

### 1. See the two rankers disagree first (no code yet)

```bash
cd exercises/wikisearch
source .venv/bin/activate
python hybrid_cli.py "big cat that lives in the jungle" --mode fts
python hybrid_cli.py "big cat that lives in the jungle" --mode vector
```

`--mode fts` and `--mode vector` work right away — they reuse your Module 1 and
Module 2 code. Eyeball the two lists: FTS shows the junk, vector shows _Lion_
first. Now you'll fuse them.

### 2. Fill in `wikisearch/fusion.py`

Three functions, top to bottom. Each has a reference block, a docstring, and
numbered sub-steps; delete each `raise NotImplementedError(...)` as you go.
Everything keys on `Document.id` (the stable id the searches return):

- `min_max_normalize(scores)` — rescale one `{doc_id: score}` map to 0–1.
- `weighted_fusion(fts_scores, vec_scores, weight_fts)` — normalize each, then
  blend over the union of doc ids (a doc missing from one side contributes 0).
- `reciprocal_rank_fusion(fts_ranked_ids, vec_ranked_ids, k=60)` — fuse two
  _ranked_ lists by position: `1 / (k + rank)`, summed across lists.

(`hybrid.py`'s `build_index` / `search` and the CLI are provided — they _call_
your functions. Default mode is `hybrid`, so once these work,
`python hybrid_cli.py "..."` fuses; until then it stops at the first one.)

**Stuck on a sub-step? Ask Claude.**

### 3. Check your work

When it's right, the default (weighted 0.5/0.5) prints (verified on the 5k slice):

```
Top 5 results for "big cat that lives in the jungle"  [mode=hybrid (fusion=weighted, weight_fts=0.5)]:

 1. Leopard  (score 0.999)
 2. Jaguar  (score 0.965)
 3. Cheetah  (score 0.842)
 4. Tiger  (score 0.789)
 5. Cat  (score 0.772)
```

All five are big cats, Leopard is #1, and the keyword junk is gone. Try RRF too
— same idea, different math:

```bash
python hybrid_cli.py "big cat that lives in the jungle" --fusion rrf
# 1. Leopard  2. Jaguar  3. Tiger  4. Cheetah  5. Cat   (scores near 0.03)
```

### 4. Observe (fill in)

- **The weight knob.** Run the _same_ query both ways:
  ```bash
  python hybrid_cli.py "a game played with a bat and ball" --weight 0.7   # leans keyword
  python hybrid_cli.py "a game played with a bat and ball" --weight 0.3   # leans meaning
  ```
  The #1 result **flips** between two sports. Which wins at 0.7 vs 0.3, and why
  does leaning toward keywords vs. meaning pick that one? My answer: For the query "a game played with a bat and ball", both keywords and meaning did pretty well overall. If I had to pick one, I'd go with the semantic meaning weighted search. This is due to the first 2 results (cricket & baseball) being a lot closer to each other (for some reason the keyword search docked cricket more points than baseball when compared to semantic meaning). For the rankings 3 onwards, it's hard to determine which one is better as both methods gave a significantly dropped score for sports below the #2 rank.
- **Weighted vs. RRF.** Find a query where the two fusion methods disagree on
  the top result. Which did you trust more, and why? My answer: "Python attack vector" is a very contextual query that resulted in the semantic search significantly outperforming the BM25 method. Semantic search understood the underlying malicious meaning and thus provided "Hacker" and "Enemy" as the top 2 results; meanwhile BM25 returned "Vector" and "Douglas Adams"
- **When hybrid _hurts_.** Find a query where plain `--mode fts` or
  `--mode vector` actually beat `--mode hybrid`. What kind of query was it?
  _fill in_ &nbsp; _(hybrid isn't a free win — knowing when it backfires is the
  real skill.)_ My answer: Couldn't find a query that resulted in fts outperforming hybrid but I can only assume fts would outperform hybrid on ultra specific queries (eg. "Bill Gates" or "French Revolution")

### 5. Commit & tag

Once it works and is committed: `git tag end-of-m4`.

### Optional — scale it up to the full 226k corpus

Everything above runs on the 5k slice (fast, already embedded). Going to the
full ~226k-article corpus is a real project, not a flag — and a good one for the
portfolio — but know what it costs before you start:

- `python setup_data.py --full` downloads ~230 MB **and rebuilds the 5k slice as
  a different random subsample** — which invalidates your cached
  `embeddings_5k.npy` and would change every verified number above. Back up
  `data/` first if you want to keep this module's exact results.
- Embedding 226k articles locally on CPU is slow (tens of minutes) and the
  vector cache grows to ~350 MB.

That pain is the point: scoring every one of 226k vectors in a Python loop on
your laptop is exactly what you _shouldn't_ do in production. **Module 6** swaps
this for a real vector store (Turbopuffer) that indexes the vectors and answers
in milliseconds. Treat 226k as the motivation for that module rather than a
required step here.

---

## Concepts to capture (your words → `glossary.md`)

- hybrid search
- score normalization (min-max) _(why is it required before adding two score
  lists? what breaks without it?)_
- weighted fusion _(what does the weight trade off?)_
- reciprocal rank fusion (RRF) _(why does fusing on rank sidestep the problem
  normalization solves?)_
- over-fetching _(why fetch 50 from each ranker when you only return 5?)_

Ask Claude to check your wording if you're unsure a definition is right.

---

## Optional — see it in production (5 min)

Only after your CLI works. WikiSearch's hybrid mode has a direct counterpart:

- **File:** `chunky-kong` →
  `lib/instinct/search/universal/query/reranker.ex`
- **Notice:** the module doc (line 13) spells out the fusion formula —
  `final = w_fts * normalized_fts + w_vector * (1 - cosine_distance)` — which is
  your `weighted_fusion` almost verbatim: normalize the FTS side, take
  `1 - cosine_distance` as the meaning score (that's just cosine similarity),
  and combine with weights. `@default_weights [fts: 0.5, vector: 0.5]` (line 33)
  is the exact 0.5/0.5 default you used, and line 19 notes that a doc returned by
  FTS but not by vectors "retain[s] only their FTS contribution" — the same
  _missing-side-counts-as-0_ rule your `.get(id, 0.0)` gives you.

---

## Open questions

- **Production is FTS-_gated_, your engine is a _union_.** In `reranker.ex`,
  vectors only re-rank docs that FTS already returned — a doc absent from the FTS
  gate is dropped entirely. Your hybrid instead _unions_ both top-50 lists, so a
  strong vector-only hit can still surface. What does each choice trade
  (recall vs. precision vs. cost)? When would gating lose a good result?
- **Why 60?** RRF's `k = 60` is a convention from the original paper (Cormack et
  al., "Reciprocal Rank Fusion outperforms Condorcet…"). What does making `k`
  bigger or smaller do to how much rank-1 outweighs rank-10? _(Try editing it.)_
- _fill in your own_
