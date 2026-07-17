# Data Sources and Licensing

## Author

This project was designed and developed by **Kien Thai** as a personal Analytics Engineering and Data Analysis portfolio project.

## NYC TLC data

The analytical release uses public monthly trip records and the taxi-zone lookup published by the New York City Taxi and Limousine Commission.

- Yellow Taxi trip records
- High Volume For-Hire Vehicle trip records
- Taxi-zone lookup

Official source files are downloaded locally by the project CLI. The 72 Parquet files and local DuckDB warehouse are excluded from Git and are not redistributed with the source repository.

The committed files under `dashboard/data/` are aggregated analytical outputs used to serve the public dashboard. They contain no trip-level records.

Users who download official TLC data are responsible for reviewing and complying with the current source-provider terms.

## Software dependencies

Chart.js, dbt, DuckDB, uv, pytest, Ruff, and other dependencies remain subject to their respective licenses. Project source code is released under the repository's MIT License.
