"""add review entry finding category audit fields

Revision ID: 20260531_0010
Revises: 20260531_0009
Create Date: 2026-05-31

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260531_0010"
down_revision: str | None = "20260531_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "review_entries",
        sa.Column(
            "finding_category", sa.String(length=64), nullable=False, server_default="unknown"
        ),
    )
    op.add_column(
        "review_entries",
        sa.Column(
            "finding_category_source",
            sa.String(length=32),
            nullable=False,
            server_default="derived",
        ),
    )


def downgrade() -> None:
    op.drop_column("review_entries", "finding_category_source")
    op.drop_column("review_entries", "finding_category")
