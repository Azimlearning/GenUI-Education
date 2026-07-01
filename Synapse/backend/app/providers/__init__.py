"""Multi-provider LLM router (ADR-011 / D-05).

No hard-coded default provider. Each agent names a primary + ordered fallback chain in
`config.py`; `router.py` executes it and falls through on error/refusal. Adapters are
stubs in P0 and get real SDK calls in P1.
"""

from app.providers.router import ProviderRouter, get_router

__all__ = ["ProviderRouter", "get_router"]
