# ADR-0001: Use DuckDB and dbt for the Portfolio Warehouse

**Status:** Accepted  
**Date:** 2026-07-17

## Context

The project must demonstrate Analytics Engineering and Data Analysis skills, run on a laptop, and remain reproducible in free CI.

## Options considered

- BigQuery with dbt: realistic cloud platform, but requires credentials and introduces cost.
- PostgreSQL with dbt: familiar, but slower to set up and less convenient for public Parquet analytics.
- DuckDB with dbt: embedded, fast for analytical files, zero service setup, and CI-friendly.

## Decision

Use DuckDB with dbt-duckdb. Keep SQL and dashboard contracts portable for a later cloud migration.

## Consequences

- Excellent local reproducibility and low cost.
- Limited concurrency and production operations compared with a managed warehouse.
- Full-scale performance claims must be benchmarked separately from sample CI.

