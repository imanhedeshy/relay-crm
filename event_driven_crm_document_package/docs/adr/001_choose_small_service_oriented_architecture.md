# ADR-001: Choose a small service-oriented architecture

## Status
Accepted

## Context
The challenge explicitly asks for multiple services instead of a monolith.

## Decision
Use:
- auth-service
- company-service
- crm-service
- workflow-service
- gateway
- web

## Consequences
Pros:
- clear ownership
- aligns with challenge
- easy to explain federation
Cons:
- more setup than a monolith
- requires Compose orchestration
