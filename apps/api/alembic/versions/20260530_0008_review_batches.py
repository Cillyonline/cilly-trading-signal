"""add review batches

Revision ID: 20260530_0008
Revises: 20260530_0007
Create Date: 2026-05-30

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260530_0008"
down_revision: str | None = "20260530_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    review_batch_type = sa.Enum("historical", "paper", name="reviewbatchtype")
    manual_review_label = sa.Enum(
        "useful", "too_permissive", "too_strict", "unclear", name="manualreviewlabel"
    )
    if bind.dialect.name == "postgresql":
        review_batch_type.create(bind, checkfirst=True)
        manual_review_label.create(bind, checkfirst=True)
        review_batch_type = postgresql.ENUM(
            "historical", "paper", name="reviewbatchtype", create_type=False
        )
        manual_review_label = postgresql.ENUM(
            "useful",
            "too_permissive",
            "too_strict",
            "unclear",
            name="manualreviewlabel",
            create_type=False,
        )

    asset_class = postgresql.ENUM("stock", "crypto", name="assetclass", create_type=False)
    strategy_type = postgresql.ENUM(
        "trend_pullback_long", "base_breakout_long", name="strategytype", create_type=False
    )
    signal_status = postgresql.ENUM(
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
    score_class = postgresql.ENUM(
        "a_setup", "b_setup", "watchlist", "no_trade", name="scoreclass", create_type=False
    )

    op.create_table(
        "review_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("review_type", review_batch_type, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("asset_class", asset_class, nullable=True),
        sa.Column("strategy_type", strategy_type, nullable=True),
        sa.Column("review_window_start", sa.Date(), nullable=True),
        sa.Column("review_window_end", sa.Date(), nullable=True),
        sa.Column("data_source", sa.String(length=160), nullable=True),
        sa.Column("context_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_batches_user_id"), "review_batches", ["user_id"])

    op.create_table(
        "review_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=True),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("asset_class", asset_class, nullable=False),
        sa.Column("strategy_type", strategy_type, nullable=False),
        sa.Column("stored_data_start", sa.Date(), nullable=True),
        sa.Column("stored_data_end", sa.Date(), nullable=True),
        sa.Column("benchmark_context", sa.String(length=32), nullable=True),
        sa.Column("signal_status", signal_status, nullable=False),
        sa.Column("score_class", score_class, nullable=True),
        sa.Column("no_trade_reasons", sa.JSON(), nullable=True),
        sa.Column("risk_flags", sa.JSON(), nullable=True),
        sa.Column("quality_blockers", sa.JSON(), nullable=True),
        sa.Column("entry_price", sa.Numeric(18, 8), nullable=True),
        sa.Column("stop_loss", sa.Numeric(18, 8), nullable=True),
        sa.Column("target_price", sa.Numeric(18, 8), nullable=True),
        sa.Column("planned_risk_reward", sa.Numeric(8, 2), nullable=True),
        sa.Column("manual_review_label", manual_review_label, nullable=False),
        sa.Column("outcome_r", sa.Numeric(8, 4), nullable=True),
        sa.Column("outcome_measurement_rule", sa.Text(), nullable=True),
        sa.Column("follow_up_needed", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("follow_up_issue_url", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["batch_id"], ["review_batches.id"]),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_entries_batch_id"), "review_entries", ["batch_id"])
    op.create_index(op.f("ix_review_entries_signal_id"), "review_entries", ["signal_id"])
    op.create_index(op.f("ix_review_entries_symbol"), "review_entries", ["symbol"])
    op.create_index(op.f("ix_review_entries_user_id"), "review_entries", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_review_entries_user_id"), table_name="review_entries")
    op.drop_index(op.f("ix_review_entries_symbol"), table_name="review_entries")
    op.drop_index(op.f("ix_review_entries_signal_id"), table_name="review_entries")
    op.drop_index(op.f("ix_review_entries_batch_id"), table_name="review_entries")
    op.drop_table("review_entries")
    op.drop_index(op.f("ix_review_batches_user_id"), table_name="review_batches")
    op.drop_table("review_batches")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        postgresql.ENUM(name="manualreviewlabel").drop(bind, checkfirst=True)
        postgresql.ENUM(name="reviewbatchtype").drop(bind, checkfirst=True)
