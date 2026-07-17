from __future__ import annotations

from pathlib import Path

import duckdb

from green_sm_nyc.sample_data import generate_sample
from green_sm_nyc.warehouse import load_raw


def test_loader_replaces_existing_views_with_sample_tables(tmp_path: Path) -> None:
    sample_dir = tmp_path / "sample"
    warehouse_path = tmp_path / "warehouse" / "test.duckdb"
    generate_sample(sample_dir)

    warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(warehouse_path))
    con.execute("create schema raw")
    con.execute("create view raw.yellow_trips as select 1 as placeholder")
    con.execute("create view raw.fhvhv_trips as select 1 as placeholder")
    con.execute("create view raw.taxi_zones as select 1 as placeholder")
    con.close()

    counts = load_raw(warehouse_path=warehouse_path, sample_dir=sample_dir)
    assert counts["yellow_trips"] > 1_000
