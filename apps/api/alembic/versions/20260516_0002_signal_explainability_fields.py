"""add signal explainability fields

Revision ID: 20260516_0002
Revises: 20260513_0001
Create Date: 2026-05-16

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260516_0002"
down_revision: str | None = "20260513_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("no_trade_reasons", sa.JSON(), nullable=True))
    op.add_column("signals", sa.Column("next_action", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("signals", "next_action")
    op.drop_column("signals", "no_trade_reasons")
