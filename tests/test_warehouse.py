from __future__ import annotations

from pathlib import Path

import duckdb

from green_sm_nyc.sample_data import generate_sample
from green_sm_nyc.warehouse import load_raw


def test_raw_load_is_idempotent(tmp_path: Path) -> None:
    sample_dir = tmp_path / "sample"
    warehouse_path = tmp_path / "warehouse" / "test.duckdb"
    generated = generate_sample(sample_dir)

    first = load_raw(warehouse_path=warehouse_path, sample_dir=sample_dir)
    second = load_raw(warehouse_path=warehouse_path, sample_dir=sample_dir)

    assert first == second
    assert first["yellow_trips"] == generated["yellow_trips"]
    assert first["fhvhv_trips"] == generated["fhvhv_trips"]

    con = duckdb.connect(str(warehouse_path), read_only=True)
    try:
        objects = {
            row[0]
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'raw'"
            ).fetchall()
        }
        assert {"yellow_trips", "fhvhv_trips", "taxi_zones", "pipeline_metadata"} <= objects
        mode = con.execute("select data_mode from raw.pipeline_metadata").fetchone()[0]
        assert mode == "sample"
    finally:
        con.close()
