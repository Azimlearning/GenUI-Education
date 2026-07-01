"""Persistent learner model (ADR-012 / D-11).

`LearnerStore` is the interface the Tutor Loop writes to and the Diagnostician reads from.
P0 ships an in-memory implementation; P3 adds SQLite; a hosted demo can add Firebase — all
behind this same Protocol so agent code never changes.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Protocol

from pydantic import BaseModel, Field


class ObservedMisconception(BaseModel):
    misconception_id: str
    topic: str
    first_seen: datetime
    last_seen: datetime
    resolved: bool = False
    review_due: datetime | None = None  # spaced-repetition schedule


class LearnerProfile(BaseModel):
    student_id: str
    mastery: dict[str, float] = Field(default_factory=dict)  # topic → 0..1
    misconceptions: dict[str, ObservedMisconception] = Field(default_factory=dict)
    preferred_patterns: list[str] = Field(default_factory=list)  # what representation "clicked"


class LearnerStore(Protocol):
    def get(self, student_id: str) -> LearnerProfile: ...
    def save(self, profile: LearnerProfile) -> None: ...


class InMemoryLearnerStore:
    """Dev-only store (D-11). Non-persistent — lost on restart. Fine through P2."""

    def __init__(self) -> None:
        self._data: dict[str, LearnerProfile] = {}

    def get(self, student_id: str) -> LearnerProfile:
        return self._data.get(student_id) or LearnerProfile(student_id=student_id)

    def save(self, profile: LearnerProfile) -> None:
        self._data[profile.student_id] = profile

    # convenience used by the Tutor Loop stub
    def record_misconception(
        self, student_id: str, misconception_id: str, topic: str, *, review_in_days: int = 3
    ) -> LearnerProfile:
        profile = self.get(student_id)
        now = datetime.now(timezone.utc)
        existing = profile.misconceptions.get(misconception_id)
        if existing is None:
            profile.misconceptions[misconception_id] = ObservedMisconception(
                misconception_id=misconception_id,
                topic=topic,
                first_seen=now,
                last_seen=now,
                review_due=now + timedelta(days=review_in_days),
            )
        else:
            existing.last_seen = now
            existing.review_due = now + timedelta(days=review_in_days)
        self.save(profile)
        return profile


_store: LearnerStore | None = None


def get_store() -> LearnerStore:
    """Return the configured store. P0: always in-memory (SQLite/Firebase deferred, D-11)."""
    global _store
    if _store is None:
        _store = InMemoryLearnerStore()
    return _store
