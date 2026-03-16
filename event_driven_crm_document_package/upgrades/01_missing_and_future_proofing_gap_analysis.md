# Missing or Optional Improvements Beyond the Challenge

This file now distinguishes between gaps already closed in the current repository and the upgrades that still remain optional future work.

## Already Covered in the Current Repo
- server-side authorization for CRM reads and writes
- gateway-only frontend communication
- dead-letter queue implementation for failed lead workflows
- bounded retries with exponential backoff
- worker restart resilience and broker-startup recovery
- health checks across Kafka, databases, services, and gateway
- structured workflow logs
- keyboard-accessible form controls, labels, focus states, and clear loading/error messaging
- read-only UI behavior for roles without write access

## Security / Auth Upgrades Still Worth Doing
- real authentication provider or JWT validation
- signed internal service-to-service auth context instead of a demo `x-user-id`
- CSRF and CORS hardening for non-demo deployment
- request rate limiting and abuse prevention
- secret management outside local `.env` files

## Privacy / Compliance Upgrades
- data retention policy and deletion workflows
- audit trail for access and mutation history
- documented PII classification and minimization policy
- export/delete workflows for CRM records
- encryption and key-management policy documentation

## Reliability / Operability Upgrades
- retry jitter to avoid synchronized retries under broader load
- queue lag monitoring and alerting
- request correlation IDs across gateway and services
- explicit gateway timeout and retry budgets
- graceful degradation rules for partial service outages

## Scalability Upgrades
- horizontal worker scaling with partition-aware planning
- pagination for larger lead, deal, and activity result sets
- query optimization / N+1 analysis
- connection pooling and production database tuning
- gateway persisted queries or response caching

## Accessibility / Internationalization Upgrades
- screen-reader QA with VoiceOver or NVDA
- extraction of user-facing strings into a translation layer
- locale-aware timestamp selection instead of fixed `en-US`
- timezone selection for non-demo users
