# Module 9 — Query Understanding: Route, Rewrite & HyDE

> **(read-only)** sections are for understanding; **Your turn** is what you
> build. Blanks marked _fill in_ are yours.

**Goal:** Stop trusting the user to type a clean query. Add a **pre-retrieval**
layer that reads the raw query and reshapes it before it hits the engine: a
rule-based **router** that picks the retriever, an LLM **rewrite** that
compresses a rambling question into keywords, and **HyDE** that expands a
question into a hypothetical answer and searches with _that_.
**Time box:** ~2 hours &nbsp;|&nbsp; **Time spent:** _fill in_ &nbsp;|&nbsp; **Done when:** `python understand_cli.py "photosynthesis" --route` routes to `fts` **with no API key**, and (once your key is set) `python understand_cli.py "why do plants need sunlight to live" --strategy hyde --mode vector` prints a generated passage and returns _Photosynthesis_ at the top.

---

## Where this fits (builds on Module 8)

- **Module 8 was the _post_-retrieval half of the query path:** retrieve first,
  then transform the result _list_ (exclude what's seen, sort it).
- **This module is the _pre_-retrieval half:** transform the _query_ first, then
  retrieve. Same engine (`search` from Module 4) in the middle — you're just
  wrapping the other side of it now.

  ```
  Module 9 (pre)          Module 4          Module 8 (post)
  raw query ──►[ route / rewrite / hyde ]──►[ search ]──►[ exclude / sort ]──► page
  ```

- **New words:** query understanding, query rewrite, query expansion, HyDE
  (Hypothetical Document Embeddings), query router / routing, pre-retrieval vs.
  post-retrieval.
- **First module with an API key.** `route` is pure rules and needs **no key** —
  build and run it first. `rewrite` and `hyde` call a hosted LLM, so they need
  `ANTHROPIC_API_KEY` set (governance note is in Step 3, and in
  `wikisearch/llm.py`). M9 uses Module 4's `search`; it does **not** need your
  Module 5 reranker.

> **This is an engine module** (like Modules 4, 5, 8). You add to
> `exercises/wikisearch/` and finish with `git tag end-of-m9`.

---

## The idea in plain English

1. **The query the user types is not the query you should search.** People type
   "that red planet", or one bare proper noun, or a paragraph of rambling. The
   retriever matches whatever it's handed — so a messy query retrieves messy
   results. Query understanding is a cheap step that sits _in front of_ retrieval
   and fixes the query before it does any damage.

2. **Routing: use a cheap signal to pick the retriever.** You already have three
   modes (`fts`, `vector`, `hybrid`). A one-word lookup ("Leopard") or a quoted
   phrase wants exact **keyword** matching — vectors would only blur it. A
   natural-language question ("how do plants make food?") wants **meaning**
   matching too. You don't need a model to tell these apart — query _length_, a
   leading question word, or quotes are enough. That's `route`.

3. **Rewrite and HyDE are opposite moves — and each helps a _different_ weakness.**
   - **Rewrite _compresses_:** ask the LLM to turn "what is that red planet in the
     solar system" into `mars planet`. This helps most when the user danced
     _around_ the entity without naming it — the model knows "that red planet =
     Mars" and injects the word the retriever actually needs.
   - **HyDE _expands_:** a _question_ and the _article that answers it_ often share
     almost no words (the question is short and interrogative; the article is long
     and declarative). So instead of embedding the question, ask the LLM to
     _hallucinate a passage that looks like the answer_, and embed **that**. A fake
     answer sits far closer to the real answer in vector space than the bare
     question does. You never show the fake text to anyone — you only borrow its
     _shape_ to find the real, trustworthy document.

---

## Worked example (read-only)

Three real runs against the 5k slice.

> **Honesty note — read before the numbers.** The **route** decisions below are
> fully deterministic — rerun them and you get exactly these. For **rewrite** and
> **HyDE**, the _rewritten string_ and the _hypothetical passage_ are what an LLM
> _would_ produce; a real model writes its own wording and it varies run to run,
> so treat the transformed **text** as illustrative. But every **ranking** below
> is real — produced by running the actual engine with that exact text as input.
> The lesson is the _shift in the results_, and that shift is genuine.

### Part 1 — `route` (rule-based, no key)

```
python understand_cli.py "<query>" --route
```

| query                                  | route decision | why                          |
| -------------------------------------- | :------------: | ---------------------------- |
| `photosynthesis`                       |     `fts`      | 1 word → keyword lookup      |
| `Leopard`                              |     `fts`      | 1 word → keyword lookup      |
| `"table salt"`                         |     `fts`      | quoted → exact phrase        |
| `how do plants make food from sunlight`|    `hybrid`    | starts with "how" → question |
| `why is the sky blue?`                 |    `hybrid`    | ends "?" → question          |
| `big cat that lives in the jungle`     |    `hybrid`    | default (no keyword signal)  |

Cheap signals — word count, quotes, a leading question word — sort queries into
"keyword lookup" vs. "natural-language question" without a single model call.

### Part 2 — `rewrite` (compress to keywords)

Query: **`what is that red planet in the solar system`** (hybrid, weighted 0.5).

| # | BEFORE (raw query) | score |     | AFTER (rewritten → `mars planet`) | score |
|:-:| ------------------ | :---: | --- | --------------------------------- | :---: |
| 1 | List of planets    | 1.000 |     | **Mars**                          | 1.000 |
| 2 | Planet             | 0.844 |     | Mars (disambiguation)             | 0.762 |
| 3 | Jupiter            | 0.779 |     | List of planets                   | 0.723 |
| 4 | **Mars**           | 0.742 |     | Mars (mythology)                  | 0.672 |
| 5 | Solar System       | 0.712 |     | Asteroid belt                     | 0.646 |

The vague query buries the real answer at **#4**, under generic articles (_List
of planets_, _Planet_, _Jupiter_). The user never typed "Mars" — they typed
"that red planet." The LLM's job is exactly to know that "that red planet =
Mars" and put the word in, which promotes **Mars to #1**. (Notice the tail now
carries _Mars (mythology)_ and _(disambiguation)_ — naming an entity in bare
keywords also re-introduces its ambiguity. Hold that thought for the Open
Questions.)

### Part 3 — HyDE (expand to a hypothetical answer)

Query: **`why do plants need sunlight to live`** (vector mode). The illustrative
passage the LLM generates:

> _"Photosynthesis is the process by which green plants and some other organisms
> use sunlight to make their own food. Plants use energy from the sun, together
> with water and carbon dioxide, to produce glucose and oxygen. Chlorophyll in
> the leaves captures the light energy that this process needs."_

We embed **that passage** (not the question) and search:

| # | BEFORE (embed the question) | score |     | AFTER (embed the HyDE passage) | score |
|:-:| --------------------------- | :---: | --- | ------------------------------ | :---: |
| 1 | Plant                       | 0.592 |     | **Photosynthesis**             | 0.766 |
| 2 | **Photosynthesis**          | 0.522 |     | Plant                          | 0.700 |
| 3 | Air                         | 0.498 |     | Carbon dioxide                 | 0.552 |
| 4 | Soil                        | 0.468 |     | Cellular respiration           | 0.485 |
| 5 | Organism                    | 0.414 |     | Green                          | 0.479 |

**Read the shift.** The bare question drifts toward loosely-associated words
(_Air_, _Soil_, _Organism_) and leaves the true answer, _Photosynthesis_, at #2.
Searching with a passage that _looks like the answer_ promotes **Photosynthesis
to #1** and swaps the fringe for a coherent topical neighborhood (_Carbon
dioxide_, _Cellular respiration_) — the concepts a real photosynthesis article
sits next to. The passage's facts don't even have to be perfect; its _shape_ is
what did the work.

_(Every ranking above is real, from the 5k slice. The transformed text is
illustrative — your LLM will phrase it differently every run.)_

---

## Your turn — put an understanding layer in front of the engine

You implement three functions in a new file, **`wikisearch/understand.py`**. The
plumbing is written: `understood_search` (same file, below your functions)
transforms the query, then calls Module 4's `search`; `understand_cli.py` prints
both what understanding _decided_ and the results. The LLM wrapper lives in
`wikisearch/llm.py` (also done — you just call `llm.complete(prompt)`).

Do them in this order — you get a running win before you touch a key.

### 1. Watch it stop (no code, no key)

```bash
cd exercises/wikisearch
source .venv/bin/activate
python understand_cli.py "photosynthesis" --route
```

It loads the corpus, builds the indexes, then stops at the first unwritten
function with `NotImplementedError: Implement route ...`. That's your start.

### 2. Implement `route` (rule-based — no key needed)

Return `"fts"` or `"hybrid"` from cheap signals: quoted phrase or ≤2 words →
`fts`; a "?" ending or a leading question word (`QUESTION_WORDS` is provided) →
`hybrid`; otherwise default `hybrid`. Numbered sub-steps are in the docstring.
Re-run the command above — it should now route `photosynthesis` to `fts` and
return results. **Confirm it matches Part 1's table** before moving on.

### 3. Get an API key set up (governance — do this once)

`rewrite` and `hyde` call a hosted LLM, so you need a key **in your
environment** — never hardcoded, never pasted into a prompt or committed:

```bash
export ANTHROPIC_API_KEY="...your key..."   # from 1Password / your .envrc
pip install anthropic                        # already in requirements.txt
```

You're sending only your _search query_ to the model (public Wikipedia queries —
nothing sensitive), and the model is Haiku (small/cheap — a rewrite is a
lightweight call). If the key is missing, `llm.py` tells you exactly that instead
of crashing. See the full note at the top of `wikisearch/llm.py`.

### 4. Implement `rewrite` (compress → keywords)

Build a prompt that tells the model it's a search-query rewriter, hands it the
query, and demands **only** the rewritten keywords back (models love to add
"Sure! Here's..."). Call `llm.complete(prompt)`, return it stripped. Then:

```bash
python understand_cli.py "what is that red planet in the solar system" --strategy rewrite
```

The CLI prints what it rewrote your query _to_, then the results. Your wording
will differ from Part 2, but the **effect** should match: the real answer climbs.

### 5. Implement `hyde` (expand → hypothetical answer)

Same shape as `rewrite`, opposite intent: prompt the model for a short (2–4
sentence) encyclopedia-style passage that _would answer_ the query, return it.
Then:

```bash
python understand_cli.py "why do plants need sunlight to live" --strategy hyde --mode vector
```

It prints the passage it generated and searches with it. _Photosynthesis_ should
land at or near the top (Part 3).

### 6. Observe (fill in)

- **Route reads the original, searches the rewrite.** Run `--strategy rewrite
  --route` on a rambling query. Which text does `route` look at to pick the mode
  — the raw query or the rewritten one? Find the answer in `understood_search`
  and say why that's the right choice. _fill in_
- **HyDE is a vector trick.** Run the HyDE command with `--mode fts` instead of
  `--mode vector`. Does the hypothetical passage help keyword search the way it
  helped vector search? Why would embedding-vs-keyword change whether HyDE pays
  off? _fill in_
- **Rewrite can over-focus.** In Part 2 the rewrite pulled in _Mars
  (mythology)_. Try rewriting a query about an ambiguous word (e.g. something
  that could mean an animal _or_ a car/OS). What did bare keywords lose that the
  full sentence carried? _fill in_

### 7. Commit & tag

Once all three work and it's committed: `git tag end-of-m9`.

---

## Concepts to capture (your words → `glossary.md`)

- query understanding _(what step is it, and where does it sit relative to
  retrieval?)_
- query router / routing _(what signal picks the retriever — and why is a rule
  enough before you reach for a model?)_
- query rewrite _(what does it change, and which retrieval weakness does it fix?)_
- query expansion _(how is HyDE a kind of expansion?)_
- HyDE / hypothetical document embeddings _(why does embedding a fake **answer**
  beat embedding the **question** — what are you actually matching on?)_
- pre-retrieval vs. post-retrieval _(Module 9 vs. Module 8 — what's transformed in
  each?)_

Ask Claude to check your wording if you're unsure a definition is right.

---

## Optional — see it in production (5 min)

Only after your CLI works. Here's the honest state of it, and it's a useful one.

- **File:** `chunky-kong` →
  `lib/instinct/search/universal/query/request.ex`
- **Production _does_ do query understanding — but the cheap, rule-based kind,
  which is exactly your `route`.** `normalize_text/1` (lines 200–201) trims and
  collapses whitespace, and then `id_pattern`/`id_shaped?` (lines 222–236) sniff
  the query for an **ID shape** — a single alphanumeric token of 7+ chars
  containing a digit and no internal spaces (phone / microchip / insurance code).
  If it matches, it emits a `patient.identifier` iglob filter (line 208) _before_
  retrieval. That's the same instinct as your `route`: read a cheap signal off the
  raw query and reshape the search accordingly — no model required.
- **Production does _not_ do LLM `rewrite` or `hyde`.** The normalized text goes
  to Turbopuffer as typed; there's no query rewriter and no HyDE anywhere in the
  universal search. So Modules 4/5/6/8 lived _inside_ what prod does — this is the
  first module where your engine reaches _past_ it. LLM query understanding is a
  real, common technique, but it's an upstream/optional layer, and a lot of
  production search (including this one) ships without it. Knowing when it's worth
  the extra model call per query is the actual product judgment — see below.

---

## Open questions

- **When is query understanding worth a model call per query?** Every `rewrite`
  or `hyde` adds an LLM round-trip (latency + cost) in front of _every_ search.
  `route` is free. What kinds of query would you gate the LLM behind — i.e., only
  rewrite when the cheap `route` signal says it's a messy natural-language
  question? Sketch that gate.
- **Rewrite ambiguity.** Compressing to bare keywords re-introduced _Mars
  (mythology)_ / an animal-vs-car collision. The full sentence carried
  disambiguating context that the keywords threw away. How would you keep some of
  that context — rewrite to keywords _plus_ a one-line intent, or feed the LLM the
  top few current results and let it refine? What does each cost?
- **HyDE with a wrong hallucination.** The passage's facts don't reach the user,
  but what if the model hallucinates a passage about the _wrong_ topic entirely
  (misreads the query)? What does that do to retrieval, and how would you notice —
  is there a cheap check that the HyDE passage is on-topic before you trust it?
- **Router beyond rules.** Your `route` is three hand-written rules. Production
  routers sometimes use a tiny classifier or an LLM to pick strategy (or even
  which _index/namespace_ to hit). What would push you from rules to a learned
  router — and how would Module 13's eval harness tell you it was actually better?
- _fill in your own_
