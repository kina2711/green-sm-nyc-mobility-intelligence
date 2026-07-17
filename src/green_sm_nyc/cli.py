"""Command-line interface for local project workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from green_sm_nyc.dashboard_export import export_dashboard
from green_sm_nyc.sample_data import generate_sample
from green_sm_nyc.tlc import download_month, download_zone_lookup
from green_sm_nyc.warehouse import load_raw


def _month(value: str) -> tuple[int, int]:
    try:
        year, month = (int(part) for part in value.split("-"))
    except ValueError as error:
        raise argparse.ArgumentTypeError("Expected YYYY-MM") from error
    if not 1 <= month <= 12:
        raise argparse.ArgumentTypeError("Month must be between 01 and 12")
    return year, month


def _month_range(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    months: list[tuple[int, int]] = []
    year, month = start
    while (year, month) <= end:
        months.append((year, month))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    sample_parser = subparsers.add_parser("generate-sample")
    sample_parser.add_argument("--output-dir", type=Path)

    load_parser = subparsers.add_parser("load-raw")
    load_parser.add_argument("--mode", choices=("sample", "local"), default="sample")

    export_parser = subparsers.add_parser("export-dashboard")
    export_parser.add_argument("--output-dir", type=Path)

    download_parser = subparsers.add_parser("download")
    download_parser.add_argument("--start", type=_month, required=True)
    download_parser.add_argument("--end", type=_month, required=True)
    download_parser.add_argument(
        "--services", nargs="+", choices=("yellow", "fhvhv"), default=["yellow", "fhvhv"]
    )

    args = parser.parse_args(argv)
    if args.command == "generate-sample":
        result = generate_sample(args.output_dir) if args.output_dir else generate_sample()
    elif args.command == "load-raw":
        result = load_raw(mode=args.mode)
    elif args.command == "export-dashboard":
        result = (
            export_dashboard(output_dir=args.output_dir) if args.output_dir else export_dashboard()
        )
    else:
        if args.end < args.start:
            parser.error("--end must be on or after --start")
        result = {"zone_lookup": download_zone_lookup()}
        for service in args.services:
            for year, month in _month_range(args.start, args.end):
                result[f"{service}_{year:04d}_{month:02d}"] = download_month(service, year, month)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
