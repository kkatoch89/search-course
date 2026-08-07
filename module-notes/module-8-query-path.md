# Module 8 — Query Path: Pagination & Sort Modes

> **(read-only)** sections are for understanding; **Your turn** is what you
> build. Blanks marked _fill in_ are yours.

**Goal:** Turn WikiSearch from "returns a ranked list" into something a real
search *product* can drive: **"load more"** that never repeats a result
(`excludeIds` pagination), and a **sort toggle** so the user can reorder results
by something other than relevance (A–Z, shortest-first).
**Time box:** ~1.5–2 hours &nbsp;|&nbsp; **Time spent:** _fill in_ &nbsp;|&nbsp; **Done when:** `python search_cli.py "big cat that lives in the jungle" --pages 2` prints two pages of five with **no title appearing twice**, and `--sort title` reorders a page alphabetically.

---

## Where this fits (builds on Module 4)

- **Module 4 gave you** a retriever: `search(...)` returns the top-k documents
  ranked by relevance (BM25 + vectors, fused). That's the _engine_.
- **This module adds** the two things a _product_ wraps around that engine, and
  both happen **after** retrieval:
  - **Pagination** — the user scrolled to the bottom and clicked "more". Return
    the _next_ batch without repeating anything already shown.
  - **Alternate sort** — the user clicked "sort: A–Z". Re-order the results by a
    key other than the score.
- **New words:** pagination, offset pagination, cursor / `excludeIds`
  pagination, sort mode, stable pagination, retrieve-then-present.
- **Note:** M8's code uses Module 4's `search` to fill a candidate pool — it does
  **not** need your Module 5 reranker. If M5 is still unwritten, M8 still runs.

> **This is an engine module** (like Module 4). You add to
> `exercises/wikisearch/` and finish with `git tag end-of-m8`.

---

## The idea in plain English

1. **A ranking isn't a product.** The engine hands back "the best 50 for this
   query, best first." A product has to decide _which slice_ of that to show
   (page 1? page 2?) and _in what order_ (by score? by name?). Those are two
   separate post-retrieval steps — you still **retrieve by relevance** (that's
   how you find the _right_ documents), then transform the list before showing it.

2. **Two ways to paginate — and why `excludeIds` wins.**
   - **Offset:** "skip 5, give me the next 5" → `results[5:10]`. Dead simple.
     But it silently breaks if the results shift between requests: a new doc
     lands at rank 3, everything below slides down one, and page 2 now _repeats_
     the doc that used to be rank 5. Offsets point at _positions_, and positions
     move.
   - **`excludeIds`:** the client remembers the ids it has already seen and asks
     for _"the best results that AREN'T these."_ Nothing can be duplicated or
     skipped, because you named exactly what to leave out. It points at
     _identities_, and identities are stable. This is what production search
     (merlin / chunky-kong) uses for "load more" — and it's the one you build.

3. **Sort reorders the pool you _retrieved_, not the whole corpus.** "Sort by
   title" means _"of the documents that matched this query, show them A–Z"_ —
   **not** "show me _Aardvark_ first regardless of what I searched for."
   Retrieval decides _which_ docs are in play; sort only decides the _order_ you
   present them in. Keep those two jobs separate and both stay simple.

---

## Worked example (read-only)

One real query against the 5k slice: **`big cat that lives in the jungle`** —
the same query from Module 4, so you already know the relevance order.

### Part 1 — pagination (`--sort relevance`, the default)

```
python search_cli.py "big cat that lives in the jungle" --pages 2
```

| page | rank | doc                              | score |
| :--: | :--: | -------------------------------- | :---: |
|  1   |  1   | Leopard                          | 0.999 |
|  1   |  2   | Jaguar                           | 0.965 |
|  1   |  3   | Cheetah                          | 0.842 |
|  1   |  4   | Tiger                            | 0.789 |
|  1   |  5   | Cat                              | 0.772 |
|  2   |  6   | Jungle                           | 0.729 |
|  2   |  7   | Lion                             | 0.619 |
|  2   |  8   | Snoopy                           | 0.557 |
|  2   |  9   | George of the Jungle             | 0.489 |
|  2   |  10  | Cartoonist                       | 0.419 |

Page 2 is the _next_ five, and **nothing from page 1 comes back**. That's
`excludeIds` doing its job: before fetching page 2, the CLI passed the five ids
from page 1 as "already seen", and `exclude_seen` dropped them from the pool.
The scores keep falling (0.999 → 0.419) because you're walking _down_ the same
one relevance ranking — page 2 is simply the less-relevant tail.

### Part 2 — a new sort mode (`--sort title`)

```
python search_cli.py "big cat that lives in the jungle" --sort title
```

| rank | doc                                | score |                                    |
| :--: | ---------------------------------- | :---: | ---------------------------------- |
|  1   | Anteater                           | 0.271 | 🤔 weak match, but "A" sorts first |
|  2   | Bear                               | 0.096 | 🤔                                 |
|  3   | Bigfoot                            | 0.076 | 🤔                                 |
|  4   | Camel                              | 0.091 | 🤔                                 |
|  5   | Canadian Broadcasting Corporation  | 0.407 | ❌ keyword junk from the pool      |

**Read this carefully — it's the whole lesson of sort modes.** Leopard and
Jaguar (the _best_ matches, score ~1.0) have vanished from page 1. Why? Because
`--sort title` **throws the score away** and orders by title instead, and "L"
and "J" come long after "A", "B", "C". The five docs above are just the
alphabetically-earliest members of the 50-doc relevance _pool_ — several of them
barely match the query at all.

That's not a bug; it's the nature of a non-relevance sort, and knowing it is the
point: **the moment you sort by anything other than relevance, your best matches
stop being at the top.** Real products deal with this by only offering A–Z on a
tight, already-relevant result set (or by keeping a relevance floor) — see the
Open Questions.

### Part 3 — the two compose

```
python search_cli.py "big cat that lives in the jungle" --pages 2 --sort title
```

Page 1 is the alphabetical five above; **page 2 continues the alphabet** with no
repeats — `Carnivore, Cartoonist, Cat, Cheetah, Dian Fossey`. Pagination
(exclude what's seen) and sort (reorder what's left) stack cleanly because they
run in that order: retrieve → exclude → sort → cut to the page.

_(Every title and score above is real — produced by the same `query.py` code
you're about to write, over the 5k slice.)_

---

## Your turn — give the engine pagination + sort

You implement two small, pure functions in a new file, **`wikisearch/query.py`**.
The plumbing is written: `paginated_search` (in the same file, below your
functions) retrieves the pool with Module 4's `search`, calls your two functions,
and cuts to the page; `search_cli.py` walks N pages and accumulates the seen-id
set for you.

### 1. Watch it stop (no code yet)

```bash
cd exercises/wikisearch
source .venv/bin/activate
python search_cli.py "big cat that lives in the jungle" --pages 2
```

It retrieves, then stops at the first unwritten function with
`NotImplementedError: Implement exclude_seen ...`. That's your starting line.

### 2. Fill in `wikisearch/query.py`

Two functions, top to bottom. Each has a docstring and numbered sub-steps;
delete each `raise NotImplementedError(...)` as you go. Everything keys on
`Document.id`, the stable id the searches hand back.

- `exclude_seen(results, seen_ids)` — return the results whose `doc.id` is **not**
  in `seen_ids`. One list comprehension. This is `excludeIds` pagination.
- `sort_results(results, sort)` — reorder by mode: `"relevance"` returns the list
  unchanged (it's already score-sorted), `"title"` sorts by `doc.title.lower()`,
  `"length"` sorts by `len(doc.text)` (shortest first); anything else raises
  `ValueError`.

(`paginated_search` and `search_cli.py` are provided — they _call_ your two
functions. You don't edit `hybrid.py`.)

**Stuck on a sub-step? Ask Claude.**

### 3. Check your work

When both are right, pagination shows two non-overlapping pages:

```
Page 1  (excluding 0 already-seen):
   1. Leopard  (score 0.999)
   ...
   5. Cat  (score 0.772)

Page 2  (excluding 5 already-seen):
   6. Jungle  (score 0.729)
   ...
  10. Cartoonist  (score 0.419)
```

and `--sort title` reorders page 1 to `Anteater, Bear, Bigfoot, Camel, Canadian
Broadcasting Corporation` (matching the worked example).

### 4. Observe (fill in)

- **Prove pagination is stable.** Run `--pages 3`. Do any titles ever repeat
  across the three pages? Why not? _fill in_
- **Sort surfaces the fringe.** In `--sort title`, the top matches (Leopard,
  Jaguar) disappear from page 1. Where do they end up — what page are they on
  now, and why there? _fill in_
- **Try `--sort length`.** `python search_cli.py "big cat that lives in the
  jungle" --sort length`. Are the shortest _relevant_ articles, or just the
  shortest articles that happened to be in the pool? What does that tell you
  about sorting a relevance pool by a field the query didn't ask about? _fill in_

### 5. Commit & tag

Once it works and is committed: `git tag end-of-m8`.

---

## Concepts to capture (your words → `glossary.md`)

- pagination
- offset pagination _(what shifts underneath it, and what goes wrong when it
  does?)_
- cursor / `excludeIds` pagination _(why does naming the ids you've seen make
  duplicates and skips impossible?)_
- sort mode _(what does it reorder — and what does it deliberately **not**
  touch?)_
- retrieve-then-present _(why keep "which docs" and "in what order" as two
  separate steps?)_

Ask Claude to check your wording if you're unsure a definition is right.

---

## Optional — see it in production (5 min)

Only after your CLI works. Both of this module's ideas are first-class fields on
chunky-kong's search request, and they're handled exactly the way you built them.

- **File:** `chunky-kong` →
  `lib/instinct/search/universal/query/request.ex`
- **Notice:** the request contract declares both knobs up front —
  `@valid_sorts [:best_match, :newest, :oldest, :created_newest, :created_oldest,
  :alphabetical]` (line 11) with `sort: :best_match` as the default (line 44),
  and `exclude_ids: []` (line 46) capped at `@max_exclude_ids 500` (line 17).
  `:best_match` is your `"relevance"`; `:alphabetical` is your `"title"`. The cap
  is a production detail worth clocking: an unbounded exclude list would grow
  forever as a user pages deeper, so they bound it at 500.
- **Where each one actually happens** (same two operations you wrote, one layer
  down):
  - `executor/filters.ex:114` — `maybe_add_exclude_ids` turns the id list into a
    `Filter.not_in("id", exclude_ids)` clause. That's your `exclude_seen`, except
    it's pushed **server-side** into the Turbopuffer query (the filtering you met
    in Module 6) instead of filtering a Python list after the fact — same
    logical "best results whose id ∉ excluded", different layer.
  - `hydrator.ex:76` — `case sort do :best_match -> Enum.sort_by(…, & &1.score,
    :desc); _ -> …` : for `:best_match` it re-sorts by score; for any other sort
    it preserves the upstream order. That's exactly your `sort_results` split
    (relevance = leave it; otherwise reorder).

---

## Open questions

- **Sort vs. relevance floor.** Your `--sort title` surfaced _Anteater_ and
  _Bigfoot_ over _Leopard_ because sort ignores the score. How would you stop a
  non-relevance sort from showing near-junk? (Options: sort only the top-N most
  relevant; drop anything below a score threshold before sorting; only offer A–Z
  once results are already tightly filtered.) What does each cost?
- **Client-side vs. server-side exclude.** Your engine excludes ids in Python
  _after_ retrieving 50; chunky-kong pushes `NotIn "id"` into the store so the
  excluded docs never come back at all. When does doing it in the store matter —
  what happens to your Python approach if a user pages past the 50-doc pool?
- **Why cap `exclude_ids` at 500?** A user who pages deep enough accumulates a
  huge "seen" set. What breaks first if you never cap it — and what should the
  product do when someone hits the cap?
- _fill in your own_
