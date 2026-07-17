"""Remove generated local artifacts while preserving source and fixtures."""

from __future__ import annotations

import shutil

from green_sm_nyc.config import PROJECT_ROOT, WAREHOUSE_DIR


def main() -> None:
    shutil.rmtree(WAREHOUSE_DIR, ignore_errors=True)
    for relative in ("dbt/target", "dbt/logs", "dbt/dbt_packages"):
        shutil.rmtree(PROJECT_ROOT / relative, ignore_errors=True)


if __name__ == "__main__":
    main()
