"""Loading the Wikipedia corpus — plumbing, written for you.

This satellite reuses the SAME 5k slice the engine downloaded in Module 1
(``exercises/wikisearch/data/wiki_simple_5k.parquet``). Nothing to change here.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# The 5k slice lives in the engine's data dir (a sibling folder).
ENGINE_DATA = (
    Path(__file__).resolve().parent.parent / "wikisearch" / "data" / "wiki_simple_5k.parquet"
)


@dataclass
class Document:
    """One Wikipedia article."""

    id: str
    title: str
    text: str


def load_corpus(path: Path = ENGINE_DATA) -> list[Document]:
    """Read the parquet corpus into a list of Documents.

    Raises a friendly error if the 5k slice hasn't been downloaded yet.
    """
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
