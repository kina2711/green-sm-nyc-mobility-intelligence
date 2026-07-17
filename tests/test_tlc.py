from __future__ import annotations

import pytest

from green_sm_nyc.tlc import download_file, trip_url


def test_trip_url_uses_official_tlc_pattern() -> None:
    assert trip_url("yellow", 2024, 1).endswith("/yellow_tripdata_2024-01.parquet")
    assert trip_url("fhvhv", 2024, 12).endswith("/fhvhv_tripdata_2024-12.parquet")


def test_trip_url_rejects_unknown_service() -> None:
    with pytest.raises(ValueError, match="Unsupported service"):
        trip_url("green", 2024, 1)


def test_download_file_is_atomic_and_skips_existing(tmp_path) -> None:
    source = tmp_path / "source.bin"
    destination = tmp_path / "nested" / "destination.bin"
    source.write_bytes(b"official-source-shaped-test")

    assert download_file(source.as_uri(), destination, attempts=1) == "downloaded"
    assert destination.read_bytes() == source.read_bytes()
    assert not destination.with_suffix(".bin.part").exists()
    assert download_file(source.as_uri(), destination, attempts=1) == "skipped"
