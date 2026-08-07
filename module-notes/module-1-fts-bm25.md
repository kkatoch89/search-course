# Module 1 — Full-Text Search & BM25

> **(read-only)** sections are for understanding; **Your turn** is what you
> build. Blanks marked _fill in_ are yours.

**Goal:** Give the WikiSearch engine its first capability — keyword search that
ranks Wikipedia articles by relevance with BM25.
**Time box:** ~2–3 hours  |  **Time spent:** _1.5h_  |  **Done when:** `python bm25_cli.py "photosynthesis"` returns a ranked list with _Photosynthesis_ on top.

---

## Where this fits (builds on Module 0)

- **Module 0 gave you:** the lay of the land — what search is for, the corpus
  (Simple English Wikipedia), and the vocabulary you're about to make concrete.
- **This module adds:** the first working retrieval step. Given a typed query,
  return the most relevant articles. This is the base of the engine every later
  module builds on (vectors, hybrid, reranking, …).
- **New words:** inverted index, tokenization, term frequency (TF), document
  frequency, inverse document frequency (IDF), length normalization, BM25.

---

## The idea in plain English

You have 5,000 articles. Someone types `photosynthesis`. How do you find the
best matches fast, and rank them?

1. **Don't scan every article per query.** Build an **inverted index** once: a
   map from each word to the list of documents containing it (and how often).
   Now answering a query is "look up the query's words," not "read 5,000 docs."
2. **First split text into words** — **tokenization**. `"The Red Fox!"` becomes
   `["the", "red", "fox"]`: lowercased, punctuation dropped. Query and documents
   get tokenized the same way so they can match.
3. **Rank by three intuitions**, which together are **BM25**:

- **Term frequency (TF):** a doc that uses the query word more is probably
  more about it — but with _diminishing returns_ (the 10th "fox" adds less
  than the 2nd).
- **Inverse document frequency (IDF):** a word in _few_ documents is more
  informative. Matching `photosynthesis` (rare) says more than matching
  `the` (everywhere), so rare words are weighted higher.
- **Length normalization:** a long document naturally repeats words, so BM25
  discounts length — a short doc that's squarely on-topic beats a long doc
  that merely mentions the word in passing.

That's it. BM25 turns those three signals into one relevance score per document,
and you sort by it.

---

## Worked example (read-only)

Tiny corpus of four documents. Query: `red fox`. Average length `avgdl`
across these four docs is **8.5 tokens**.

The two query words differ in how rare they are:

| query word | in how many docs (document frequency) | so its IDF weight is… |
| ---------- | ------------------------------------- | --------------------- |
| `red`      | 2 of 4                                | **higher** (rarer)    |
| `fox`      | 3 of 4                                | lower (more common)   |

Now the documents and their driving signals:

| doc   | text                                                                                   | length | tf(`red`) | tf(`fox`) | **BM25 score** |
| ----- | -------------------------------------------------------------------------------------- | ------ | --------- | --------- | -------------- |
| **A** | "The red fox."                                                                         | 3      | 1         | 1         | **1.428**      |
| **B** | "The red fox is a wild animal that lives in the forest and hunts small prey at night." | 18     | 1         | 1         | **0.720**      |
| **C** | "A fox, a fox, a clever fox."                                                          | 7      | 0         | 3         | **0.583**      |
| **D** | "The dog is a loyal pet."                                                              | 6      | 0         | 0         | **0.000**      |

**Ranking: A → B → C.** (D is _dropped_ — see why below.)

**Why each lands where it does:**

- **A is #1.** It has both query words and is extremely short. Length
  normalization rewards a doc that is _entirely_ about the query.
- **B is #2.** Identical query-word counts to A (`red`×1, `fox`×1) — but it's 18
  tokens vs. A's 3. _Nothing differs except length,_ so this pair isolates length
  normalization: the longer doc scores lower.
- **C is #3.** It says `fox` three times but never `red`. Piling up a _common_
  word (low IDF) can't out-score having the _rarer_ word `red` (high IDF) that
  both A and B carry. IDF beats raw repetition here.
- **D is dropped.** It contains neither query word, so its score is exactly 0.
  Zero-score docs aren't "ranked last" — they're not results at all.

(These scores are real — produced by running BM25 with the course's standard
settings k1 = 1.2, b = 0.75.)

---

## Your turn — give the engine keyword search

You'll implement BM25 inside the engine at `exercises/wikisearch/`. The plumbing
(data download, CLI, printing, loading the corpus) is already written. You write
the search itself.

### 1. Set up (once)

```bash
cd exercises/wikisearch
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python setup_data.py          # downloads a 5k slice; reruns do nothing
python bm25_cli.py "photosynthesis"
```

That last command runs, loads 5,000 articles, then stops at the first
unwritten function with a `NotImplementedError`. That's your starting line.

### 2. Fill in `wikisearch/bm25.py`

Four functions, top to bottom. Each has a docstring (what goes in / comes out)
and numbered sub-steps. Delete each `raise NotImplementedError(...)` as you go:

- `tokenize(text)` — text → list of lowercase terms.
- `build_index(docs)` — scan the corpus once into an `InvertedIndex`
  (postings, document frequencies, doc lengths, `avgdl`).
- `bm25_score(query_terms, doc_index, index)` — the score for one doc (the BM25
  formula is quoted at the top of the file).
- `search(query, index, docs, k)` — tokenize the query, score the candidate
  docs, drop zeros, return the top-k.

**Stuck on a sub-step? Ask Claude.**

### 3. Check your work

When it's right, `python bm25_cli.py "photosynthesis"` returns exactly this
(verified against the 5k slice):

```
 1. Photosynthesis          (score 11.423)
 2. Carbon dioxide          (score  8.181)
 3. Variegated leaf         (score  8.177)
 4. Plant                   (score  8.100)
 5. List of biochemistry topics  (score 7.630)
```

Scores may differ slightly if your tokenization differs, but _Photosynthesis_
should sit on top and the neighbors should be plant/biology articles.

### 4. Observe (fill in)

Run a couple of queries and jot what you notice:

- A precise, rare word (e.g. `photosynthesis`) → _result observation:_
- A short common word or a two-word phrase (try `red fox`) → _result
  observation:_   _(Hint: does the animal win? Why might a person named Fox
  or an article full of "red" out-rank it? Keep this in mind for Module 2.)_

### 5. Tag it

Once it works and is committed: `git tag end-of-m1`.

---

## Concepts to capture (your words → `glossary.md`)

Each of these was explained above; write them in your own words in
`glossary.md`. Some are already started there — refine them now that you've
built the thing:

- inverted index
- tokenization
- term frequency (TF)
- document frequency
- inverse document frequency (IDF)
- length normalization (and `avgdl`)
- BM25
- prefix matching _(not used above — define it from the reading; it's a
  match-time trick, not a scoring one)_

Ask Claude to check your wording if you're unsure a definition is right.

---

## Optional — see it in production (5 min)

Only after the engine works. One file, one thing to notice:

- **File:** `chunky-kong` → `lib/instinct/search/universal/clients/turbopuffer/ranking.ex:6`
- **Notice:** `def bm25(field, text), do: [field, "BM25", text]`. In production,
  a BM25 query isn't hand-rolled like yours — it's expressed as a single
  `[field, "BM25", text]` **rank_by clause** handed to Turbopuffer, which runs
  the same TF/IDF/length math you just implemented. Your toy engine and the real
  one compute the same thing; production just delegates the scoring to the
  search store.

---

## Open questions

- Why did `red fox` not return a fox article at the top? What would fix that?
- _fill in your own_
