# ADR-0002: Serve the Dashboard as Static HTML, CSS, JavaScript, and JSON

**Status:** Accepted  
**Date:** 2026-07-17

## Context

The target portfolio roles include Data Analyst and Analytics Engineer. A static JavaScript experience makes the analytical product easy to publish and review without operating a backend service.

## Options considered

- Streamlit: fast, but requires a Python server and shifts attention away from front-end data storytelling.
- Superset: strong BI features, but operationally heavy for a portfolio.
- Static JavaScript: deploys cheaply, makes the data contract explicit, and supports a custom visual identity.

## Decision

Build a custom static site. Python exports aggregate dbt marts to versioned JSON; browser JavaScript renders filters and Chart.js visualizations.

## Consequences

- No backend or warehouse credentials are exposed.
- Data refresh requires rebuilding and redeploying static JSON.
- Row-level exploration and ad-hoc queries remain outside the dashboard.
