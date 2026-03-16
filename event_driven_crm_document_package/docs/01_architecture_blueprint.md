# Architecture Blueprint

## High-level architecture

This project should be implemented as a small monorepo with:
- React frontend
- Apollo GraphQL gateway
- 3 Django-based domain services
- 1 Python async worker service
- Kafka for event streaming
- PostgreSQL per service
- Docker Compose for full end-to-end local runtime
- Nx for workspace orchestration and structure

## Service boundaries

### 1. `auth-service`
Owns:
- users
- roles
- memberships
- user-to-company relationships
- authorization metadata

### 2. `company-service`
Owns:
- companies
- parent/child hierarchy
- visibility lineage
- hierarchy traversal

### 3. `crm-service`
Owns:
- leads
- contacts
- deals
- activities
- CRM mutations
- event publication

### 4. `workflow-service`
Owns:
- Kafka consumers
- retries
- idempotency
- dead-letter / failure routing
- background processing
- async side effects

### 5. `gateway`
Owns:
- federated GraphQL entrypoint
- auth context injection
- service composition
- gateway-level instrumentation and request tracing

### 6. `web`
Owns:
- user-facing UI
- Apollo Client
- loading/error states
- async status display
- role-aware UX

## Core async workflow

Recommended workflow:
1. User creates a lead
2. `crm-service` writes the lead with `scoringStatus = PENDING`
3. `crm-service` publishes `LeadCreated`
4. `workflow-service` consumes `LeadCreated`
5. Worker performs lightweight enrichment/scoring/follow-up generation
6. Worker updates the lead and creates a follow-up activity
7. UI refetches or polls and shows eventual consistency

## Architectural principles

- Explicit bounded contexts
- Backend-enforced authorization
- Event-driven side effects
- Deterministic local development
- Minimal but real observability
- Clean contracts between services
- Prefer boring, explainable technology over flashy complexity
