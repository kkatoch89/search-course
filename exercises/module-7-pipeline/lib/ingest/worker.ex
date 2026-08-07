defmodule Ingest.Worker do
  @moduledoc """
  The Oban worker that drives one resource through the pipeline — plumbing.

  This is the "side effects" half (the pure half is `Ingest.ResourcePipeline`,
  which you write). Each time Oban runs this job it:

    1. loads the resource,
    2. if it's `:failed`, rewinds to `ResourcePipeline.retry_target/1`,
    3. runs the stage due at its current checkpoint (chunk / embed / store),
    4. on success, moves it forward via `ResourcePipeline.advance/1` and
       continues to the next stage until `:indexed`,
    5. on failure, records the failed stage and returns `{:error, _}` so Oban
       retries the job (up to `max_attempts`, with backoff).

  The actual chunk/embed/store work is STUBBED — this module is about the
  *pipeline*, not recomputing vectors (you did the real chunk/embed/store in
  Modules 3/2/6). The embed step is deliberately flaky so you can watch a retry.
  """
  use Oban.Worker, queue: :ingest, max_attempts: 5

  require Logger

  alias Ingest.Repo
  alias Ingest.Resource
  alias Ingest.ResourcePipeline

  # Small, fast backoff so retries are visible immediately in the demo.
  @impl Oban.Worker
  def backoff(_job), do: 1

  @impl Oban.Worker
  def perform(%Oban.Job{args: %{"resource_id" => id}, attempt: attempt}) do
    Resource
    |> Repo.get!(id)
    |> resume_if_failed()
    |> run_pipeline(attempt)
  end

  # --- the pipeline loop ---------------------------------------------------

  # Terminal: nothing to do. Re-running a finished resource is a safe no-op —
  # that's idempotency at the pipeline level.
  defp run_pipeline(%Resource{status: :indexed} = r, _attempt) do
    Logger.info("[#{r.title}] already :indexed — nothing to do")
    :ok
  end

  defp run_pipeline(%Resource{status: status} = r, attempt) do
    stage = stage_for(status)

    case run_stage(stage, r, attempt) do
      :ok ->
        next = ResourcePipeline.advance(status)
        Logger.info("[#{r.title}] #{stage} ✓   #{status} → #{next}")

        r
        |> transition!(%{status: next, failed_stage: nil, error_message: nil})
        |> run_pipeline(attempt)

      {:error, reason} ->
        transition!(r, %{
          status: :failed,
          failed_stage: stage,
          error_message: reason,
          attempt_count: r.attempt_count + 1
        })

        Logger.warning("[#{r.title}] #{stage} ✗   (attempt #{attempt}) #{reason}")
        {:error, reason}
    end
  end

  defp resume_if_failed(%Resource{status: :failed, failed_stage: failed_stage} = r) do
    target = ResourcePipeline.retry_target(failed_stage)
    Logger.info("[#{r.title}] retrying: rewind from failed #{failed_stage} → #{target}")
    transition!(r, %{status: target})
  end

  defp resume_if_failed(r), do: r

  # Which unit of work is due at each checkpoint (the inverse of advance/1).
  defp stage_for(:pending), do: :chunk
  defp stage_for(:chunked), do: :embed
  defp stage_for(:embedded), do: :store

  # --- the (stubbed) work of each stage ------------------------------------

  defp run_stage(:chunk, %Resource{} = r, _attempt) do
    chunks = r.content |> String.split() |> Enum.chunk_every(40) |> Enum.map(&Enum.join(&1, " "))
    Logger.info("[#{r.title}]   chunk: #{length(chunks)} chunks")
    :ok
  end

  defp run_stage(:embed, %Resource{}, attempt) do
    # Flaky ON PURPOSE: the embedding service "times out" on the first 2 tries,
    # then succeeds. This is what makes the retry path observable.
    if attempt <= 2 do
      {:error, "embedding service timeout (simulated, attempt #{attempt})"}
    else
      :ok
    end
  end

  defp run_stage(:store, %Resource{}, _attempt), do: :ok

  defp transition!(%Resource{} = r, attrs) do
    r |> Resource.transition_changeset(attrs) |> Repo.update!()
  end
end
