"""Seed KSSM misconception library (ADR-004 / D-04).

The Diagnostician matches student questions against these pre-authored entries rather than
improvising — this is the citable pedagogical-impact artifact (Educational Significance).

P0 uses simple keyword triggers for detection; P1 replaces `detect()` with an LLM-grounded
match via the provider router (the diagnostician still cites an entry from HERE — the model
classifies into this list, it does not invent misconceptions). Expand this KB with real,
sourced Malaysian/ESL science-education literature (see synapse-sources.md → "to gather").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Misconception:
    id: str
    subject: str
    form: int
    topic: str
    statement: str  # the wrong belief, as students phrase it
    correct: str  # the faithful correction
    triggers: list[str] = field(default_factory=list)  # P0 keyword/regex cues
    source: str | None = None  # citation, to be filled from literature (P1)


MISCONCEPTIONS: dict[str, Misconception] = {
    "osmosis-inverted-gradient": Misconception(
        id="osmosis-inverted-gradient",
        subject="Biology",
        form=4,
        topic="osmosis",
        statement="Osmosis is when water moves to where there is more water.",
        correct=(
            "Water moves across a selectively permeable membrane from a region of lower "
            "solute concentration to a region of higher solute concentration (down the "
            "water potential gradient) — i.e. toward more solute, not more water."
        ),
        triggers=["osmos", "water mov", "more water", "toward water", "less salt"],
        source="TODO: cite KSSM/ESL osmosis-misconception study (P1)",
    ),
    "bonding-sharing-vs-transfer": Misconception(
        id="bonding-sharing-vs-transfer",
        subject="Chemistry",
        form=4,
        topic="ionic vs covalent bonding",
        statement="Ionic and covalent bonds are basically the same kind of sharing.",
        correct=(
            "Ionic bonding is electron TRANSFER between a metal and non-metal (forming ions "
            "held by electrostatic attraction); covalent bonding is electron SHARING between "
            "non-metals. The electronegativity difference decides which occurs."
        ),
        triggers=["ionic", "covalent", "bond"],
        source="TODO: cite bonding-misconception literature (P1)",
    ),
    "newton-force-needed-to-keep-moving": Misconception(
        id="newton-force-needed-to-keep-moving",
        subject="Physics",
        form=4,
        topic="Newton's first law",
        statement="A moving object needs a continuous force to keep moving.",
        correct=(
            "An object in motion stays in motion at constant velocity unless acted on by a "
            "net external force (Newton's first law). What stops everyday objects is friction, "
            "not the absence of a driving force."
        ),
        triggers=["keep moving", "force to move", "stops moving", "need force"],
        source="TODO: cite force-motion misconception literature (P1)",
    ),
}


def get_misconception(mid: str) -> Misconception | None:
    return MISCONCEPTIONS.get(mid)


def detect(question: str) -> Misconception | None:
    """P0 keyword-based detection. Returns the first misconception whose triggers match.

    Deliberately simple — P1 replaces this with an LLM classifier (via the provider router)
    that still selects from this same list rather than improvising (D-04).
    """
    q = question.lower()
    for m in MISCONCEPTIONS.values():
        for trig in m.triggers:
            if re.search(re.escape(trig), q):
                return m
    return None
