"""add signal review note

Revision ID: 20260517_0004
Revises: 20260516_0003
Create Date: 2026-05-17

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260517_0004"
down_revision: str | None = "20260516_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("review_note", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("signals", "review_note")
