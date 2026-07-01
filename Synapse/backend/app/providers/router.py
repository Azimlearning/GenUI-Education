"""The provider router (ADR-011 / D-05).

`run()` takes an agent name + a prompt and walks that agent's provider chain
(`config.AGENT_PROVIDER_CHAINS`), calling the first configured provider that succeeds.
In P0 the adapters are stubs: if no provider is configured (no API key), `run()` raises
`ProviderUnavailable`, and callers (the agents) fall back to their scripted P0 behaviour.

P1: implement the adapter bodies (`_call_openai`, `_call_anthropic`, …) against the real
SDKs, and have agents call `run()` instead of returning scripted output.
"""

from __future__ import annotations

import logging

from app.config import get_settings
from app.models import AgentName
from app.providers.config import AGENT_PROVIDER_CHAINS, ProviderChoice

logger = logging.getLogger("synapse.providers")


class ProviderUnavailable(RuntimeError):
    """Raised when no provider in an agent's chain is configured/usable."""


class ProviderRouter:
    def __init__(self) -> None:
        self._settings = get_settings()

    # ── key lookup ───────────────────────────────────────────────────────────
    def _key_for(self, provider: str) -> str:
        return {
            "openai": self._settings.openai_api_key,
            "anthropic": self._settings.anthropic_api_key,
            "gemini": self._settings.gemini_api_key,
            "openrouter": self._settings.openrouter_api_key,
        }.get(provider, "")

    def is_configured(self, provider: str) -> bool:
        return bool(self._key_for(provider))

    # ── public API ───────────────────────────────────────────────────────────
    def run(self, agent: AgentName, prompt: str, *, system: str | None = None) -> str:
        """Execute the agent's provider chain; return the model's text output.

        Raises ProviderUnavailable if the whole chain is unconfigured/failing so the
        caller can fall back to scripted P0 behaviour.
        """
        chain = AGENT_PROVIDER_CHAINS.get(agent, [])
        errors: list[str] = []
        for choice in chain:
            if not self.is_configured(choice.provider):
                errors.append(f"{choice.provider}: not configured")
                continue
            try:
                return self._dispatch(choice, prompt, system)
            except NotImplementedError:
                # P0: adapters aren't wired yet even if a key exists.
                errors.append(f"{choice.provider}: adapter not implemented (P0)")
            except Exception as exc:  # noqa: BLE001 - fall through on any provider error
                logger.warning("provider %s failed: %s", choice.provider, exc)
                errors.append(f"{choice.provider}: {exc}")
        raise ProviderUnavailable(
            f"no usable provider for {agent.value}: " + "; ".join(errors or ["empty chain"])
        )

    # ── dispatch + adapters (stubs in P0) ──────────────────────────────────────
    def _dispatch(self, choice: ProviderChoice, prompt: str, system: str | None) -> str:
        if choice.provider == "openai":
            return self._call_openai(choice.model, prompt, system)
        if choice.provider == "anthropic":
            return self._call_anthropic(choice.model, prompt, system)
        if choice.provider == "gemini":
            return self._call_gemini(choice.model, prompt, system)
        if choice.provider == "openrouter":
            return self._call_openrouter(choice.model, prompt, system)
        raise ProviderUnavailable(f"unknown provider {choice.provider!r}")

    def _call_openai(self, model: str, prompt: str, system: str | None) -> str:
        # P1: from openai import OpenAI; client.chat.completions.create(...); log tokens/cost.
        raise NotImplementedError

    def _call_anthropic(self, model: str, prompt: str, system: str | None) -> str:
        """Live Anthropic adapter (D-14). Lazily imports the SDK so the app still runs without it.

        If `anthropic` isn't installed, this raises (caught by `run()` → falls through the chain
        → agents use scripted P0 behaviour). Install with the SDK present + ANTHROPIC_API_KEY set
        to go live. Token/cost logging is a P1 follow-up.
        """
        try:
            import anthropic  # lazy: optional dependency
        except ImportError as exc:  # not installed → treat as unavailable, fall through
            raise RuntimeError("anthropic SDK not installed") from exc

        client = anthropic.Anthropic(api_key=self._key_for("anthropic"))
        msg = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system or "You are a precise assistant. Reply only with what is asked.",
            messages=[{"role": "user", "content": prompt}],
        )
        # Concatenate text blocks from the response.
        return "".join(getattr(b, "text", "") for b in msg.content).strip()

    def _call_gemini(self, model: str, prompt: str, system: str | None) -> str:
        raise NotImplementedError

    def _call_openrouter(self, model: str, prompt: str, system: str | None) -> str:
        raise NotImplementedError


_router: ProviderRouter | None = None


def get_router() -> ProviderRouter:
    global _router
    if _router is None:
        _router = ProviderRouter()
    return _router
