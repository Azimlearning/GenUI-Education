"""The four pedagogical agents + the LangGraph pipeline (PRD §5).

P0: each agent is a scripted stub over `PipelineState` (deterministic, LLM-free) so the whole
loop is visible end-to-end. P1: replace each body with a real LLM call via the provider router.
"""

from app.agents.graph import build_graph, run_pipeline

__all__ = ["build_graph", "run_pipeline"]
