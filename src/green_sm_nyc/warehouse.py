"""Idempotent loading of sample or official TLC inputs into DuckDB raw objects."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import duckdb

from green_sm_nyc.config import RAW_DIR, SAMPLE_DIR, WAREHOUSE_PATH


def _sql_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def _create_from_csv(con: duckdb.DuckDBPyConnection, table: str, path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required input does not exist: {path}")
    con.execute(
        f"create or replace table raw.{table} as "
        f"select *, '{_sql_path(path)}'::varchar as source_file, "
        f"row_number() over () - 1 as source_row_number "
        f"from read_csv_auto('{_sql_path(path)}', header=true)"
    )


def _create_from_parquet(con: duckdb.DuckDBPyConnection, table: str, pattern: Path) -> int:
    files = sorted(pattern.parent.glob(pattern.name))
    if not files:
        raise FileNotFoundError(f"No Parquet files match: {pattern}")
    file_sql = ", ".join(f"'{_sql_path(path)}'" for path in files)
    con.execute(
        f"create or replace view raw.{table} as "
        f"select *, filename as source_file, file_row_number as source_row_number "
        f"from read_parquet([{file_sql}], union_by_name=true, "
        f"filename=true, file_row_number=true)"
    )
    return len(files)


def _drop_relation(con: duckdb.DuckDBPyConnection, relation: str) -> None:
    row = con.execute(
        """
        select table_type
        from information_schema.tables
        where table_schema = 'raw' and table_name = ?
        """,
        [relation],
    ).fetchone()
    if not row:
        return
    object_type = "view" if row[0] == "VIEW" else "table"
    con.execute(f"drop {object_type} raw.{relation}")


def load_raw(
    mode: str = "sample",
    warehouse_path: Path = WAREHOUSE_PATH,
    sample_dir: Path = SAMPLE_DIR,
    raw_dir: Path = RAW_DIR,
) -> dict[str, int | str]:
    """Replace raw relations and return source counts. Safe to rerun."""
    if mode not in {"sample", "local"}:
        raise ValueError("mode must be 'sample' or 'local'")

    warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(warehouse_path))
    try:
        con.execute("create schema if not exists raw")
        for relation in ("yellow_trips", "fhvhv_trips", "taxi_zones"):
            _drop_relation(con, relation)

        if mode == "sample":
            _create_from_csv(con, "yellow_trips", sample_dir / "yellow_trips.csv")
            _create_from_csv(con, "fhvhv_trips", sample_dir / "fhvhv_trips.csv")
            _create_from_csv(con, "taxi_zones", sample_dir / "taxi_zones.csv")
            source_files = 3
        else:
            yellow_files = _create_from_parquet(
                con, "yellow_trips", raw_dir / "yellow" / "*.parquet"
            )
            fhvhv_files = _create_from_parquet(con, "fhvhv_trips", raw_dir / "fhvhv" / "*.parquet")
            zone_path = raw_dir / "taxi_zone_lookup.csv"
            _create_from_csv(con, "taxi_zones", zone_path)
            source_files = yellow_files + fhvhv_files + 1

        counts = {
            "yellow_trips": con.execute("select count(*) from raw.yellow_trips").fetchone()[0],
            "fhvhv_trips": con.execute("select count(*) from raw.fhvhv_trips").fetchone()[0],
            "zones": con.execute("select count(*) from raw.taxi_zones").fetchone()[0],
            "mode": mode,
            "source_files": source_files,
        }
        con.execute(
            """
            create or replace table raw.pipeline_metadata as
            select ?::varchar as data_mode,
                   ?::timestamp as loaded_at_utc,
                   ?::integer as source_file_count
            """,
            [mode, datetime.now(UTC).replace(tzinfo=None), source_files],
        )
        return counts
    finally:
        con.close()
