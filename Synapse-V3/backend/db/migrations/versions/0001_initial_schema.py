"""Initial schema: artifacts, sessions, messages, interaction_events, feedback, traces.

Mirrors docs/DATA_MODEL.md.

Revision ID: 0001
Revises:
Create Date: 2026-07-16

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

NOW = sa.text("now()")
TSTZ = postgresql.TIMESTAMP(timezone=True)


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("created_at", TSTZ, nullable=False, server_default=NOW),
        sa.Column("last_active", TSTZ, nullable=False, server_default=NOW),
        sa.Column("gen_count_window", sa.Integer, nullable=False, server_default="0"),
        sa.Column("gen_window_start", TSTZ, nullable=True),
    )

    op.create_table(
        "artifacts",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("cache_key", sa.Text, nullable=False, unique=True),
        sa.Column("canonical_concept", sa.Text, nullable=False),
        sa.Column("domain", sa.Text, nullable=False),
        sa.Column("artifact_type", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("plan", postgresql.JSONB, nullable=False),
        sa.Column("html", sa.Text, nullable=False),
        sa.Column("verifier_report", postgresql.JSONB, nullable=False),
        sa.Column("screenshot_path", sa.Text, nullable=True),
        sa.Column("model_version", sa.Text, nullable=False),
        sa.Column("prompt_version", sa.Text, nullable=False),
        sa.Column("size_bytes", sa.Integer, nullable=False),
        sa.Column("serve_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("rating_sum", sa.Integer, nullable=False, server_default="0"),
        sa.Column("rating_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("evicted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("evicted_reason", sa.Text, nullable=True),
        sa.Column("created_at", TSTZ, nullable=False, server_default=NOW),
    )
    op.create_index(
        "idx_artifacts_library",
        "artifacts",
        ["domain", "evicted", sa.text("created_at DESC")],
    )
    op.create_index("idx_artifacts_concept", "artifacts", ["canonical_concept"])

    op.create_table(
        "messages",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Text, sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("artifact_id", sa.Text, sa.ForeignKey("artifacts.id"), nullable=True),
        sa.Column("created_at", TSTZ, nullable=False, server_default=NOW),
    )
    op.create_index("idx_messages_session", "messages", ["session_id", "id"])

    op.create_table(
        "interaction_events",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Text, sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("artifact_id", sa.Text, sa.ForeignKey("artifacts.id"), nullable=False),
        sa.Column("control", sa.Text, nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("ts", TSTZ, nullable=False),
    )
    op.create_index(
        "idx_events_session_artifact",
        "interaction_events",
        ["session_id", "artifact_id", "ts"],
    )

    op.create_table(
        "feedback",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("artifact_id", sa.Text, sa.ForeignKey("artifacts.id"), nullable=False),
        sa.Column("session_id", sa.Text, sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("rating", sa.SmallInteger, nullable=False),
        sa.Column("flag_reason", sa.Text, nullable=True),
        sa.Column("created_at", TSTZ, nullable=False, server_default=NOW),
        sa.UniqueConstraint("artifact_id", "session_id"),
    )

    op.create_table(
        "traces",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("run_id", sa.Text, nullable=False),
        sa.Column("session_id", sa.Text, nullable=False),
        sa.Column("node", sa.Text, nullable=False),
        sa.Column("model", sa.Text, nullable=True),
        sa.Column("prompt_version", sa.Text, nullable=True),
        sa.Column("tokens_in", sa.Integer, nullable=True),
        sa.Column("tokens_out", sa.Integer, nullable=True),
        sa.Column("cost_usd", sa.Numeric(8, 5), nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("verdict", sa.Text, nullable=True),
        sa.Column("retry_index", sa.SmallInteger, nullable=False, server_default="0"),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", TSTZ, nullable=False, server_default=NOW),
    )
    op.create_index("idx_traces_run", "traces", ["run_id"])
    op.create_index("idx_traces_cost", "traces", ["created_at", "cost_usd"])


def downgrade() -> None:
    op.drop_table("traces")
    op.drop_table("feedback")
    op.drop_table("interaction_events")
    op.drop_table("messages")
    op.drop_table("artifacts")
    op.drop_table("sessions")
