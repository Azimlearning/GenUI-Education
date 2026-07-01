"""Per-agent provider chains (ADR-011 / D-05).

No global default. Each agent declares an ordered chain of (provider, model); the router
tries them in order and falls through on error/refusal. Reorder or add providers HERE —
never inside an agent. Model ids are placeholders to be confirmed in P1 (OQ-2).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models import AgentName


@dataclass(frozen=True)
class ProviderChoice:
    provider: str  # "openai" | "anthropic" | "gemini" | "openrouter"
    model: str


# Ordered fallback chains, per agent.
#
# Anthropic Claude is the live PRIMARY (D-14); OpenAI is the configured fallback.
# Rationale:
#   - Diagnostician / Composer: latency-sensitive, structured output → fast model (Haiku) first.
#   - Strategist: the reasoning-heaviest step → a stronger model (Sonnet) first.
# Reorder / add providers HERE only — never inside an agent.
AGENT_PROVIDER_CHAINS: dict[AgentName, list[ProviderChoice]] = {
    AgentName.diagnostician: [
        ProviderChoice("anthropic", "claude-haiku-4-5-20251001"),
        ProviderChoice("openai", "gpt-4o-mini"),
    ],
    AgentName.pedagogy_strategist: [
        ProviderChoice("anthropic", "claude-sonnet-5"),
        ProviderChoice("openai", "gpt-4o"),
    ],
    AgentName.component_composer: [
        ProviderChoice("anthropic", "claude-haiku-4-5-20251001"),
        ProviderChoice("openai", "gpt-4o-mini"),
    ],
    # tutor_loop is deterministic bookkeeping — no LLM chain needed.
    AgentName.tutor_loop: [],
}
