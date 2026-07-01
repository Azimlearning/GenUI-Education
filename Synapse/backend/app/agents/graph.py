"""The LangGraph pipeline (PRD §5) — Diagnostician → Strategist → Composer → Tutor Loop.

A linear `StateGraph` over `PipelineState`. Each node returns a partial update; the `steps`
reducer accumulates the visible reasoning across nodes (D-03). Two entry points:

- `run_pipeline(question, student_id)` — invoke to completion, returns the final `PipelineState`.
- `build_graph()` — the compiled graph; the SSE route uses `.stream(..., stream_mode="updates")`
  to emit each node's steps as they are produced.
"""

from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.agents.component_composer import compose
from app.agents.diagnostician import diagnose
from app.agents.pedagogy_strategist import strategize
from app.agents.tutor_loop import close_loop
from app.models import PipelineState


@lru_cache
def build_graph():
    """Build and compile the pipeline once (cached)."""
    g: StateGraph = StateGraph(PipelineState)

    g.add_node("diagnostician", diagnose)
    g.add_node("pedagogy_strategist", strategize)
    g.add_node("component_composer", compose)
    g.add_node("tutor_loop", close_loop)

    g.add_edge(START, "diagnostician")
    g.add_edge("diagnostician", "pedagogy_strategist")
    g.add_edge("pedagogy_strategist", "component_composer")
    g.add_edge("component_composer", "tutor_loop")
    g.add_edge("tutor_loop", END)

    return g.compile()


def run_pipeline(question: str, student_id: str | None = None) -> PipelineState:
    """Invoke the whole pipeline to completion (non-streaming). Returns the final state."""
    graph = build_graph()
    initial = PipelineState(question=question, student_id=student_id)
    result = graph.invoke(initial)
    # LangGraph returns the state as a dict-like; normalise back to the Pydantic model.
    return PipelineState.model_validate(result)
