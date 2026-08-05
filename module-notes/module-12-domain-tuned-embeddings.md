# Module 12 — Domain-Tuned Embeddings

**Concepts:** contrastive learning, triplet / InfoNCE / `MultipleNegativesRankingLoss`, hard-negative mining, fine-tuning sentence-transformers.
**Time spent:** _fill in_
**Date completed:** _fill in_

## What I read

- [ ] Sentence-Transformers training docs
- [ ] Sentence-BERT paper (skim)

## Codebase walk

None — production uses off-the-shelf embeddings.

**Reflection:** would Instinct's veterinary corpus benefit from domain-tuned
embeddings? On which queries / namespaces? _fill in_

## Exercises

### 1. Triplet construction

- Source queries: my 30 eval pairs from Module 13
- Hard negatives: BM25 top-N where the doc is NOT the labeled positive
- Final triplet count: _fill in_
- Stored as: `exercises/module-12/triplets.jsonl`

### 2. Fine-tune

- Base model: `sentence-transformers/all-MiniLM-L6-v2`
- Loss: `MultipleNegativesRankingLoss`
- Epochs: _3_, batch size: _fill in_
- Hardware: _CPU / GPU model_, training time: _fill in_
- Saved to: `exercises/module-12/finetuned-model/`

### 3. Before/after eval

| Metric    | Off-the-shelf | Fine-tuned | Δ    |
| --------- | ------------- | ---------- | ---- |
| Recall@5  |               |            |      |
| MRR       |               |            |      |
| NDCG@10   |               |            |      |

Plot: `exercises/module-12/before_after.png`

## Mini-project writeup (PORTFOLIO PIECE)

- Repo: `exercises/module-12/`
- Writeup answers:
  - Did fine-tuning help overall? On which query types?
  - Where did it hurt? (overfit categories?)
  - When would I do this in production?
  - What does this say about the value of off-the-shelf embeddings for
    general-domain corpora?

## Glossary additions

## Open questions
