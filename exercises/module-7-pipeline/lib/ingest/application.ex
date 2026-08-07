defmodule Ingest.Application do
  @moduledoc "Boots the Repo and Oban — plumbing, written for you."
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      Ingest.Repo,
      {Oban, Application.fetch_env!(:ingest, Oban)}
    ]

    Supervisor.start_link(children, strategy: :one_for_one, name: Ingest.Supervisor)
  end
end
