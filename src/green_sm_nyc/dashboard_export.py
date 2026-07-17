"""Export compact, versioned dashboard datasets from dbt marts."""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import duckdb

from green_sm_nyc.config import PROJECT_ROOT, WAREHOUSE_PATH

SCHEMA_VERSION = "1.0.0"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "dashboard" / "data"


def _rows(connection: duckdb.DuckDBPyConnection, query: str) -> list[dict[str, Any]]:
    cursor = connection.execute(query)
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def _json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "row_count": len(rows),
        "data": [{key: _json_value(value) for key, value in row.items()} for row in rows],
    }


def build_dashboard_payloads(connection: duckdb.DuckDBPyConnection) -> dict[str, dict[str, Any]]:
    """Build dashboard-facing contracts strictly from marts and pipeline metadata."""
    queries = {
        "summary": """
            select
                count(*) as completed_trips,
                count(distinct operator) as observed_operators,
                count(distinct pickup_zone_id) as active_pickup_zones,
                round(avg(fare_amount), 2) as avg_observed_fare,
                min(pickup_at) as period_start,
                max(pickup_at) as period_end
            from marts.fct_trips
        """,
        "market": """
            select pickup_month, borough, operator, service_category, completed_trips,
                   observed_fare, fare_trip_count, paid_miles, avg_observed_fare,
                   fare_per_paid_mile, completed_trip_share
            from marts.mart_market_overview
            order by pickup_month, borough, operator
        """,
        "zones": """
            select zone_id, borough, zone_name, analysis_year, completed_trips,
                   prior_year_completed_trips, yoy_completed_trip_growth,
                   avg_observed_fare, airport_trip_share, activity_component,
                   growth_component, fare_component, airport_component,
                   opportunity_score
            from marts.mart_zone_opportunity
            order by opportunity_score desc, zone_name
        """,
        "fares": """
            select pickup_month, operator, service_category, completed_trips,
                   observed_fare, fare_trip_count, paid_miles, avg_observed_fare,
                   fare_per_paid_mile, avg_observed_total
            from marts.mart_fare_positioning
            order by pickup_month, operator
        """,
        "hourly": """
            select zone_id, day_of_week, pickup_hour, completed_trips,
                   observed_days, avg_completed_trips_per_observed_day,
                   avg_observed_fare
            from marts.mart_hourly_demand
            order by zone_id, day_of_week, pickup_hour
        """,
        "metadata": """
            select data_mode as source_mode, loaded_at_utc as loaded_at,
                   source_file_count,
                   (select count(*) from raw.yellow_trips)
                     + (select count(*) from raw.fhvhv_trips) as row_count
            from raw.pipeline_metadata
        """,
    }
    return {name: _payload(_rows(connection, query)) for name, query in queries.items()}


def validate_dashboard_payloads(payloads: dict[str, dict[str, Any]]) -> None:
    """Fail fast when a dashboard contract is missing or outside expected bounds."""
    required = {"summary", "market", "zones", "fares", "hourly", "metadata"}
    missing = required - payloads.keys()
    if missing:
        raise ValueError(f"Missing dashboard datasets: {sorted(missing)}")
    empty = [name for name in required if not payloads[name]["data"]]
    if empty:
        raise ValueError(f"Empty dashboard datasets: {sorted(empty)}")
    if any(not 0 <= row["opportunity_score"] <= 100 for row in payloads["zones"]["data"]):
        raise ValueError("Zone opportunity scores must be between 0 and 100")
    if any(not 0 <= row["completed_trip_share"] <= 1 for row in payloads["market"]["data"]):
        raise ValueError("Market shares must be between 0 and 1")


def export_dashboard(
    warehouse_path: Path = WAREHOUSE_PATH, output_dir: Path = DEFAULT_OUTPUT_DIR
) -> dict[str, Any]:
    """Write deterministic JSON files and return a compact export manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(warehouse_path), read_only=True) as connection:
        payloads = build_dashboard_payloads(connection)
    validate_dashboard_payloads(payloads)
    for name, payload in payloads.items():
        path = output_dir / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "schema_version": SCHEMA_VERSION,
        "output_dir": str(output_dir),
        "datasets": {name: payload["row_count"] for name, payload in payloads.items()},
    }
