"""Fire-and-forget task spawning for writes that must never block the stream.

Telemetry (traces) and chat persistence (sessions, messages) are off the
request's critical path: a down database costs seconds per awaited call,
which showed up as 19s to first token in the Phase 1 live smoke. Tasks are
kept in a strong-reference set (asyncio holds only weak refs) and log their
exceptions instead of dying silently.
"""

import asyncio
import logging
from collections.abc import Coroutine

logger = logging.getLogger(__name__)

_pending: set[asyncio.Task] = set()


def spawn(coro: Coroutine, *, name: str) -> asyncio.Task:
    task = asyncio.get_running_loop().create_task(coro, name=name)
    _pending.add(task)
    task.add_done_callback(_finish)
    return task


def _finish(task: asyncio.Task) -> None:
    _pending.discard(task)
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error("background task %s failed: %s", task.get_name(), exc, exc_info=exc)
