"""Record the timezone used to interpret provider candle intervals."""

from alembic import op
import sqlalchemy as sa

revision = "20260911_0011"
down_revision = "20260531_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("market_data_series", sa.Column("timestamp_timezone", sa.String(64)))


def downgrade() -> None:
    op.drop_column("market_data_series", "timestamp_timezone")
