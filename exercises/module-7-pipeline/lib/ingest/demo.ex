defmodule Ingest.Demo do
  @moduledoc """
  Runs the whole pipeline end to end and narrates it — plumbing.

      mix ingest.demo      (or: mix run -e "Ingest.Demo.run()")

  It resets the tables, intakes a couple of articles, drains the Oban queue
  (running every job + retry synchronously so the output is deterministic), then
  demonstrates idempotency: re-intaking unchanged content does nothing, while an
  edit re-runs the pipeline.
  """
  require Logger
  import Ecto.Query

  alias Ingest.Repo
  alias Ingest.Resource

  @doc false
  def run do
    reset()

    banner("1. Intake two new articles → run the pipeline")
    {:created, a} = intake("Photosynthesis", "Plants use sunlight to turn water and carbon dioxide into sugar and oxygen. This process is called photosynthesis and it happens in the leaves.")
    {:created, b} = intake("Salt water", "Salt water is water with salt dissolved in it. The oceans are made of salt water. It is not safe to drink because of the salt.")
    drain()
    show([a, b])

    banner("2. Idempotency: re-intake the SAME content")
    {result, _} = intake("Photosynthesis", "Plants use sunlight to turn water and carbon dioxide into sugar and oxygen. This process is called photosynthesis and it happens in the leaves.")
    IO.puts("   intake returned: #{inspect(result)}  (no job enqueued — nothing changed)")
    drain()
    show([a])

    banner("3. A real edit re-runs the pipeline")
    {result2, _} = intake("Photosynthesis", "Plants use sunlight to turn water and carbon dioxide into STARCH and oxygen. This edited sentence changes the content hash.")
    IO.puts("   intake returned: #{inspect(result2)}  (content changed — reset to :pending)")
    drain()
    show([a])

    :ok
  end

  # --- intake (plumbing): the idempotency gate ------------------------------
  # Same idea as Module 3's content hash + Module 6's upsert-by-id: we only do
  # work when the content actually changed.
  defp intake(title, content) do
    hash = sha256(content)

    case Repo.get_by(Resource, title: title) do
      nil ->
        {:ok, r} =
          %{title: title, content: content, content_hash: hash, status: :pending}
          |> Resource.create_changeset()
          |> Repo.insert()

        enqueue(r)
        {:created, r}

      %Resource{content_hash: ^hash} = r ->
        # Identical content -> no-op. Don't touch state, don't enqueue.
        {:unchanged, r}

      %Resource{} = r ->
        # Content changed -> reset to the top and re-enqueue.
        {:ok, r2} =
          r
          |> Ecto.Changeset.change(%{
            content: content,
            content_hash: hash,
            status: :pending,
            attempt_count: 0,
            failed_stage: nil,
            error_message: nil
          })
          |> Repo.update()

        enqueue(r2)
        {:changed, r2}
    end
  end

  defp enqueue(%Resource{id: id}) do
    %{resource_id: id} |> Ingest.Worker.new() |> Oban.insert!()
  end

  # Run every available job (and its retries) inline, so the demo is deterministic.
  defp drain do
    summary = Oban.drain_queue(queue: :ingest, with_scheduled: true, with_recursion: true)
    IO.puts("   drain: #{inspect(Map.take(summary, [:success, :failure, :discard]))}")

    # A `discard` means a job used up all its retries and gave up — surface WHY.
    # (Transient failures that later succeed show up as `failure` and are normal.)
    if Map.get(summary, :discard, 0) > 0, do: report_last_error()
  end

  defp report_last_error do
    job =
      Oban.Job
      |> where([j], fragment("cardinality(?) > 0", j.errors))
      |> order_by([j], desc: j.id)
      |> limit(1)
      |> Repo.one()

    with %Oban.Job{errors: [_ | _] = errors} <- job do
      lines = (List.last(errors)["error"] || "") |> String.split("\n")
      first = Enum.find(lines, &String.contains?(&1, "TODO")) || List.first(lines)
      IO.puts("   ↳ a job gave up. last error: #{first}")
    end
  end

  defp show(resources) do
    for %Resource{id: id} <- resources do
      r = Repo.get!(Resource, id)

      IO.puts(
        "   #{String.pad_trailing(r.title, 16)} status=#{r.status}" <>
          " attempts=#{r.attempt_count}" <>
          if(r.failed_stage, do: " failed_stage=#{r.failed_stage}", else: "")
      )
    end
  end

  defp reset do
    Repo.delete_all(Resource)
    Repo.delete_all(Oban.Job)
  end

  defp sha256(text), do: :crypto.hash(:sha256, text) |> Base.encode16(case: :lower)

  defp banner(text) do
    IO.puts("\n" <> String.duplicate("=", 66) <> "\n== #{text}\n" <> String.duplicate("=", 66))
  end
end
