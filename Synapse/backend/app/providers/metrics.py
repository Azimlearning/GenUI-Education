"""Per-call LLM observability (hackAstone TRL signal).

Every LLM call through the router records provider, model, agent, token counts, an
estimated cost, and latency / time-to-first-token. Kept in a small in-memory ring buffer
the dev panel reads via GET /api/metrics. Deliberately dependency-free.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Any

# Rough USD per 1M tokens (input, output). Only used for the dev cost readout — not billing.
# Sources: the claude-api skill's model table (2026-06). OpenAI values are ballpark fallbacks.
_PRICING: dict[str, tuple[float, float]] = {
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-5": (3.00, 15.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
}


@dataclass
class LLMCall:
    agent: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    ok: bool
    note: str = ""


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    in_rate, out_rate = _PRICING.get(model, (0.0, 0.0))
    return round((input_tokens * in_rate + output_tokens * out_rate) / 1_000_000, 6)


class _Metrics:
    def __init__(self, maxlen: int = 200) -> None:
        self._calls: deque[LLMCall] = deque(maxlen=maxlen)
        self._lock = Lock()

    def record(self, call: LLMCall) -> None:
        with self._lock:
            self._calls.append(call)

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock:
            items = list(self._calls)[-limit:]
        return [asdict(c) for c in reversed(items)]

    def summary(self) -> dict[str, Any]:
        with self._lock:
            calls = list(self._calls)
        if not calls:
            return {"count": 0, "total_cost_usd": 0.0, "avg_latency_ms": 0, "ok_rate": 1.0}
        ok = [c for c in calls if c.ok]
        return {
            "count": len(calls),
            "total_cost_usd": round(sum(c.cost_usd for c in calls), 6),
            "avg_latency_ms": int(sum(c.latency_ms for c in calls) / len(calls)),
            "ok_rate": round(len(ok) / len(calls), 3),
        }


METRICS = _Metrics()
