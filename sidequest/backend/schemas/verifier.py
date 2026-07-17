"""VerifierReport schema. Anchored in docs/DATA_MODEL.md.

Phase 1 runs the Verifier in log-only stub mode (never blocks); the report
shape is fixed now so Phase 2 swaps in the LLM verifier without churn. The
PassedVerifierReport delivery-gate type arrives in Phase 2 with the real
verifier (SECURITY.md section 4).
"""

from typing import Literal

from pydantic import BaseModel, Field


class SpotCheck(BaseModel):
    inputs: str = Field(max_length=200)
    expected: str = Field(max_length=200)
    code_derived: str = Field(max_length=200)


class VerifierIssue(BaseModel):
    severity: Literal["blocker", "major", "minor"]
    category: Literal["science", "behavior", "interactivity", "safety", "pedagogy"]
    description: str = Field(max_length=600)
    fix_hint: str = Field(max_length=400)


class VerifierReport(BaseModel):
    verdict: Literal["pass", "fail"]
    issues: list[VerifierIssue] = []
    spot_checks: list[SpotCheck] = []
    mode: Literal["llm", "stub_log_only"] = "llm"
