"""Thin async wrapper around the Anthropic SDK with usage/cost accounting."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import lru_cache

from anthropic import AsyncAnthropic

from config import get_settings


@dataclass
class LLMResult:
    text: str
    tokens_in: int
    tokens_out: int
    cost_usd: float


class LLMClient:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.llm_enabled:
            raise RuntimeError(
                "LLM client requested but ANTHROPIC_API_KEY is not set (or ECHO_MODE=true)"
            )
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._settings = settings

    def _cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        price_in, price_out = self._settings.price_for(model)
        return tokens_in * price_in / 1_000_000 + tokens_out * price_out / 1_000_000

    async def complete(
        self, *, model: str, system: str, user: str, max_tokens: int = 1024
    ) -> LLMResult:
        """Non-streaming completion (Router-style strict-JSON nodes)."""
        message = await self._client.messages.create(
            model=model,
            system=system,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(block.text for block in message.content if block.type == "text")
        tokens_in = message.usage.input_tokens
        tokens_out = message.usage.output_tokens
        return LLMResult(text, tokens_in, tokens_out, self._cost(model, tokens_in, tokens_out))

    async def stream(
        self,
        *,
        model: str,
        system: str,
        user: str,
        max_tokens: int = 1024,
        on_chunk: Callable[[str], Awaitable[None]],
    ) -> LLMResult:
        """Streaming completion; awaits on_chunk for every text delta."""
        async with self._client.messages.stream(
            model=model,
            system=system,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": user}],
        ) as stream:
            async for chunk in stream.text_stream:
                await on_chunk(chunk)
            message = await stream.get_final_message()
        text = "".join(block.text for block in message.content if block.type == "text")
        tokens_in = message.usage.input_tokens
        tokens_out = message.usage.output_tokens
        return LLMResult(text, tokens_in, tokens_out, self._cost(model, tokens_in, tokens_out))


@lru_cache
def get_llm() -> LLMClient:
    return LLMClient()
