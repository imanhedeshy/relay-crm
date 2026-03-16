# ADR-004: Enforce authorization server-side

## Status
Accepted

## Context
The challenge explicitly requires server-side access control.

## Decision
All services validate role and company visibility before returning or mutating data.

## Consequences
Pros:
- secure by design
- aligns exactly with prompt
Cons:
- more plumbing in resolvers and service layer
