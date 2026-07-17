# Runbook

## Purpose

This runbook covers repeatable local builds, optional official NYC TLC inputs, dashboard serving, common failures, and validation evidence.

## Sample-mode build

From the repository root:

```bash
uv sync --frozen --all-groups
uv run python scripts/run_pipeline.py --mode sample --manifest artifacts/pipeline.json
uv run pytest
uv run ruff check .
uv run ruff format --check .
node --check dashboard/app.js
```

Expected evidence:

- `data/warehouse/mobility.duckdb` contains `raw`, `staging`, `intermediate`, and `marts` schemas;
- `dbt/target/run_results.json` reports all dbt nodes passed;
- `dashboard/data/` contains six JSON contracts;
- `artifacts/pipeline.json` records step durations when `--manifest` is supplied.

## Official TLC local mode

Download selected months with the project CLI:

```bash
uv run mobility-intel download --start 2024-01 --end 2024-03 --services yellow fhvhv
uv run python scripts/run_pipeline.py --mode local
```

The loader expects Yellow Taxi and High Volume FHV Parquet files under `data/raw/tlc/<service>/` and the taxi-zone lookup at `data/raw/tlc/taxi_zone_lookup.csv`. Downloads and warehouses are ignored by Git. Start with a small date range because official files can be large.

The verified full local release uses:

```bash
uv run mobility-intel download --start 2023-01 --end 2025-12 --services yellow fhvhv
uv run python scripts/run_pipeline.py --mode local --manifest artifacts/real-2023-2025.json
```

This downloads approximately 18.36 GB across 72 monthly Parquet files. The downloader writes `.part` files atomically and retries with HTTP byte-range resume. Keep at least 25 GB free beyond the raw files for temporary analytical work. Local mode excludes only trip-key tests tagged `sample_only`; all aggregate-grain and business-invariant tests remain active.

## Serve the dashboard

```bash
python -m http.server 8000 -d dashboard
```

Open `http://localhost:8000`. Confirm the source-mode badge, period, charts, filters, zone table, heatmap, and methodology notice. The dashboard uses Chart.js from a CDN, so charts require network access unless that dependency is vendored later.

## Clean rebuild

```bash
uv run python scripts/clean.py
uv run python scripts/run_pipeline.py --mode sample
```

The clean command removes the local warehouse and dbt artifact directories. It preserves source code, raw TLC files, and the committed aggregate dashboard snapshot. Re-export dashboard contracts after rebuilding real marts and before committing a refreshed public snapshot.

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| Dashboard says it cannot load JSON | HTML opened with `file://`, or export not run | Run the pipeline and serve `dashboard/` over HTTP. |
| dbt cannot find a source | Raw loading was skipped | Run `mobility-intel load-raw --mode sample` or the complete pipeline. |
| Local mode reports no Parquet files | Expected TLC directory is empty | Run the download command or place files in the documented paths. |
| Dashboard contract test cannot open DuckDB | Tests ran before the build on a clean clone | Run the pipeline first; CI enforces this order. |
| Chart panels remain empty | CDN is unavailable or JavaScript failed | Check browser console, network access, and `node --check dashboard/app.js`. |

## Recovery and rollback

All generated state is reproducible. Run `scripts/clean.py` and rebuild when necessary. GitHub Pages deploys the committed aggregate contracts under `dashboard/data/`; a failed validation cannot advance the deployment job. To restore a previous public dashboard, redeploy a known-good commit through the Pages workflow.
