# Scalability, Reliability, and Operability Roadmap

## Already Implemented Baseline
- health checks for Kafka, databases, Django services, and gateway
- persistent workflow idempotency state in Postgres
- DLQ topic for failed lead workflows
- structured logging in the workflow path
- restart behavior for Kafka, gateway, and workflow worker
- startup ordering that waits for healthy dependencies

## Near-Term Improvements
- add Kafka lag visibility and alerts
- add request correlation IDs across gateway and subgraphs
- add cursor-based pagination for larger CRM datasets
- define gateway timeout budgets and upstream failure policy

## Medium-Term Improvements
- introduce tracing across gateway and services
- scale workers horizontally and tune Kafka partitioning strategy
- optimize N+1 risk in federated and service-local queries
- add persisted queries or targeted gateway caching

## Longer-Term Improvements
- event version registry and schema-governance process
- domain event history / replay strategy
- reporting or analytics service split
- hierarchy lookup caching
- production authentication provider and secret management platform
