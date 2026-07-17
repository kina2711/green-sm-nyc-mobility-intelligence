from __future__ import annotations

import hashlib
from pathlib import Path

from green_sm_nyc.sample_data import generate_sample


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_sample_generation_is_deterministic(tmp_path: Path) -> None:
    first = generate_sample(tmp_path)
    first_hashes = {path.name: _hash(path) for path in tmp_path.glob("*.csv")}
    second = generate_sample(tmp_path)
    second_hashes = {path.name: _hash(path) for path in tmp_path.glob("*.csv")}

    assert first == second
    assert first_hashes == second_hashes
    assert first["yellow_trips"] > 1_000
    assert first["fhvhv_trips"] > first["yellow_trips"]
    assert first["zones"] == 8
