# ADR 0001: Keep the MVP split into narrow subgraphs

## Status
Accepted

## Decision
Use four narrow Python services plus an Apollo gateway instead of collapsing everything into one Django app.

## Consequences
- The repository demonstrates clear ownership boundaries and real federation.
- Authorization requires a small amount of service-to-service coordination.
- The system stays explainable because each service has a small schema and small model surface.
