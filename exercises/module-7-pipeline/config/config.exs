import Config

# --- Database (plumbing) ---------------------------------------------------
# Connects to your local Postgres. Defaults match a stock homebrew install
# (your OS user, no password, localhost). Override with env vars if needed.
config :ingest, Ingest.Repo,
  username: System.get_env("PGUSER", System.get_env("USER", "postgres")),
  password: System.get_env("PGPASSWORD", ""),
  hostname: System.get_env("PGHOST", "localhost"),
  database: System.get_env("PGDATABASE", "m7_pipeline_dev"),
  pool_size: 5

config :ingest, ecto_repos: [Ingest.Repo]

# --- Oban (plumbing) -------------------------------------------------------
# We run with NO online queue producers (`queues: false`) and no plugins:
# the Demo drives everything synchronously with `Oban.drain_queue/2`, so runs
# are deterministic and you can watch each state transition in order.
config :ingest, Oban,
  repo: Ingest.Repo,
  queues: false,
  plugins: false

config :logger, level: :info
