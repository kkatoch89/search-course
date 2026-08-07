defmodule Ingest.MixProject do
  use Mix.Project

  # Module 7 — a tiny, real ingestion pipeline: Oban (background jobs) + Ecto
  # (a Postgres-backed state machine) + retries. It mirrors the shape of
  # chunky-kong's search-sync pipeline, scaled down to plain open-source Oban.

  def project do
    [
      app: :ingest,
      version: "0.1.0",
      elixir: "~> 1.16",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      aliases: aliases()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {Ingest.Application, []}
    ]
  end

  defp deps do
    [
      {:ecto_sql, "~> 3.11"},
      {:postgrex, "~> 0.17"},
      {:oban, "~> 2.17"},
      {:jason, "~> 1.4"}
    ]
  end

  defp aliases do
    [
      # `mix setup` = install deps + create/migrate the database in one shot.
      setup: ["deps.get", "ecto.create", "ecto.migrate"],
      "ecto.reset": ["ecto.drop", "ecto.create", "ecto.migrate"]
    ]
  end
end
