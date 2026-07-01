"""KSSM misconception knowledge base — the Diagnostician's grounding (ADR-004 / D-04)."""

from app.knowledge.misconceptions import (
    MISCONCEPTIONS,
    Misconception,
    detect,
    get_misconception,
)

__all__ = ["MISCONCEPTIONS", "Misconception", "detect", "get_misconception"]
