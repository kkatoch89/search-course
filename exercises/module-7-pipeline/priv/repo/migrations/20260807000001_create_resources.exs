defmodule Ingest.Repo.Migrations.CreateResources do
  use Ecto.Migration

  def change do
    create table(:resources) do
      add(:title, :string, null: false)
      add(:content, :text, null: false)
      add(:content_hash, :string, null: false)
      add(:status, :string, null: false, default: "pending")
      add(:failed_stage, :string)
      add(:error_message, :text)
      add(:attempt_count, :integer, null: false, default: 0)

      timestamps(type: :utc_datetime_usec)
    end
  end
end
