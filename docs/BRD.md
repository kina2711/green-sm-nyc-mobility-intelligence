# Business Requirements Document

## Product

**Green SM NYC Mobility Intelligence** is a decision-support product for evaluating a hypothetical electric ride-hailing market entry in New York City.

The product is data-informed, not an automated dispatch or pricing system. It summarizes observed completed trips from NYC TLC data and helps strategy analysts prioritize questions for deeper market research.

## Target users

| User | Decision supported | Expected action |
|---|---|---|
| Market Strategy Analyst | Which services and boroughs are gaining completed-trip share? | Focus primary research on attractive segments. |
| City Operations Analyst | Which zones and time windows show persistent trip activity? | Propose candidate launch zones for operational validation. |
| Commercial Analyst | How do observed fare and trip economics vary by service? | Build pricing and unit-economics scenarios. |
| Executive Sponsor | Is the observed market large and concentrated enough to justify the next discovery phase? | Approve, reject, or narrow the market-entry study. |

## Business questions

1. How has completed-trip share changed by service and operator?
2. Which boroughs and taxi zones combine recent activity, growth, fare value, and airport relevance?
3. When does observed trip activity peak by zone, weekday, and hour?
4. How do fare per trip and fare per mile differ by service?
5. Which conclusions are supported by TLC data, and which require supply, request, cost, or customer research?

## KPI framework

### North Star decision metric

**Zone Opportunity Score**: a transparent prioritization heuristic used to rank zones for further research. It is not a prediction of profitability or unmet demand.

### Supporting KPIs

- Completed trips
- Completed-trip share
- Year-over-year completed-trip growth
- Average observed fare per completed trip
- Observed fare per paid mile
- Airport-trip share
- Peak activity hour
- Market concentration by operator using HHI

Definitions, grains, owners, and limitations are maintained in `docs/METRICS.md`.

## Functional requirements

- Load deterministic sample data in CI and support official TLC Parquet files locally.
- Transform data through dbt staging, intermediate, and marts layers.
- Publish a static HTML/CSS/JavaScript dashboard backed only by exported mart JSON.
- Filter the dashboard by year, borough, and service where relevant.
- Display data freshness, source, sample/full mode, and metric limitations.
- Validate primary grains, referential integrity, accepted values, and business invariants.
- Rebuild the project from a clean clone using documented commands.

## Non-functional requirements

- A sample pipeline must finish in under five minutes in GitHub Actions.
- Dashboard data must be generated, never manually copied into JavaScript.
- No credentials or raw production-scale data may be committed.
- Pipeline execution must be idempotent.
- Public documentation and code are written in English.
- All source-derived claims must be reproducible from marts.

## Out of scope

- Real-time vehicle dispatch
- Price elasticity or causal pricing claims
- Unmet-demand estimation from completed trips alone
- Driver acquisition ROI
- Production forecasting and automated fleet allocation
- Claims representing Green SM's official plans

## Success criteria

- All automated validation gates pass on deterministic sample data.
- Every dashboard KPI maps to one documented dbt mart field.
- A reviewer can identify the grain and business use of every mart.
- The dashboard clearly separates observed facts, heuristic scores, and unsupported questions.

