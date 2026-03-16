# ADR-003: Use Kafka for one meaningful async workflow

## Status
Accepted

## Context
The challenge requires at least one asynchronous workflow using Kafka.

## Decision
Implement `LeadCreated` -> worker scoring/follow-up flow.

## Consequences
Pros:
- meaningful async behavior
- easy to demonstrate eventual consistency
- good discussion surface for retries/idempotency
Cons:
- only one async workflow in MVP
