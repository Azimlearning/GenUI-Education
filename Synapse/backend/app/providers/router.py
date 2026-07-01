"""The provider router (ADR-011 / D-05).

Walks an agent's provider chain (`config.AGENT_PROVIDER_CHAINS`) and calls the first
configured provider that succeeds. Two entry points:

- `run()`            — plain text completion (kept for compatibility / simple prompts).
- `run_structured()` — asks the model for a single JSON object, extracts + parses it, and
                       repairs once on malformed output. Returns a `dict`; the calling agent
                       validates it into its Pydantic model and falls back to scripted P0
                       behaviour if validation fails. This is the D-01 seam: the model
                       CONFIGURES a pre-built component, it never emits markup.

Anthropic Claude is the live primary (D-14); OpenAI is the configured fallback. Both adapters
lazy-import their SDK so the app still runs (scripted) when neither key/SDK is present. Every
call is timed and costed into `providers.metrics` for the dev panel (hackAstone TRL signal).
"""

from __future__ import annotations

import json
import logging
import re
import time

from app.config import get_settings
from app.models import AgentName
from app.providers.config import AGENT_PROVIDER_CHAINS, ProviderChoice
from app.providers.metrics import METRICS, LLMCall, estimate_cost

logger = logging.getLogger("synapse.providers")


class ProviderUnavailable(RuntimeError):
    """Raised when no provider in an agent's chain is configured/usable."""


class ProviderResult:
    """A raw text result plus the token/latency bookkeeping the metrics log wants."""

    def __init__(self, text: str, *, input_tokens: int, output_tokens: int) -> None:
        self.text = text
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


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

    def any_live(self, agent: AgentName) -> bool:
        """True if at least one provider in this agent's chain has a key configured."""
        return any(self.is_configured(c.provider) for c in AGENT_PROVIDER_CHAINS.get(agent, []))

    # ── public API ───────────────────────────────────────────────────────────
    def run(self, agent: AgentName, prompt: str, *, system: str | None = None) -> str:
        """Execute the agent's provider chain; return the model's text output."""
        return self._walk_chain(agent, prompt, system).text

    def run_structured(
        self,
        agent: AgentName,
        prompt: str,
        *,
        system: str | None = None,
        schema_hint: str,
    ) -> dict:
        """Return a parsed JSON object from the model.

        `schema_hint` is a short human-readable description of the shape we want; it's appended
        to the system prompt. The model is told to answer with JSON only. We extract the first
        JSON object from the reply; on failure we retry ONCE with an explicit repair instruction
        before giving up (which lets the agent fall back to scripted behaviour).
        """
        json_system = (
            (system or "You are a precise assistant.")
            + "\n\nReturn ONLY a single JSON object, no prose, no markdown fences. "
            + "It must match this shape:\n"
            + schema_hint
        )
        result = self._walk_chain(agent, prompt, json_system)
        parsed = _extract_json(result.text)
        if parsed is not None:
            return parsed

        # Repair pass: hand the malformed text back and ask for valid JSON only.
        repair_prompt = (
            f"Your previous reply was not valid JSON:\n{result.text}\n\n"
            "Reply again with ONLY the JSON object described. No prose."
        )
        result2 = self._walk_chain(agent, repair_prompt, json_system)
        parsed = _extract_json(result2.text)
        if parsed is not None:
            return parsed
        raise ProviderUnavailable(f"{agent.value}: model did not return parseable JSON")

    # ── chain walking + metrics ────────────────────────────────────────────────
    def _walk_chain(
        self, agent: AgentName, prompt: str, system: str | None
    ) -> ProviderResult:
        chain = AGENT_PROVIDER_CHAINS.get(agent, [])
        errors: list[str] = []
        for choice in chain:
            if not self.is_configured(choice.provider):
                errors.append(f"{choice.provider}: not configured")
                continue
            t0 = time.monotonic()
            try:
                result = self._dispatch(choice, prompt, system)
            except NotImplementedError:
                errors.append(f"{choice.provider}: adapter not implemented")
                continue
            except Exception as exc:  # noqa: BLE001 - fall through on any provider error
                latency_ms = int((time.monotonic() - t0) * 1000)
                logger.warning("provider %s failed: %s", choice.provider, exc)
                METRICS.record(
                    LLMCall(agent.value, choice.provider, choice.model, 0, 0, 0.0,
                            latency_ms, ok=False, note=str(exc)[:120])
                )
                errors.append(f"{choice.provider}: {exc}")
                continue
            latency_ms = int((time.monotonic() - t0) * 1000)
            METRICS.record(
                LLMCall(
                    agent.value, choice.provider, choice.model,
                    result.input_tokens, result.output_tokens,
                    estimate_cost(choice.model, result.input_tokens, result.output_tokens),
                    latency_ms, ok=True,
                )
            )
            return result
        raise ProviderUnavailable(
            f"no usable provider for {agent.value}: " + "; ".join(errors or ["empty chain"])
        )

    def _dispatch(self, choice: ProviderChoice, prompt: str, system: str | None) -> ProviderResult:
        if choice.provider == "anthropic":
            return self._call_anthropic(choice.model, prompt, system)
        if choice.provider == "openai":
            return self._call_openai(choice.model, prompt, system)
        raise NotImplementedError

    def _call_anthropic(self, model: str, prompt: str, system: str | None) -> ProviderResult:
        """Live Anthropic adapter (D-14). Lazily imports the SDK so the app runs without it."""
        try:
            import anthropic  # lazy: optional dependency
        except ImportError as exc:
            raise RuntimeError("anthropic SDK not installed") from exc

        client = anthropic.Anthropic(api_key=self._key_for("anthropic"))
        msg = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system or "You are a precise assistant. Reply only with what is asked.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(getattr(b, "text", "") for b in msg.content).strip()
        usage = getattr(msg, "usage", None)
        return ProviderResult(
            text,
            input_tokens=getattr(usage, "input_tokens", 0) or 0,
            output_tokens=getattr(usage, "output_tokens", 0) or 0,
        )

    def _call_openai(self, model: str, prompt: str, system: str | None) -> ProviderResult:
        """OpenAI fallback adapter. Lazy import; only used if OPENAI_API_KEY is set."""
        try:
            from openai import OpenAI  # lazy: optional dependency
        except ImportError as exc:
            raise RuntimeError("openai SDK not installed") from exc

        client = OpenAI(api_key=self._key_for("openai"))
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(model=model, max_tokens=1024, messages=messages)
        text = (resp.choices[0].message.content or "").strip()
        usage = getattr(resp, "usage", None)
        return ProviderResult(
            text,
            input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            output_tokens=getattr(usage, "completion_tokens", 0) or 0,
        )


# ── JSON extraction helper ─────────────────────────────────────────────────────
_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _extract_json(text: str) -> dict | None:
    """Best-effort: pull the first JSON object out of a model reply."""
    if not text:
        return None
    candidate = text.strip()
    fence = _FENCE_RE.search(candidate)
    if fence:
        candidate = fence.group(1).strip()
    # Trim to the outermost braces if there is surrounding prose.
    start, end = candidate.find("{"), candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = candidate[start : end + 1]
    try:
        obj = json.loads(candidate)
        return obj if isinstance(obj, dict) else None
    except (json.JSONDecodeError, ValueError):
        return None


_router: ProviderRouter | None = None


def get_router() -> ProviderRouter:
    global _router
    if _router is None:
        _router = ProviderRouter()
    return _router
