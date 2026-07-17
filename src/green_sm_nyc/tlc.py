"""Small, resumable downloader for official NYC TLC public files."""

from __future__ import annotations

import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

from green_sm_nyc.config import RAW_DIR, SUPPORTED_SERVICES

TLC_BASE_URL = "https://d37ci6vzurychx.cloudfront.net"
USER_AGENT = {"User-Agent": "green-sm-nyc-mobility-intelligence/0.1"}


def trip_url(service: str, year: int, month: int) -> str:
    if service not in SUPPORTED_SERVICES:
        raise ValueError(f"Unsupported service: {service}")
    return f"{TLC_BASE_URL}/trip-data/{service}_tripdata_{year:04d}-{month:02d}.parquet"


def download_file(
    url: str,
    destination: Path,
    overwrite: bool = False,
    attempts: int = 5,
    timeout: int = 180,
    backoff_seconds: float = 2,
) -> str:
    """Download atomically with retry and byte-range resume."""
    if destination.exists() and destination.stat().st_size > 0 and not overwrite:
        return "skipped"
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    if overwrite:
        partial.unlink(missing_ok=True)

    for attempt in range(1, attempts + 1):
        offset = partial.stat().st_size if partial.exists() else 0
        headers = {**USER_AGENT, **({"Range": f"bytes={offset}-"} if offset else {})}
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                is_partial_response = getattr(response, "status", None) == 206
                mode = "ab" if offset and is_partial_response else "wb"
                with partial.open(mode) as handle:
                    shutil.copyfileobj(response, handle, length=1024 * 1024)
            partial.replace(destination)
            return "downloaded"
        except urllib.error.HTTPError as error:
            if error.code == 404:
                partial.unlink(missing_ok=True)
                return "missing"
            if 400 <= error.code < 500 and error.code != 408:
                raise
            last_error: Exception = error
        except (TimeoutError, urllib.error.URLError, OSError) as error:
            last_error = error

        if attempt < attempts:
            time.sleep(backoff_seconds * attempt)

    raise RuntimeError(f"Download failed after {attempts} attempts: {url}") from last_error


def download_month(service: str, year: int, month: int, raw_dir: Path = RAW_DIR) -> str:
    destination = raw_dir / service / f"{service}_tripdata_{year:04d}-{month:02d}.parquet"
    return download_file(trip_url(service, year, month), destination)


def download_zone_lookup(raw_dir: Path = RAW_DIR) -> str:
    return download_file(
        f"{TLC_BASE_URL}/misc/taxi_zone_lookup.csv", raw_dir / "taxi_zone_lookup.csv"
    )
