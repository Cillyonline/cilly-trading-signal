"""add alert foundation

Revision ID: 20260516_0003
Revises: 20260516_0002
Create Date: 2026-05-16

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260516_0003"
down_revision: str | None = "20260516_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    alerttype = sa.Enum(
        "info",
        "watchlist",
        "armed",
        "near_trigger",
        "entry_trigger",
        "management",
        "exit_warning",
        "exit_signal",
        "invalidation",
        name="alerttype",
    )
    alertstatus = sa.Enum(
        "active",
        "triggered",
        "resolved",
        "cancelled",
        "expired",
        name="alertstatus",
    )
    alertsource = sa.Enum("manual", "tradingview_webhook", "system", name="alertsource")
    alertdeliverystatus = sa.Enum(
        "pending", "sent", "failed", "skipped", name="alertdeliverystatus"
    )
    notificationchannel = sa.Enum("telegram", name="notificationchannel")
    timeframe = postgresql.ENUM("1W", "1D", "4H", name="timeframe", create_type=False)

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=True),
        sa.Column("trade_id", sa.Integer(), nullable=True),
        sa.Column("watchlist_item_id", sa.Integer(), nullable=True),
        sa.Column("alert_type", alerttype, nullable=False),
        sa.Column("status", alertstatus, nullable=False),
        sa.Column("source", alertsource, nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("trigger_level", sa.Numeric(18, 8), nullable=True),
        sa.Column("timeframe", timeframe, nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("source_payload", sa.JSON(), nullable=True),
        sa.Column("delivery_status", alertdeliverystatus, nullable=False),
        sa.Column("delivery_error", sa.Text(), nullable=True),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"]),
        sa.ForeignKeyConstraint(["trade_id"], ["trades.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["watchlist_item_id"], ["watchlist_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_signal_id"), "alerts", ["signal_id"], unique=False)
    op.create_index(op.f("ix_alerts_trade_id"), "alerts", ["trade_id"], unique=False)
    op.create_index(op.f("ix_alerts_user_id"), "alerts", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_alerts_watchlist_item_id"), "alerts", ["watchlist_item_id"], unique=False
    )

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=True),
        sa.Column("channel", notificationchannel, nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", alertdeliverystatus, nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("provider_payload", sa.JSON(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notification_logs_alert_id"), "notification_logs", ["alert_id"], unique=False
    )
    op.create_index(
        op.f("ix_notification_logs_user_id"), "notification_logs", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_notification_logs_user_id"), table_name="notification_logs")
    op.drop_index(op.f("ix_notification_logs_alert_id"), table_name="notification_logs")
    op.drop_table("notification_logs")
    op.drop_index(op.f("ix_alerts_watchlist_item_id"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_user_id"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_trade_id"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_signal_id"), table_name="alerts")
    op.drop_table("alerts")

    for enum_name in (
        "notificationchannel",
        "alertdeliverystatus",
        "alertsource",
        "alertstatus",
        "alerttype",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
