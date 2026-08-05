# Data Setup — Simple English Wikipedia

The course uses Simple English Wikipedia (~226k articles) as its primary
corpus across all modules.

## Why Simple English Wikipedia

- **Right size:** big enough to be portfolio-credible, small enough that the
  ingestion pipeline runs end-to-end on a laptop in minutes.
- **Cheap to embed:** ~$2–5 with OpenAI `text-embedding-3-small`; free with a
  local sentence-transformers model.
- **Recognizable:** demoable to non-technical viewers — everyone knows
  Wikipedia.
- **Diverse topics:** lets hybrid-search differences (FTS vs. vector vs.
  hybrid) actually show up in results.

## Schema

| Field   | Type   | Notes                                |
| ------- | ------ | ------------------------------------ |
| `id`    | string | Wikipedia page ID                    |
| `url`   | string | Source URL                           |
| `title` | string | Article title                        |
| `text`  | string | Full article body (plain text)       |

## Download (Hugging Face)

```python
# install: pip install datasets
from datasets import load_dataset

ds = load_dataset("wikimedia/wikipedia", "20231101.simple")
print(ds)
# DatasetDict({ train: Dataset({ features: ['id','url','title','text'], num_rows: 226_350 }) })

# Save locally as parquet for fast reload
ds["train"].to_parquet("data/wiki_simple_full.parquet")
```

## 5k subsample for early modules

Modules 1–3 use a 5k random subsample so prototyping stays fast.

```python
import pandas as pd

df = pd.read_parquet("data/wiki_simple_full.parquet")
sample = df.sample(n=5_000, random_state=42)
sample.to_parquet("data/wiki_simple_5k.parquet")
print(f"saved {len(sample)} articles")
```

## Storage tips

- `data/` is gitignored — never commit corpora or embeddings.
- Full parquet is ~700MB. Plan disk accordingly.
- Consider DuckDB for ad-hoc querying:
  ```python
  import duckdb
  duckdb.sql("SELECT title FROM 'data/wiki_simple_full.parquet' LIMIT 10")
  ```

## Embedding cost reference

| Model                                         | Dim  | Cost (full corpus, ~113M tokens) |
| --------------------------------------------- | ---- | -------------------------------- |
| OpenAI `text-embedding-3-small`               | 1536 | ~$2.30                           |
| OpenAI `text-embedding-3-large`               | 3072 | ~$15                             |
| local `sentence-transformers/all-MiniLM-L6-v2` | 384 | $0 (laptop CPU/GPU, ~30–60 min) |

**Recommendation:** local embedder for exercises, OpenAI for the capstone
demo so the writeup can claim production-grade quality.

## Ground-truth queries (for Module 9 + capstone eval)

Hand-label your own. A starter set lives in `data/eval_queries.jsonl` —
create it once, grow it as you go:

```jsonl
{"query": "When did World War II end?", "ideal_titles": ["World War II"]}
{"query": "How do plants make food?", "ideal_titles": ["Photosynthesis"]}
{"query": "Who painted the Mona Lisa?", "ideal_titles": ["Leonardo da Vinci", "Mona Lisa"]}
```
