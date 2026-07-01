"""Persistent learner model (ADR-012 / D-11).

`LearnerStore` is the interface the Tutor Loop writes to and the Diagnostician reads from.
Two implementations behind the same interface, selected by the LEARNER_STORE env var:

- `memory` (default) — in-process dict, lost on restart. Fine for tests / quick demos.
- `sqlite`          — durable single-file store (`LEARNER_STORE_PATH`). Survives restarts,
                      which is the whole point of the tutor loop. Firebase (D-11) is deferred
                      to a hosted multi-device demo.

Agent code depends only on this module's functions, never on the concrete store.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from typing import Protocol

from pydantic import BaseModel, Field

from app.config import get_settings


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
    def record_misconception(
        self, student_id: str, misconception_id: str, topic: str, *, review_in_days: int = 3
    ) -> LearnerProfile: ...
    def record_interaction(
        self, student_id: str, topic: str, correct: bool, *, misconception_id: str | None = None
    ) -> LearnerProfile: ...


def _record_misconception(
    store: LearnerStore, student_id: str, misconception_id: str, topic: str, review_in_days: int
) -> LearnerProfile:
    """Shared spaced-repetition bookkeeping used by both store implementations."""
    profile = store.get(student_id)
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
    store.save(profile)
    return profile


def _record_interaction(
    store: LearnerStore, student_id: str, topic: str, correct: bool, misconception_id: str | None
) -> LearnerProfile:
    """Update mastery from a live interaction (P3) and re-schedule spaced repetition.

    Mastery moves toward 1 on a correct interaction and decays on a wrong one. A correct
    prediction against a diagnosed misconception marks it resolved and pushes the next review
    out (spaced repetition); a wrong one resurfaces it sooner.
    """
    profile = store.get(student_id)
    now = datetime.now(timezone.utc)
    m = profile.mastery.get(topic, 0.0)
    m = m + 0.34 * (1 - m) if correct else m * 0.6
    profile.mastery[topic] = round(m, 3)

    if misconception_id and misconception_id in profile.misconceptions:
        obs = profile.misconceptions[misconception_id]
        obs.last_seen = now
        if correct:
            obs.resolved = True
            obs.review_due = now + timedelta(days=7)  # spaced out — they got it
        else:
            obs.resolved = False
            obs.review_due = now + timedelta(days=1)  # bring it back soon
    store.save(profile)
    return profile


def due_for_review(profile: LearnerProfile, *, now: datetime | None = None) -> list[ObservedMisconception]:
    """Unresolved misconceptions whose review date has arrived."""
    at = now or datetime.now(timezone.utc)
    return [
        obs for obs in profile.misconceptions.values()
        if not obs.resolved and obs.review_due is not None and obs.review_due <= at
    ]


class InMemoryLearnerStore:
    """Dev-only store (D-11). Non-persistent — lost on restart."""

    def __init__(self) -> None:
        self._data: dict[str, LearnerProfile] = {}

    def get(self, student_id: str) -> LearnerProfile:
        return self._data.get(student_id) or LearnerProfile(student_id=student_id)

    def save(self, profile: LearnerProfile) -> None:
        self._data[profile.student_id] = profile

    def record_misconception(
        self, student_id: str, misconception_id: str, topic: str, *, review_in_days: int = 3
    ) -> LearnerProfile:
        return _record_misconception(self, student_id, misconception_id, topic, review_in_days)

    def record_interaction(
        self, student_id: str, topic: str, correct: bool, *, misconception_id: str | None = None
    ) -> LearnerProfile:
        return _record_interaction(self, student_id, topic, correct, misconception_id)


class SqliteLearnerStore:
    """Durable store (D-11). One row per learner; the profile is a JSON blob."""

    def __init__(self, path: str) -> None:
        self._path = path
        self._lock = threading.Lock()
        # check_same_thread=False so the store works under uvicorn's threadpool; the lock serialises.
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS learners (student_id TEXT PRIMARY KEY, profile TEXT NOT NULL)"
        )
        self._conn.commit()

    def get(self, student_id: str) -> LearnerProfile:
        with self._lock:
            row = self._conn.execute(
                "SELECT profile FROM learners WHERE student_id = ?", (student_id,)
            ).fetchone()
        if row is None:
            return LearnerProfile(student_id=student_id)
        return LearnerProfile.model_validate_json(row[0])

    def save(self, profile: LearnerProfile) -> None:
        blob = profile.model_dump_json()
        with self._lock:
            self._conn.execute(
                "INSERT INTO learners (student_id, profile) VALUES (?, ?) "
                "ON CONFLICT(student_id) DO UPDATE SET profile = excluded.profile",
                (profile.student_id, blob),
            )
            self._conn.commit()

    def record_misconception(
        self, student_id: str, misconception_id: str, topic: str, *, review_in_days: int = 3
    ) -> LearnerProfile:
        return _record_misconception(self, student_id, misconception_id, topic, review_in_days)

    def record_interaction(
        self, student_id: str, topic: str, correct: bool, *, misconception_id: str | None = None
    ) -> LearnerProfile:
        return _record_interaction(self, student_id, topic, correct, misconception_id)


_store: LearnerStore | None = None


def get_store() -> LearnerStore:
    """Return the configured store (LEARNER_STORE=memory|sqlite; default memory)."""
    global _store
    if _store is None:
        settings = get_settings()
        if settings.learner_store.lower() == "sqlite":
            _store = SqliteLearnerStore(settings.learner_store_path)
        else:
            _store = InMemoryLearnerStore()
    return _store
