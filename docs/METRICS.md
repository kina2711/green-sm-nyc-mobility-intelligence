# Metric Contracts

Metric owner: Analytics Engineering. Business approver: Market Strategy.

| Metric | Definition | Grain / dimensions | Action | Limitation |
|---|---|---|---|---|
| Completed trips | Count of valid completed trip records | Date, service, operator, borough, zone | Size observed market segments | Excludes rejected/cancelled requests and unreported trips |
| Completed-trip share | Segment completed trips / all completed trips in the same period and geography | Month, borough, operator | Track observed competitive mix | Not customer or revenue market share |
| YoY trip growth | `(current trips - prior-year trips) / prior-year trips` | Zone, year | Identify zones for deeper research | Sensitive to shocks and source coverage changes |
| Average observed fare | `sum(fare_amount) / count(valid fare trips)` | Month, service | Compare observed fare positioning | Not contribution margin; excludes missing fares |
| Fare per paid mile | `sum(fare_amount) / sum(trip_miles)` for positive miles | Month, service | Compare distance-normalized pricing | Paid trip miles are not total vehicle miles |
| Airport-trip share | Trips touching JFK, LaGuardia, or Newark zone IDs / zone trips | Zone, year | Surface airport-oriented zones | Newark mapping follows TLC zone conventions |
| HHI | Sum of squared operator shares multiplied by 10,000 | Year | Track concentration | Based on completed trips only |
| Zone Opportunity Score | Weighted percentile heuristic documented in `DATA_MODEL.md` | Latest year, zone | Rank zones for primary research | Not profitability, unmet demand, or an optimization result |

## Change policy

Any formula or weight change requires:

1. An ADR or decision-log entry.
2. Updated dbt documentation and tests.
3. Updated dashboard methodology text.
4. A comparison of old and new results before merge.

