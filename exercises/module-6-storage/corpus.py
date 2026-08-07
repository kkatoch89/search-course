"""Loading the corpus + cached vectors, and deriving filter attributes — plumbing.

Written for you (like Module 3's ``corpus.py``). This satellite reuses TWO
artifacts the engine already produced, both under ``../wikisearch/data/``:

  * ``wiki_simple_5k.parquet``  — the 5k articles (Module 1 downloaded it)
  * ``embeddings_5k.npy``       — one 384-dim vector per article, in the SAME
                                  row order as the parquet (Module 2 built it)

Nothing here talks to the network. It just reads those two files and derives a
few cheap **attributes** per article (things you can filter on later in the
store). Nothing to change in this file.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# Both artifacts live in the engine's data dir (a sibling folder).
ENGINE_DATA = Path(__file__).resolve().parent.parent / "wikisearch" / "data"
CORPUS_PARQUET = ENGINE_DATA / "wiki_simple_5k.parquet"
EMBEDDINGS_NPY = ENGINE_DATA / "embeddings_5k.npy"


@dataclass
class Document:
    """One Wikipedia article."""

    id: str
    title: str
    text: str


def load_corpus(path: Path = CORPUS_PARQUET) -> list[Document]:
    """Read the parquet corpus into a list of Documents (same order as on disk)."""
    if not path.exists():
        raise SystemExit(
            f"No corpus found at {path}.\n"
            f"This module reuses the engine's 5k slice. Download it once with:\n"
            f"    cd ../wikisearch && python setup_data.py"
        )
    df = pd.read_parquet(path, columns=["id", "title", "text"])
    return [
        Document(id=str(row.id), title=str(row.title), text=str(row.text))
        for row in df.itertuples(index=False)
    ]


def load_embeddings(path: Path = EMBEDDINGS_NPY) -> np.ndarray:
    """Load the cached (5000, 384) document-embedding matrix.

    Row ``i`` is the vector for ``load_corpus()[i]`` — same order, so you can zip
    documents and vectors by position.
    """
    if not path.exists():
        raise SystemExit(
            f"No embeddings found at {path}.\n"
            f"This module reuses the vectors you built in Module 2. Build them once:\n"
            f"    cd ../wikisearch && python vector_cli.py \"test\"\n"
            f"(that caches embeddings_5k.npy), then come back."
        )
    return np.load(path)


def length_bucket(word_count: int) -> str:
    """Coarse size band for an article, used as a categorical filter attribute.

    Cutoffs chosen from the real 5k distribution (median ~= 300 words):
        short  < 100 words   (~1.0k articles — stubs / one-liners)
        medium 100..399      (~1.9k)
        long   >= 400        (~2.1k — the substantial articles)
    """
    if word_count < 100:
        return "short"
    if word_count < 400:
        return "medium"
    return "long"


def derive_attributes(doc: Document) -> dict:
    """Cheap, filterable metadata for one article.

    None of this comes from the vector — these are plain scalar attributes you
    store *alongside* the vector so you can narrow a search by them later:

      * title         — kept so results are readable
      * word_count    — an integer (enables numeric range filters: Gt / Lte / ...)
      * length_bucket — "short" / "medium" / "long" (a categorical Eq filter)
      * title_initial — first letter A..Z (or "#"); a highly selective Eq filter
    """
    word_count = len(doc.text.split())
    first = doc.title[:1]
    return {
        "title": doc.title,
        "word_count": word_count,
        "length_bucket": length_bucket(word_count),
        "title_initial": first.upper() if first.isalpha() else "#",
    }
