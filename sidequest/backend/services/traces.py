"""Trace logging: every LangGraph node call writes one row to `traces`.

The cost dashboard and eval metrics read from this table; during prompt
tuning it is the primary debugging surface (SYSTEM_ARCHITECTURE.md section 9).
Writes are best-effort: a down database must never break the user stream,
but failures are logged loudly.
"""

import logging

from db.models import Trace
from db.session import session_scope

logger = logging.getLogger(__name__)


async def record_trace(
    *,
    run_id: str,
    session_id: str,
    node: str,
    model: str | None = None,
    prompt_version: str | None = None,
    tokens_in: int | None = None,
    tokens_out: int | None = None,
    cost_usd: float | None = None,
    latency_ms: int | None = None,
    verdict: str | None = None,
    retry_index: int = 0,
    error: str | None = None,
) -> None:
    try:
        async with session_scope() as session:
            session.add(
                Trace(
                    run_id=run_id,
                    session_id=session_id,
                    node=node,
                    model=model,
                    prompt_version=prompt_version,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    cost_usd=cost_usd,
                    latency_ms=latency_ms,
                    verdict=verdict,
                    retry_index=retry_index,
                    error=error,
                )
            )
    except Exception:
        logger.exception("trace write failed (run_id=%s node=%s)", run_id, node)
