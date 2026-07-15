"""StateGraph assembly.

Phase 0 shape: router -> explainer -> END. The artifact branch (cache,
planner, generator, verifier, postprocess) is added in Phases 1-2 as a
parallel branch after the router; conditional edges are documented in
docs/SYSTEM_ARCHITECTURE.md section 4.
"""

from functools import lru_cache

from langgraph.graph import END, StateGraph

from graph.nodes.explainer import explainer_node
from graph.nodes.router import router_node
from graph.state import PipelineState


@lru_cache
def build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("router", router_node)
    graph.add_node("explainer", explainer_node)
    graph.set_entry_point("router")
    graph.add_edge("router", "explainer")
    graph.add_edge("explainer", END)
    return graph.compile()
