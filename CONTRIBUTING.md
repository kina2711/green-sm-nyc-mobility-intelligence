# Contributing

## Working agreement

- Keep public code and documentation in English.
- Preserve the distinction between completed-trip activity and unobserved demand or supply.
- Define the grain and business question before adding a mart or dashboard metric.
- Do not commit raw TLC files, DuckDB databases, generated JSON, or credentials.
- Add tests at the lowest useful layer and update metric/model documentation with behavior changes.

## Development workflow

1. Create a focused branch.
2. Run `uv sync --frozen --all-groups`.
3. Implement the smallest coherent change.
4. Run `uv run python scripts/run_pipeline.py --mode sample`.
5. Run `uv run pytest`, Ruff checks, and `node --check dashboard/app.js`.
6. Explain business impact, metric changes, and validation evidence in the pull request.

Changes to scoring weights, source meaning, model grain, or serving contracts require an ADR or an update to an existing ADR. Contract-breaking dashboard changes require a schema-version increment.
