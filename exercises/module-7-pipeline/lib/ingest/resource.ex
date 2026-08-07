defmodule Ingest.Resource do
  @moduledoc """
  One thing being ingested (here: a Wikipedia-style article) — plumbing.

  This is the Postgres-backed **state machine**. `status` is where the resource
  is in the pipeline; it lives in the database, so if the app crashes mid-run,
  the resource is still sitting at its last checkpoint when things come back up.
  That durability is the whole point of a DB-backed pipeline.

  Mirrors chunky-kong's `sync/resource.ex` (statuses, failed_stage, attempt_count,
  content_hash for idempotency), trimmed to the essentials.
  """
  use Ecto.Schema
  import Ecto.Changeset

  # The happy-path checkpoints, in order, plus the failure state.
  #   :pending  -> nothing done yet
  #   :chunked  -> text has been split into chunks (Module 3)
  #   :embedded -> chunks have vectors (Module 2)
  #   :indexed  -> vectors stored in the vector store (Module 6) — DONE
  #   :failed   -> a stage raised; see failed_stage / error_message
  @statuses [:pending, :chunked, :embedded, :indexed, :failed]

  # The three units of work between checkpoints (what can fail).
  @stages [:chunk, :embed, :store]

  schema "resources" do
    field(:title, :string)
    field(:content, :string)

    # Idempotency key: identical content -> identical hash (same idea as Module 3).
    field(:content_hash, :string)

    field(:status, Ecto.Enum, values: @statuses, default: :pending)

    # Failure bookkeeping.
    field(:failed_stage, Ecto.Enum, values: @stages)
    field(:error_message, :string)
    field(:attempt_count, :integer, default: 0)

    timestamps(type: :utc_datetime_usec)
  end

  def statuses, do: @statuses
  def stages, do: @stages

  @doc "Changeset for a brand-new resource entering the pipeline."
  def create_changeset(attrs) do
    %__MODULE__{}
    |> cast(attrs, [:title, :content, :content_hash, :status])
    |> validate_required([:title, :content, :content_hash])
    |> validate_inclusion(:status, @statuses)
  end

  @doc "Changeset for a state transition (status + failure bookkeeping)."
  def transition_changeset(%__MODULE__{} = resource, attrs) do
    resource
    |> cast(attrs, [:status, :failed_stage, :error_message, :attempt_count])
    |> validate_required([:status])
    |> validate_inclusion(:status, @statuses)
  end
end
