"""Per-request run context threaded through LangGraph via config["configurable"].

Nodes never touch the SSE transport directly; they emit typed payloads
through the context and the API layer owns the wire format.
"""

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

from schemas.events import Usage

Emit = Callable[[BaseModel], Awaitable[None]]


@dataclass
class RunContext:
    run_id: str
    session_id: str
    emit: Emit
    started_at: float = field(default_factory=time.monotonic)
    usage: Usage = field(default_factory=Usage)
    first_token_ms: int | None = None

    def add_usage(self, tokens_in: int, tokens_out: int, cost_usd: float) -> None:
        self.usage.tokens_in += tokens_in
        self.usage.tokens_out += tokens_out
        self.usage.cost_usd = round(self.usage.cost_usd + cost_usd, 6)

    def mark_first_token(self) -> None:
        if self.first_token_ms is None:
            self.first_token_ms = self.elapsed_ms()

    def elapsed_ms(self) -> int:
        return int((time.monotonic() - self.started_at) * 1000)


def get_ctx(config: RunnableConfig) -> RunContext:
    return config["configurable"]["ctx"]
