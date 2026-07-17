"""Generate deterministic, source-shaped fixtures for CI and local demos.

The generated rows are synthetic. They mirror a small subset of NYC TLC column
names but do not reproduce records from the reference repository or real riders.
"""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from green_sm_nyc.config import SAMPLE_DIR

ZONES = [
    (1, "EWR", "Newark Airport", "Airports", True, 0.55),
    (48, "Manhattan", "Clinton East", "Yellow Zone", False, 1.05),
    (79, "Manhattan", "East Village", "Yellow Zone", False, 1.12),
    (132, "Queens", "JFK Airport", "Airports", True, 1.18),
    (138, "Queens", "LaGuardia Airport", "Airports", True, 1.10),
    (161, "Manhattan", "Midtown Center", "Yellow Zone", False, 0.98),
    (181, "Brooklyn", "Park Slope", "Boro Zone", False, 1.25),
    (255, "Brooklyn", "Williamsburg North", "Boro Zone", False, 1.32),
]

YELLOW_FIELDS = [
    "VendorID",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "fare_amount",
    "tip_amount",
    "tolls_amount",
    "total_amount",
]

FHVHV_FIELDS = [
    "hvfhs_license_num",
    "pickup_datetime",
    "dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "trip_miles",
    "base_passenger_fare",
    "tolls",
    "sales_tax",
    "congestion_surcharge",
    "airport_fee",
    "tips",
    "driver_pay",
]


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _trip_time(rng: random.Random, year: int, month: int, trip_number: int) -> datetime:
    day = 1 + (trip_number * 7 + rng.randint(0, 5)) % 27
    hour_weights = [1, 1, 1, 1, 1, 2, 3, 4, 4, 3, 2, 2, 2, 2, 2, 3, 4, 5, 5, 4, 3, 2, 2, 1]
    hour = rng.choices(range(24), weights=hour_weights, k=1)[0]
    return datetime(year, month, day, hour, rng.randint(0, 59), rng.randint(0, 59))


def generate_sample(output_dir: Path = SAMPLE_DIR, seed: int = 20260717) -> dict[str, int]:
    """Create stable two-year Yellow and FHVHV fixtures and a zone dimension."""
    rng = random.Random(seed)
    yellow_rows: list[dict[str, object]] = []
    fhvhv_rows: list[dict[str, object]] = []

    for year in (2023, 2024):
        for month in range(1, 13):
            for zone_id, _borough, _zone, _service_zone, is_airport, growth in ZONES:
                year_factor = 1.0 if year == 2023 else growth
                seasonal = 1 + 0.12 * (month in (3, 10, 12)) - 0.08 * (month in (1, 2))
                base = 8 + (zone_id % 7)

                yellow_count = max(2, round(base * seasonal * (1.03 if year == 2023 else 0.93)))
                fhvhv_count = max(3, round((base + 5) * seasonal * year_factor))

                for index in range(yellow_count):
                    pickup = _trip_time(rng, year, month, index)
                    miles = round(rng.uniform(1.1, 8.5) + (4 if is_airport else 0), 2)
                    minutes = max(5, round(miles / rng.uniform(9, 24) * 60))
                    fare = round(3.0 + miles * rng.uniform(2.7, 3.4), 2)
                    tip = round(fare * (0.18 if index % 3 else 0), 2)
                    tolls = 6.94 if is_airport and index % 2 == 0 else 0.0
                    yellow_rows.append(
                        {
                            "VendorID": 1 + index % 2,
                            "tpep_pickup_datetime": pickup.isoformat(sep=" "),
                            "tpep_dropoff_datetime": (
                                pickup + timedelta(minutes=minutes)
                            ).isoformat(sep=" "),
                            "passenger_count": 1 + index % 3,
                            "trip_distance": miles,
                            "PULocationID": zone_id,
                            "DOLocationID": rng.choice(ZONES)[0],
                            "payment_type": 1 if index % 4 else 2,
                            "fare_amount": fare,
                            "tip_amount": tip,
                            "tolls_amount": tolls,
                            "total_amount": round(fare + tip + tolls + 2.5, 2),
                        }
                    )

                for index in range(fhvhv_count):
                    pickup = _trip_time(rng, year, month, index + 31)
                    miles = round(rng.uniform(1.0, 10.0) + (5 if is_airport else 0), 2)
                    minutes = max(5, round(miles / rng.uniform(8, 22) * 60))
                    fare = round(2.5 + miles * rng.uniform(2.2, 3.1), 2)
                    tips = round(fare * (0.08 if index % 5 == 0 else 0), 2)
                    fhvhv_rows.append(
                        {
                            "hvfhs_license_num": "HV0003" if index % 3 else "HV0005",
                            "pickup_datetime": pickup.isoformat(sep=" "),
                            "dropoff_datetime": (pickup + timedelta(minutes=minutes)).isoformat(
                                sep=" "
                            ),
                            "PULocationID": zone_id,
                            "DOLocationID": rng.choice(ZONES)[0],
                            "trip_miles": miles,
                            "base_passenger_fare": fare,
                            "tolls": 6.94 if is_airport and index % 2 == 0 else 0.0,
                            "sales_tax": round(fare * 0.08875, 2),
                            "congestion_surcharge": 2.75 if zone_id in (48, 79, 161) else 0.0,
                            "airport_fee": 2.5 if is_airport else 0.0,
                            "tips": tips,
                            "driver_pay": round(fare * 0.72, 2),
                        }
                    )

    zone_rows = [
        {
            "LocationID": zone_id,
            "Borough": borough,
            "Zone": zone,
            "service_zone": service_zone,
            "is_airport": str(is_airport).lower(),
        }
        for zone_id, borough, zone, service_zone, is_airport, _growth in ZONES
    ]

    _write_csv(output_dir / "yellow_trips.csv", YELLOW_FIELDS, yellow_rows)
    _write_csv(output_dir / "fhvhv_trips.csv", FHVHV_FIELDS, fhvhv_rows)
    _write_csv(
        output_dir / "taxi_zones.csv",
        ["LocationID", "Borough", "Zone", "service_zone", "is_airport"],
        zone_rows,
    )
    return {
        "yellow_trips": len(yellow_rows),
        "fhvhv_trips": len(fhvhv_rows),
        "zones": len(zone_rows),
    }
