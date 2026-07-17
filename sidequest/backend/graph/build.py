"""StateGraph assembly.

Phase 3 shape: router -> [explainer || artifact_branch] -> END. The two-branch
flow from docs/SYSTEM_ARCHITECTURE.md section 2: text is the fast path and is
never blocked by the artifact branch; both multiplex onto one SSE stream and
the client demuxes by event type. The artifact branch no-ops for text_only
intents (and in echo mode or when ARTIFACTS_DISABLED is set); its internal
timeout bounds only itself. Phase 4 adds the cache node ahead of the planner.
"""

from functools import lru_cache

from langgraph.graph import END, StateGraph

from graph.nodes.artifact import artifact_branch
from graph.nodes.explainer import explainer_node
from graph.nodes.router import router_node
from graph.state import PipelineState


@lru_cache
def build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("router", router_node)
    graph.add_node("explainer", explainer_node)
    graph.add_node("artifact_branch", artifact_branch)
    graph.set_entry_point("router")
    # Fan-out: both branches start as soon as the router classifies. They
    # write disjoint state keys, so the parallel superstep merge is safe.
    graph.add_edge("router", "explainer")
    graph.add_edge("router", "artifact_branch")
    graph.add_edge("explainer", END)
    graph.add_edge("artifact_branch", END)
    return graph.compile()
