"""add signal review events

Revision ID: 20260517_0005
Revises: 20260517_0004
Create Date: 2026-05-17

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260517_0005"
down_revision: str | None = "20260517_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    signalstatus = postgresql.ENUM(
        "watchlist",
        "armed",
        "triggered",
        "invalidated",
        "no_setup",
        "missed",
        "expired",
        name="signalstatus",
        create_type=False,
    )
    op.create_table(
        "signal_review_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("previous_status", signalstatus, nullable=True),
        sa.Column("new_status", signalstatus, nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_signal_review_events_signal_id"),
        "signal_review_events",
        ["signal_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_signal_review_events_user_id"),
        "signal_review_events",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_signal_review_events_user_id"), table_name="signal_review_events")
    op.drop_index(op.f("ix_signal_review_events_signal_id"), table_name="signal_review_events")
    op.drop_table("signal_review_events")
