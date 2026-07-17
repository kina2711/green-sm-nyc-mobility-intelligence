"""Run the reproducible local analytics pipeline from source to dashboard JSON."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from green_sm_nyc.config import PROJECT_ROOT


def run_step(name: str, command: list[str]) -> dict[str, float | str]:
    """Run one visible pipeline step and stop immediately on failure."""
    print(f"\n[pipeline] {name}", flush=True)
    started = time.perf_counter()
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    return {"step": name, "seconds": round(time.perf_counter() - started, 2)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("sample", "local"), default="sample")
    parser.add_argument("--manifest", type=Path, help="Optional JSON run manifest path")
    args = parser.parse_args()

    python = sys.executable
    dbt = shutil.which("dbt")
    if not dbt:
        raise RuntimeError("dbt executable not found; run `uv sync --all-groups` first")

    results: list[dict[str, float | str]] = []
    if args.mode == "sample":
        results.append(
            run_step(
                "generate deterministic sample",
                [python, "-m", "green_sm_nyc.cli", "generate-sample"],
            )
        )
    results.append(
        run_step(
            "load raw DuckDB relations",
            [python, "-m", "green_sm_nyc.cli", "load-raw", "--mode", args.mode],
        )
    )
    dbt_command = [dbt, "build", "--project-dir", "dbt", "--profiles-dir", "dbt"]
    if args.mode == "local":
        dbt_command.extend(["--exclude", "tag:sample_only"])
    results.append(run_step("build and test dbt graph", dbt_command))
    results.append(
        run_step(
            "export dashboard contracts", [python, "-m", "green_sm_nyc.cli", "export-dashboard"]
        )
    )

    manifest = {"mode": args.mode, "status": "passed", "steps": results}
    if args.manifest:
        output = args.manifest if args.manifest.is_absolute() else PROJECT_ROOT / args.manifest
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n[pipeline] completed: {json.dumps(manifest)}", flush=True)


if __name__ == "__main__":
    main()
