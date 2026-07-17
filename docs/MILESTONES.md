# Implementation Milestones

## Milestone 0 — Discovery and architecture

- BRD, KPI contracts, data model, architecture, and ADRs
- Validation: documentation links, explicit grains, scope, and limitations review

## Milestone 1 — Reproducible foundation

- Python project, deterministic sample generator, and raw DuckDB loader
- Unit tests for generation, loading, and idempotency
- Validation: Ruff, pytest, and repeat-load row-count equality

## Milestone 2 — Analytics engineering

- dbt staging, intermediate, dimensions, facts, and marts
- Generic, singular, relationship, and reconciliation tests
- Validation: `dbt build` on sample data and mart contract checks

## Milestone 3 — JavaScript dashboard

- Custom responsive HTML/CSS/JavaScript experience
- JSON generated from marts, filters, charts, freshness, and methodology
- Validation: JSON contract tests, static asset tests, and JavaScript syntax check

## Milestone 4 — CI/CD and documentation

- GitHub Actions CI and GitHub Pages deployment
- Runbook, contribution guide, portfolio README, and license
- Validation: clean local pipeline plus workflow syntax inspection

## Milestone 5 — Review and release candidate

- Architecture, SQL, Python, dbt, dashboard, and documentation review
- Refactor all blocking and high-priority findings
- Validation: full quality command and final scorecard
