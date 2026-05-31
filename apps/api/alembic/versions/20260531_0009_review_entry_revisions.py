"""add review entry revisions

Revision ID: 20260531_0009
Revises: 20260530_0008
Create Date: 2026-05-31

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260531_0009"
down_revision: str | None = "20260530_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "review_entry_revisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("previous_values", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["batch_id"], ["review_batches.id"]),
        sa.ForeignKeyConstraint(["entry_id"], ["review_entries.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_review_entry_revisions_batch_id"), "review_entry_revisions", ["batch_id"]
    )
    op.create_index(
        op.f("ix_review_entry_revisions_entry_id"), "review_entry_revisions", ["entry_id"]
    )
    op.create_index(
        op.f("ix_review_entry_revisions_user_id"), "review_entry_revisions", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_review_entry_revisions_user_id"), table_name="review_entry_revisions")
    op.drop_index(op.f("ix_review_entry_revisions_entry_id"), table_name="review_entry_revisions")
    op.drop_index(op.f("ix_review_entry_revisions_batch_id"), table_name="review_entry_revisions")
    op.drop_table("review_entry_revisions")
