"""Deterministic output fixes for the Generator (Phase 1+).

Each rule is a pure function `str -> str | PostprocessReject`, has a unit
test, and carries a comment citing the observed failure class it fixes
(TECHNICAL.md section 4). This file is expected to grow rule by rule as
repeated generation failures are observed; per CLAUDE.md, a failure class
seen 3+ times becomes a rule here instead of a prompt addition.

Phase 0 ships no rules: there is no Generator yet. The types below fix the
contract early so Phase 1 rules and their tests have a stable shape.
"""

from dataclasses import dataclass


@dataclass
class PostprocessReject:
    """A rule hit that must count as a verifier fail, never auto-strip
    (SECURITY.md section 3: auto-stripping produces silently broken artifacts)."""

    rule: str
    reason: str


Rule = "Callable[[str], str | PostprocessReject]"

RULES: list = []  # ordered; applied left to right in Phase 1


def run(html: str) -> str | PostprocessReject:
    for rule in RULES:
        result = rule(html)
        if isinstance(result, PostprocessReject):
            return result
        html = result
    return html
