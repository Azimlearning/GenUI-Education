"""Trace logging: every LangGraph node call writes one row to `traces`.

The cost dashboard and eval metrics read from this table; during prompt
tuning it is the primary debugging surface (SYSTEM_ARCHITECTURE.md section 9).
Writes are fire-and-forget: telemetry must never block or delay the user
stream (a down database was costing ~4s per awaited write), but every
failure is logged loudly.
"""

import logging

from db.models import Trace
from db.session import session_scope
from services.background import spawn

logger = logging.getLogger(__name__)


def record_trace(
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
    details: dict | None = None,
) -> None:
    """Schedule the trace write in the background and return immediately."""
    spawn(
        _write(
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
            details=details,
        ),
        name=f"trace:{node}:{run_id}",
    )


async def _write(**fields) -> None:
    try:
        async with session_scope() as session:
            session.add(Trace(**fields))
    except Exception:
        logger.exception(
            "trace write failed (run_id=%s node=%s)", fields["run_id"], fields["node"]
        )
