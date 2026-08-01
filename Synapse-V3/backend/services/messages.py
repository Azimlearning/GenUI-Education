"""Session and message persistence.

Best-effort in dev (a down database must not kill the SSE stream), but every
failure is logged loudly. In docker-compose the database is always up.
"""

import logging

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from db.models import Message, Session
from db.session import session_scope

logger = logging.getLogger(__name__)


async def ensure_session(session_id: str) -> None:
    """Create the session row if new; bump last_active either way."""
    try:
        async with session_scope() as db:
            stmt = (
                insert(Session)
                .values(id=session_id)
                .on_conflict_do_update(
                    index_elements=[Session.id], set_={"last_active": text("now()")}
                )
            )
            await db.execute(stmt)
    except Exception:
        logger.exception("ensure_session failed (session_id=%s)", session_id)


async def save_message(
    session_id: str, role: str, content: str, artifact_id: str | None = None
) -> None:
    try:
        async with session_scope() as db:
            db.add(
                Message(
                    session_id=session_id, role=role, content=content, artifact_id=artifact_id
                )
            )
    except Exception:
        logger.exception("save_message failed (session_id=%s role=%s)", session_id, role)
