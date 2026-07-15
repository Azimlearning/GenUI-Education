"""SQLAlchemy models. Design intent lives in docs/DATA_MODEL.md; the Alembic
migrations under db/migrations are the source of truth. Update both together."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
        dict: JSON().with_variant(JSONB(), "postgresql"),
    }


NOW = text("now()")


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(Text, primary_key=True)  # art_<nanoid>
    cache_key: Mapped[str] = mapped_column(Text, unique=True)  # sha256(domain|type|concept)
    canonical_concept: Mapped[str] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(Text)
    artifact_type: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    plan: Mapped[dict] = mapped_column()  # ArtifactPlan
    html: Mapped[str] = mapped_column(Text)  # post-processed, verified
    verifier_report: Mapped[dict] = mapped_column()
    screenshot_path: Mapped[str | None] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(Text)
    prompt_version: Mapped[str] = mapped_column(Text)
    size_bytes: Mapped[int] = mapped_column(Integer)
    serve_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    rating_sum: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    rating_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    evicted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    evicted_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=NOW)

    __table_args__ = (
        Index("idx_artifacts_library", "domain", "evicted", created_at.desc()),
        Index("idx_artifacts_concept", "canonical_concept"),
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(Text, primary_key=True)  # server-issued opaque
    created_at: Mapped[datetime] = mapped_column(server_default=NOW)
    last_active: Mapped[datetime] = mapped_column(server_default=NOW)
    gen_count_window: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    gen_window_start: Mapped[datetime | None] = mapped_column()


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(Text, ForeignKey("sessions.id"))
    role: Mapped[str] = mapped_column(Text)  # user|assistant|tutor
    content: Mapped[str] = mapped_column(Text)
    artifact_id: Mapped[str | None] = mapped_column(Text, ForeignKey("artifacts.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=NOW)

    __table_args__ = (Index("idx_messages_session", "session_id", "id"),)


class InteractionEvent(Base):
    __tablename__ = "interaction_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(Text, ForeignKey("sessions.id"))
    artifact_id: Mapped[str] = mapped_column(Text, ForeignKey("artifacts.id"))
    control: Mapped[str] = mapped_column(Text)
    value: Mapped[str] = mapped_column(Text)  # stringified; typed client-side only
    ts: Mapped[datetime] = mapped_column()

    __table_args__ = (
        Index("idx_events_session_artifact", "session_id", "artifact_id", "ts"),
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    artifact_id: Mapped[str] = mapped_column(Text, ForeignKey("artifacts.id"))
    session_id: Mapped[str] = mapped_column(Text, ForeignKey("sessions.id"))
    rating: Mapped[int] = mapped_column(SmallInteger)  # 1 | -1
    flag_reason: Mapped[str | None] = mapped_column(Text)  # wrong_science|broken|confusing
    created_at: Mapped[datetime] = mapped_column(server_default=NOW)

    __table_args__ = (UniqueConstraint("artifact_id", "session_id"),)


class Trace(Base):
    __tablename__ = "traces"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(Text)  # one per /ask or /modify request
    session_id: Mapped[str] = mapped_column(Text)
    node: Mapped[str] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(Text)
    prompt_version: Mapped[str | None] = mapped_column(Text)
    tokens_in: Mapped[int | None] = mapped_column(Integer)
    tokens_out: Mapped[int | None] = mapped_column(Integer)
    cost_usd: Mapped[float | None] = mapped_column(Numeric(8, 5))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    verdict: Mapped[str | None] = mapped_column(Text)  # verifier only: pass|fail
    retry_index: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0")
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=NOW)

    __table_args__ = (
        Index("idx_traces_run", "run_id"),
        Index("idx_traces_cost", "created_at", "cost_usd"),
    )
