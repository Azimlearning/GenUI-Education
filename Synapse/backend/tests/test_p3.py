"""P3 tests — the learner loop closing: mastery updates + spaced repetition + history-informed
diagnosis."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.store.learner_store import (
    InMemoryLearnerStore,
    due_for_review,
)


def test_correct_interaction_raises_mastery_and_resolves() -> None:
    store = InMemoryLearnerStore()
    store.record_misconception("s1", "osmosis-inverted-gradient", "osmosis")
    p0 = store.get("s1")
    assert p0.mastery.get("osmosis", 0.0) == 0.0
    assert p0.misconceptions["osmosis-inverted-gradient"].resolved is False

    p1 = store.record_interaction("s1", "osmosis", correct=True, misconception_id="osmosis-inverted-gradient")
    assert p1.mastery["osmosis"] > 0.3  # moved toward 1
    assert p1.misconceptions["osmosis-inverted-gradient"].resolved is True


def test_wrong_interaction_decays_mastery_and_reschedules_soon() -> None:
    store = InMemoryLearnerStore()
    store.record_misconception("s2", "newton-force-needed-to-keep-moving", "Newton's first law")
    store.record_interaction("s2", "Newton's first law", correct=True, misconception_id="newton-force-needed-to-keep-moving")
    p = store.record_interaction("s2", "Newton's first law", correct=False, misconception_id="newton-force-needed-to-keep-moving")
    assert p.misconceptions["newton-force-needed-to-keep-moving"].resolved is False
    # review pulled back to ~1 day out
    due = p.misconceptions["newton-force-needed-to-keep-moving"].review_due
    assert due is not None and due < datetime.now(timezone.utc) + timedelta(days=2)


def test_due_for_review_filters_by_date() -> None:
    store = InMemoryLearnerStore()
    profile = store.record_misconception("s3", "osmosis-inverted-gradient", "osmosis")
    # freshly recorded → review is days out → not due yet
    assert due_for_review(profile) == []
    # simulate the review date having passed
    obs = profile.misconceptions["osmosis-inverted-gradient"]
    obs.review_due = datetime.now(timezone.utc) - timedelta(hours=1)
    assert len(due_for_review(profile)) == 1
