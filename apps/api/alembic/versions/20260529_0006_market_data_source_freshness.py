"""add market data source freshness metadata

Revision ID: 20260529_0006
Revises: 20260517_0005
Create Date: 2026-05-29

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260529_0006"
down_revision: str | None = "20260517_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE marketdatasource ADD VALUE IF NOT EXISTS 'provider'")
        op.execute("ALTER TYPE marketdatasource ADD VALUE IF NOT EXISTS 'unknown'")

    freshness_status = sa.Enum(
        "fresh",
        "stale",
        "unknown",
        "failed",
        "partial",
        name="marketdatafreshnessstatus",
    )
    sync_status = sa.Enum(
        "not_applicable",
        "success",
        "skipped",
        "failed",
        "partial",
        name="marketdatasyncstatus",
    )
    if bind.dialect.name == "postgresql":
        freshness_status.create(bind, checkfirst=True)
        sync_status.create(bind, checkfirst=True)

    op.add_column(
        "market_data_series", sa.Column("provider_name", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "market_data_series", sa.Column("provider_symbol", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "market_data_series", sa.Column("provider_exchange", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "market_data_series", sa.Column("provider_timeframe", sa.String(length=32), nullable=True)
    )
    op.add_column(
        "market_data_series", sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "market_data_series",
        sa.Column(
            "freshness_status",
            freshness_status,
            server_default="unknown",
            nullable=False,
        ),
    )
    op.add_column(
        "market_data_series",
        sa.Column(
            "sync_status",
            sync_status,
            server_default="not_applicable",
            nullable=False,
        ),
    )
    op.add_column(
        "market_data_series", sa.Column("sync_error_code", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "market_data_series", sa.Column("sync_error_message", sa.String(length=512), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("market_data_series", "sync_error_message")
    op.drop_column("market_data_series", "sync_error_code")
    op.drop_column("market_data_series", "sync_status")
    op.drop_column("market_data_series", "freshness_status")
    op.drop_column("market_data_series", "last_synced_at")
    op.drop_column("market_data_series", "provider_timeframe")
    op.drop_column("market_data_series", "provider_exchange")
    op.drop_column("market_data_series", "provider_symbol")
    op.drop_column("market_data_series", "provider_name")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        postgresql.ENUM(name="marketdatasyncstatus").drop(bind, checkfirst=True)
        postgresql.ENUM(name="marketdatafreshnessstatus").drop(bind, checkfirst=True)
