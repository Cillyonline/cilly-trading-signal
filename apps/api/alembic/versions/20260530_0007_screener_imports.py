"""add screener import models

Revision ID: 20260530_0007
Revises: 20260529_0006
Create Date: 2026-05-30

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260530_0007"
down_revision: str | None = "20260529_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    screener_import_source = sa.Enum(
        "tradingview_screener_csv",
        name="screenerimportsource",
    )
    screener_import_status = sa.Enum(
        "pending",
        "validated",
        "failed",
        "imported",
        "partial",
        name="screenerimportstatus",
    )
    screener_result_status = sa.Enum(
        "candidate",
        "watchlist_added",
        "duplicate",
        "rejected",
        "ignored",
        name="screenerresultstatus",
    )
    if bind.dialect.name == "postgresql":
        screener_import_source.create(bind, checkfirst=True)
        screener_import_status.create(bind, checkfirst=True)
        screener_result_status.create(bind, checkfirst=True)

        screener_import_source = postgresql.ENUM(
            "tradingview_screener_csv",
            name="screenerimportsource",
            create_type=False,
        )
        screener_import_status = postgresql.ENUM(
            "pending",
            "validated",
            "failed",
            "imported",
            "partial",
            name="screenerimportstatus",
            create_type=False,
        )
        screener_result_status = postgresql.ENUM(
            "candidate",
            "watchlist_added",
            "duplicate",
            "rejected",
            "ignored",
            name="screenerresultstatus",
            create_type=False,
        )

    asset_class = postgresql.ENUM("stock", "crypto", name="assetclass", create_type=False)

    op.create_table(
        "screener_imports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "source",
            screener_import_source,
            server_default="tradingview_screener_csv",
            nullable=False,
        ),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("asset_class", asset_class, nullable=False),
        sa.Column("screener_preset", sa.String(length=120), nullable=True),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accepted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rejected_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicate_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "status",
            screener_import_status,
            server_default="pending",
            nullable=False,
        ),
        sa.Column("validation_errors", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_screener_imports_user_id"), "screener_imports", ["user_id"])

    op.create_table(
        "screener_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("screener_import_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("watchlist_item_id", sa.Integer(), nullable=True),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("asset_class", asset_class, nullable=False),
        sa.Column("exchange", sa.String(length=64), nullable=True),
        sa.Column("currency", sa.String(length=16), nullable=True),
        sa.Column("sector", sa.String(length=120), nullable=True),
        sa.Column("industry", sa.String(length=120), nullable=True),
        sa.Column("price", sa.Numeric(18, 8), nullable=True),
        sa.Column("change_percent", sa.Numeric(10, 4), nullable=True),
        sa.Column("volume", sa.Numeric(24, 8), nullable=True),
        sa.Column("relative_volume", sa.Numeric(12, 4), nullable=True),
        sa.Column("market_cap", sa.Numeric(24, 2), nullable=True),
        sa.Column("rsi14", sa.Numeric(8, 4), nullable=True),
        sa.Column("ema20", sa.Numeric(18, 8), nullable=True),
        sa.Column("ema50", sa.Numeric(18, 8), nullable=True),
        sa.Column("ema200", sa.Numeric(18, 8), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            screener_result_status,
            server_default="candidate",
            nullable=False,
        ),
        sa.Column("duplicate_of_result_id", sa.Integer(), nullable=True),
        sa.Column("validation_errors", sa.JSON(), nullable=True),
        sa.Column("raw_metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["duplicate_of_result_id"], ["screener_results.id"]),
        sa.ForeignKeyConstraint(["screener_import_id"], ["screener_imports.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["watchlist_item_id"], ["watchlist_items.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "screener_import_id",
            "asset_class",
            "symbol",
            "exchange",
            name="uq_screener_results_import_symbol_exchange",
        ),
    )
    op.create_index(
        op.f("ix_screener_results_screener_import_id"),
        "screener_results",
        ["screener_import_id"],
    )
    op.create_index(op.f("ix_screener_results_symbol"), "screener_results", ["symbol"])
    op.create_index(op.f("ix_screener_results_user_id"), "screener_results", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_screener_results_user_id"), table_name="screener_results")
    op.drop_index(op.f("ix_screener_results_symbol"), table_name="screener_results")
    op.drop_index(
        op.f("ix_screener_results_screener_import_id"), table_name="screener_results"
    )
    op.drop_table("screener_results")
    op.drop_index(op.f("ix_screener_imports_user_id"), table_name="screener_imports")
    op.drop_table("screener_imports")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        postgresql.ENUM(name="screenerresultstatus").drop(bind, checkfirst=True)
        postgresql.ENUM(name="screenerimportstatus").drop(bind, checkfirst=True)
        postgresql.ENUM(name="screenerimportsource").drop(bind, checkfirst=True)
