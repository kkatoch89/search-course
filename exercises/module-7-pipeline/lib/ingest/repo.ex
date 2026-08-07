defmodule Ingest.Repo do
  @moduledoc "The Ecto repo — plumbing, written for you."
  use Ecto.Repo,
    otp_app: :ingest,
    adapter: Ecto.Adapters.Postgres
end
