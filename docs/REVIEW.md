# Release Candidate Review

## Summary

The project meets a solid middle-level Analytics Engineer / Data Analyst portfolio bar. It demonstrates end-to-end ownership from business requirements to a deployed analytical product, while keeping unsupported demand, supply, profitability, and optimization claims out of the descriptive data layer.

## Scorecard

| Area | Score | Evidence | Remaining gap |
|---|---:|---|---|
| Business framing | 4.5/5 | BRD, user decisions, KPI contracts, explicit out-of-scope statements | No stakeholder interviews or real decision outcome |
| SQL and dimensional modeling | 4.5/5 | Conformed trip fact, three dimensions, reusable intermediate layer, five marts | No incremental strategy at production scale |
| dbt engineering | 4.5/5 | Documented three-layer graph, generic and singular tests, reconciliation controls | No state-based slim CI or exposures |
| Python engineering | 4.0/5 | Typed modules, deterministic fixtures, idempotent loader, CLI, exporter contracts | Downloader has limited retry/telemetry behavior |
| Data quality | 4.5/5 | Source, grain, relationship, bounds, weighted-metric, and contract tests | No historical anomaly thresholds on real data |
| Dashboard and analysis | 4.5/5 | Responsive JavaScript product, filters, transparent scoring, methodology | Static JSON limits drill-through and large-data interaction |
| Orchestration and operations | 4.0/5 | One-command pipeline, clean rebuild, run manifest, runbook | Process orchestration only; no scheduler, alerts, or backfill UI |
| CI/CD and documentation | 4.5/5 | Locked environment, CI evidence, Pages deployment, ADRs, runbook, portfolio README | Pages release has no environment-specific promotion gate |

**Overall: 4.4/5 — credible middle-level portfolio release candidate.**

## Strongest signals for target roles

- Business language and SQL grain are connected: each mart has a defined question and action.
- Additive fare numerators and denominators prevent average-of-averages errors in browser filtering.
- Deterministic fixtures let CI validate the full transformation graph without publishing large data.
- The JavaScript dashboard consumes generated contracts instead of duplicating business logic.
- Limitations are part of the product interface, not hidden in a final README footnote.

## Skill gaps to discuss honestly

- **Production warehouse scale**: DuckDB proves the model but not BigQuery/Snowflake cost, partition, clustering, or concurrency decisions.
- **Incremental and late-arriving data**: the core graph rebuilds small local tables and does not implement merge/backfill patterns.
- **Operational observability**: run manifests exist, but there is no alert routing, SLA monitor, or centralized lineage service.
- **Causal and predictive analysis**: the release is descriptive; it does not claim that activity causes market attractiveness.
- **Fleet optimization inputs**: completed trips alone cannot measure vehicle availability, idle time, charging constraints, or rejected requests.

## Recommended extensions

1. **Real-data analytical release** — load 12–24 months of official TLC partitions, add source freshness/anomaly tests, and publish a clearly dated market brief.
2. **Forecasting workbench** — add zone/hour baselines, rolling-origin backtests, weather/calendar features, and error analysis without feeding predictions into the descriptive score.
3. **Fleet scenario layer** — only after acquiring supply and charging assumptions, build explicit scenario inputs and constraints; keep it labeled as simulation rather than observed fact.

## Release decision

Ready for portfolio use after the final clean-room validation passes. The next investment should improve analytical evidence with official data before adding platform complexity.
