# Data directories

```text
data/
├── raw/tlc/       Official local TLC Parquet and zone lookup files (ignored)
├── sample/        Generated deterministic CI fixtures (ignored except .gitkeep)
└── warehouse/     Generated DuckDB database and temporary spill files (ignored)
```

The sample CSV files are not source assets. `mobility-intel generate-sample` recreates them before sample-mode builds. Official TLC files and local warehouses must never be committed.
