# ADR-0003: Treat TLC Trips as Observed Completed Trips, Not Supply or Unmet Demand

**Status:** Accepted  
**Date:** 2026-07-17

## Context

NYC TLC trip records describe completed trips. They do not provide a complete inventory of available vehicles, rejected requests, or customer abandonment.

## Decision

Name demand measures as completed-trip activity. Do not calculate a demand-supply gap or price elasticity from TLC completed trips alone. Use a transparent zone ranking heuristic only for prioritizing further research.

## Consequences

- Claims are narrower but defensible.
- Fleet optimization and causal pricing remain roadmap items requiring additional data.

