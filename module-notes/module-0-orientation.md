# Module 0 — Orientation

**Goal:** see the whole system before zooming in.
**Time spent:** _fill in_
**Date completed:** _fill in_

## What I read

- [x] `chunky-kong/lib/instinct/search/universal/README.md`
- [ ] _other_

## Codebase walk

Trace `Universal.search/1` → `Planner.plan/1` → `Executor.run/1` → `Hydrator.hydrate/3`.

- File: `lib/instinct/search/universal/universal.ex` — _what does it do?_
  - What I think it does:
    - I'm confused about this file. The moduledoc states that it's a public API but I thought a public API would either be the defined schema that a consumer of the API sees or the router for endpoints. This seems like the initial point of entry for the search feature
- File: `lib/instinct/search/universal/query/planner.ex` — _what does it do?_
  - What I think it does:
    - This file does all the preprocessing of requests and builds the datashape for business logic functions
    - Also I think this creates some sort of plan based off the namespaces that qualify for the query
- File: `lib/instinct/search/universal/query/executor.ex` — _what does it do?_
  - What I think it does:
    - I didn't quite understand what this does. All I know is that there's a pipeline that goes in the following order - prepare -> retreive -> finalize. But I have no clue what it's preparing, what it's retreiving or what it's finalizing. There's mention about gates, metadata, etc, I have no clue what these are
- File: `lib/instinct/search/universal/query/hydrator.ex` — _what does it do?_
  - What I think it does:
    - Enriches the response with additional data that's used by the UI. But what additional data, I'm not sure.

## Exercise: "What happens when a user types 'amoxicillin'?"

_Write your answer here in your own words._
My answer:

- if only the string 'amoxicillin' is sent in the request:
  1. The single arity search function that accepts a string type will be invoked
     a. Creates a new Request struct, normalizes the string and adds to the struct. Struct is returned
     b. the single arity search function that accepts a Request struct is then invoked
  2. search(%Request{text: text, sort: sort} = request)
     a. invokes Planner.plan with the Request struct
     b. Planner.plan invokes RequestFilter.normalize_list which takes the request.filters and creates a new Request struct for each filter (not 100% sure about this)
     c. A Plan struct is created and returned. The targets field in the struct is a result of Namespaces.query_facing |> Enum.flat_map(fn namespace -> ...) I didn't quite understand what's going on here
  3. I didn't quite understand what's happening in Executor.run
  4. Hydrator.hydrate then enriches the response with additional data to be used by the UI

## Glossary additions

_List terms you added to glossary.md._
I'm not sure, what terms do you think I should have added to the glossary.md file?

## Open questions

- _things I don't yet understand_
  What I don't understand:
- What's a callback in the context of lib/instinct/search/universal/namespaces.ex? Is a callback like a webhook (ie. a function that can be called?)
- Is lib/instinct/search/universal/namespaces.ex a behaviour module?
- In lib/instinct/search/universal/query/filter.ex it states " Filters are tagged tuples — provider-agnostic by design. Adapters translate `Filter.t()` values to whatever wire format their provider expects." What are the "providers" in this context?
