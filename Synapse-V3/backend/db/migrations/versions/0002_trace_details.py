"""Add structured trace details for router shadow comparisons.

Revision ID: 0002_trace_details
Revises: 0001
Create Date: 2026-07-18
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_trace_details"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("traces", sa.Column("details", postgresql.JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("traces", "details")
