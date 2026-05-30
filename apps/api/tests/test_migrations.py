from importlib import util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

from sqlalchemy import Column, Integer, MetaData, Table, create_engine, inspect, text
from sqlalchemy.schema import CreateColumn


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


def test_market_data_source_freshness_migration_exists() -> None:
    migration_path = Path("alembic/versions/20260529_0006_market_data_source_freshness.py")

    assert migration_path.exists()


def test_market_data_source_freshness_migration_adds_metadata_columns() -> None:
    migration = Path("alembic/versions/20260529_0006_market_data_source_freshness.py").read_text()

    for column_name in (
        "provider_name",
        "provider_symbol",
        "provider_exchange",
        "provider_timeframe",
        "last_synced_at",
        "freshness_status",
        "sync_status",
        "sync_error_code",
        "sync_error_message",
    ):
        assert f'"{column_name}"' in migration

    assert "server_default=\"unknown\"" in migration
    assert "server_default=\"not_applicable\"" in migration


def test_screener_imports_migration_exists() -> None:
    migration_path = Path("alembic/versions/20260530_0007_screener_imports.py")

    assert migration_path.exists()


def test_screener_imports_migration_adds_review_candidate_tables() -> None:
    migration = Path("alembic/versions/20260530_0007_screener_imports.py").read_text()

    for table_name in ("screener_imports", "screener_results"):
        assert f'"{table_name}"' in migration

    for column_name in (
        "source",
        "asset_class",
        "screener_preset",
        "accepted_count",
        "duplicate_count",
        "watchlist_item_id",
        "duplicate_of_result_id",
        "raw_metadata",
    ):
        assert f'"{column_name}"' in migration

    assert "uq_screener_results_import_symbol_exchange" in migration


def test_alembic_migrations_apply_cleanly_to_sqlite(tmp_path: Path) -> None:
    database_path = tmp_path / "migration-smoke.db"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        metadata = MetaData()
        Table("market_data_series", metadata, Column("id", Integer, primary_key=True))
        metadata.create_all(engine)

        migration_path = Path("alembic/versions/20260529_0006_market_data_source_freshness.py")
        spec = util.spec_from_file_location("market_data_source_freshness", migration_path)
        assert spec is not None
        assert spec.loader is not None
        migration = util.module_from_spec(spec)

        original_alembic = sys.modules.pop("alembic", None)
        fake_alembic = ModuleType("alembic")
        fake_alembic.op = SimpleNamespace()
        try:
            sys.modules["alembic"] = fake_alembic
            spec.loader.exec_module(migration)
        finally:
            if original_alembic is not None:
                sys.modules["alembic"] = original_alembic
            else:
                sys.modules.pop("alembic", None)

        with engine.begin() as connection:
            def add_column(table_name: str, column: Column) -> None:
                column_sql = CreateColumn(column).compile(dialect=connection.dialect)
                connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_sql}"))

            migration.op = SimpleNamespace(
                get_bind=lambda: connection,
                execute=connection.execute,
                add_column=add_column,
            )
            migration.upgrade()

        columns = {column["name"] for column in inspect(engine).get_columns("market_data_series")}
    finally:
        engine.dispose()

    assert "freshness_status" in columns
    assert "sync_status" in columns
