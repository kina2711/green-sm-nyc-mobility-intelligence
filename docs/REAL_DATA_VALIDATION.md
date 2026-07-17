# Real Data Validation: 2023–2025

## Scope

The local analytical release was built from official NYC TLC monthly files covering January 2023 through December 2025 inclusive.

| Source | Files | Raw rows |
|---|---:|---:|
| Yellow Taxi | 36 Parquet files | 128,202,548 |
| High Volume FHV | 36 Parquet files | 715,550,152 |
| Taxi zones | 1 CSV lookup | 265 |
| **Trips total** | **72 Parquet files** | **843,752,700** |

Raw Parquet size was approximately 18.36 GB. Files are retained locally under `data/raw/tlc/` and excluded from Git.

## Transformation result

- Analysis boundary: `2023-01-01 <= pickup_at < 2026-01-01`.
- Valid completed trips after source quality rules: **839,068,674**.
- Observed period: `2023-01-01 00:00:00` through `2025-12-31 23:59:59`.
- Active pickup zones represented in the opportunity mart: **263**.
- dbt local build: **61/61 selected nodes passed**, including 15 models and 46 full-data tests.
- Dashboard export: six JSON contracts totaling approximately 11.5 MB.

## Scale-aware quality strategy

The initial sample-oriented trip key used a partitioned `row_number()` and global uniqueness tests. At 843 million rows, that design created more than 24 GB of DuckDB spill and risked exhausting the local disk.

The release replaces that key with a portable stable hash of service, source basename, and Parquet row number. Eight trip-key uniqueness/non-null tests are tagged `sample_only`; deterministic CI continues to run them on every change. Local full-data mode excludes those redundant global sorts while retaining:

- source accepted-value and non-null checks;
- date, service, and taxi-zone relationship tests;
- fact/conformed row reconciliation;
- weighted-fare reconciliation;
- market-share totals;
- mart-grain uniqueness;
- opportunity-score bounds.

The full local build completed in approximately 25 minutes on the validation machine with a 2 GB DuckDB memory limit. Peak observed spill during aggregate construction was approximately 2.6 GB.

## Serving status

The dashboard metadata reports `LOCAL` mode and reads these real-data marts. GitHub CI uses deterministic fixtures for transformation tests, while GitHub Pages publishes the committed 11.5 MB aggregate real-data contracts. Raw TLC files and the DuckDB warehouse remain local.
