"""Async engine and session factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    # Short connect timeout: DB writes here are off the request's critical
    # path, and a down database must fail fast, not hang for seconds.
    return create_async_engine(
        get_settings().database_url,
        pool_pre_ping=True,
        connect_args={"timeout": 2},
    )


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """One transaction per unit of work; commits on success, rolls back on error."""
    async with get_sessionmaker()() as session:
        async with session.begin():
            yield session
