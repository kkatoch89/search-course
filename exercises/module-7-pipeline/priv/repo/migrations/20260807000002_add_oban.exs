defmodule Ingest.Repo.Migrations.AddOban do
  use Ecto.Migration

  # Creates the oban_jobs table (and supporting objects) Oban needs to persist
  # background jobs. Written for you — this is Oban's own migration.
  def up, do: Oban.Migration.up()
  def down, do: Oban.Migration.down(version: 1)
end
