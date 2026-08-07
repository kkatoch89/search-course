defmodule Mix.Tasks.Ingest.Demo do
  @shortdoc "Runs the Module 7 ingestion-pipeline demo end to end"
  @moduledoc @shortdoc
  use Mix.Task

  @impl Mix.Task
  def run(_args) do
    Mix.Task.run("app.start")
    Ingest.Demo.run()
  end
end
