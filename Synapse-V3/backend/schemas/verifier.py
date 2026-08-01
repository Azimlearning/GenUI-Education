"""VerifierReport schema. Anchored in docs/DATA_MODEL.md.

Phase 1 runs the Verifier in log-only stub mode (never blocks); the report
shape is fixed now so Phase 2 swaps in the LLM verifier without churn. The
PassedVerifierReport delivery-gate type arrives in Phase 2 with the real
verifier (SECURITY.md section 4).
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Length caps bound free-text volume without strangling real verification
# detail: live spot checks legitimately carry multi-step hand calculations.
# A detailed amylase-temperature trace exceeded the earlier 600- and 2,000-
# character limits. The verifier's verdict is the safety-relevant value, so a
# verbose explanation must be bounded, never allowed to discard that verdict.
SPOT_CHECK_MAX_CHARS = 8_000
_TRUNCATION_SUFFIX = " [truncated]"


class SpotCheck(BaseModel):
    inputs: str = Field(max_length=SPOT_CHECK_MAX_CHARS)
    expected: str = Field(max_length=SPOT_CHECK_MAX_CHARS)
    code_derived: str = Field(max_length=SPOT_CHECK_MAX_CHARS)

    @field_validator("inputs", "expected", "code_derived", mode="before")
    @classmethod
    def bound_verbose_trace(cls, value: object) -> object:
        """Preserve a verifier verdict when an explanatory trace is verbose."""
        if not isinstance(value, str) or len(value) <= SPOT_CHECK_MAX_CHARS:
            return value
        return value[: SPOT_CHECK_MAX_CHARS - len(_TRUNCATION_SUFFIX)] + _TRUNCATION_SUFFIX


class VerifierIssue(BaseModel):
    severity: Literal["blocker", "major", "minor"]
    category: Literal["science", "behavior", "interactivity", "safety", "pedagogy"]
    description: str = Field(max_length=1500)
    fix_hint: str = Field(max_length=800)


class VerifierReport(BaseModel):
    verdict: Literal["pass", "fail"]
    issues: list[VerifierIssue] = []
    spot_checks: list[SpotCheck] = []
    mode: Literal["llm", "stub_log_only"] = "llm"
