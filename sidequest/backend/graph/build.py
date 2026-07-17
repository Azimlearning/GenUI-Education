"""StateGraph assembly.

Phase 1 shape: router -> explainer -> artifact_branch -> END, sequential.
The artifact branch no-ops for text_only intents (and in echo mode or when
ARTIFACTS_DISABLED is set). Phase 2 adds the verifier retry loop inside the
branch; Phase 3 runs explainer and artifact branch in parallel; Phase 4 adds
the cache node ahead of the planner. Conditional-edge design lives in
docs/SYSTEM_ARCHITECTURE.md section 4.
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
    graph.add_edge("router", "explainer")
    graph.add_edge("explainer", "artifact_branch")
    graph.add_edge("artifact_branch", END)
    return graph.compile()
