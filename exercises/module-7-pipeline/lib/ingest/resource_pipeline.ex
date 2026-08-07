defmodule Ingest.ResourcePipeline do
  @moduledoc """
  The pipeline's state machine — THIS IS THE MODULE 7 EXERCISE.

  These are **pure functions**: they take a status (or a stage) and return the
  next one. No database, no Oban, no side effects — just the *shape* of the
  pipeline. That separation is deliberate and worth internalizing: the rules of
  the state machine live here where they're trivial to reason about and test,
  while the messy side effects (DB writes, calling the embedder, enqueuing jobs)
  live in the worker. chunky-kong does exactly this split — its
  `sync/resource_pipeline.ex` is "Pure functions for resource state transitions.
  Returns changesets — no database calls, no side effects."

  The pipeline has three units of work between four checkpoints:

      :pending --chunk--> :chunked --embed--> :embedded --store--> :indexed

  The worker (`Ingest.Worker`, written for you) looks at a resource's status,
  runs the one stage that comes next, and then calls YOUR `advance/1` to move it
  to the next checkpoint. If a stage fails, it calls YOUR `retry_target/1` to
  decide where to resume.

  The note (`module-notes/module-7-pipeline.md`) explains all of this and walks a
  worked example. Read it first. Stuck? Ask Claude.
  """

  @doc """
  Move a resource FORWARD one checkpoint after its current stage succeeded.

  Given the status the resource is at now, return the status it should be at
  once the next stage completes:

      advance(:pending)  => :chunked     # chunking finished
      advance(:chunked)  => :embedded    # embedding finished
      advance(:embedded) => :indexed     # storing finished — pipeline done

  Implement it with one function clause per arrow above (pattern-match the input
  status, return the next one). ``:indexed`` is terminal — the worker never calls
  advance on it, so you don't need a clause for it.
  """
  @spec advance(atom()) :: atom()
  def advance(status) do
    _ = status
    raise "TODO: implement advance/1 (see the arrows in the docstring)"
  end

  @doc """
  Decide where a resource should RESUME after a stage fails.

  When a stage raises, the worker marks the resource `:failed` and records which
  stage died (`:chunk`, `:embed`, or `:store`). On retry, we don't start over
  from scratch — we rewind to the checkpoint *just before* the stage that failed
  and run forward again. Because every stage is idempotent (re-chunking,
  re-embedding, re-storing the same content is safe), replaying from that
  checkpoint is correct:

      retry_target(:chunk) => :pending     # redo from the top
      retry_target(:embed) => :chunked     # chunks are durable; just re-embed
      retry_target(:store) => :embedded    # vectors are durable; just re-store

  Implement it with one function clause per arrow. (chunky-kong's
  `retry_target/1` does the same thing — rewind to the last durable checkpoint.)
  """
  @spec retry_target(atom()) :: atom()
  def retry_target(failed_stage) do
    _ = failed_stage
    raise "TODO: implement retry_target/1 (see the arrows in the docstring)"
  end
end
