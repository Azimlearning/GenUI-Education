"""VerifierReport schema. Anchored in docs/DATA_MODEL.md.

Phase 1 runs the Verifier in log-only stub mode (never blocks); the report
shape is fixed now so Phase 2 swaps in the LLM verifier without churn. The
PassedVerifierReport delivery-gate type arrives in Phase 2 with the real
verifier (SECURITY.md section 4).
"""

from typing import Literal

from pydantic import BaseModel, Field


# Length caps bound free-text volume without strangling real verification
# detail: live spot checks legitimately carry multi-step hand calculations
# (Stefan-Boltzmann traces blew the original 200-char caps).
class SpotCheck(BaseModel):
    inputs: str = Field(max_length=600)
    expected: str = Field(max_length=600)
    code_derived: str = Field(max_length=600)


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
