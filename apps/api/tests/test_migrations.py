from pathlib import Path


def test_initial_migration_exists() -> None:
    migration_path = Path("alembic/versions/20260513_0001_initial_schema.py")

    assert migration_path.exists()


def test_initial_migration_contains_mvp_tables() -> None:
    migration = Path("alembic/versions/20260513_0001_initial_schema.py").read_text()

    for table_name in (
        "users",
        "settings",
        "watchlist_items",
        "market_data_series",
        "market_data_candles",
        "indicator_snapshots",
        "signals",
        "trades",
        "trade_events",
        "journal_entries",
    ):
        assert f'"{table_name}"' in migration
