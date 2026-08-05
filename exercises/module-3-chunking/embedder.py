"""A stand-in embedder — plumbing, written for you.

In Module 2 you saw that turning text into a vector is a *model call*: slow and,
in production, metered/paid. This module's whole lesson is **not making that call
when you don't have to**. So we don't need a real model here — we need something
that lets us *count* calls.

``StubEmbedder`` stands in for Module 2's ``embed_texts``. Every ``.embed(text)``
bumps a counter and returns a throwaway value. If your idempotency logic is right,
the counter goes up on the first run and stays flat when nothing changed.
"""
from __future__ import annotations


class StubEmbedder:
    """Pretends to embed text; really just counts how often it's asked to."""

    def __init__(self) -> None:
        self.calls = 0

    def embed(self, text: str):
        self.calls += 1
        return [0.0]  # stand-in for a real 384-dim vector from Module 2
