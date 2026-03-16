# RelayCRM

## 1. Project Overview

I built RelayCRM as a deliberately scoped event-driven CRM for the take-home challenge in [`event_driven_crm_document_package/`](./event_driven_crm_document_package).

The MVP focuses on:

- customer-related CRM data through leads, deals, and activities
- multi-company hierarchy with one parent and multiple child companies
- role-based access control enforced server-side
- one real asynchronous workflow: lead creation triggers Kafka-based scoring and follow-up generation

I split the system into narrow services so the ownership model is easy to review in an interview:

- `auth-service` owns users, memberships, and roles
- `company-service` owns companies and hierarchy traversal
- `crm-service` owns leads, deals, activities, and event publication
- `workflow-service` owns Kafka consumption, idempotency, retries, and background processing
- `gateway` is the only GraphQL endpoint used by the browser
- `web` is a React + Apollo client that makes eventual consistency visible

## 2. Tech Stack

- React 19
- Apollo Client
- Apollo Gateway
- Python 3.12 / Django 5
- Ariadne
- Kafka
- PostgreSQL
- Docker Compose
- Nx workspace structure

## 3. Architecture Summary

### Service responsibilities

- `apps/web`
  - seed-user selector
  - visible company selector
  - lead creation UI
  - read-only viewer state for non-writing roles
  - polling-based async status updates
  - full-page reload on user switch so each role gets a clean auth context
- `apps/gateway`
  - federated GraphQL entrypoint
  - forwards `x-user-id` auth context to subgraphs
  - returns sanitized GraphQL errors without stack traces
  - retries startup until subgraphs are reachable
- `services/auth-service`
  - source of truth for users and memberships
  - exposes `viewer`, `users`, and `accessContext`
- `services/company-service`
  - source of truth for companies
  - computes visible companies from memberships and hierarchy
- `services/crm-service`
  - enforces lead/deal/activity access rules
  - stores new leads with `scoringStatus=PENDING`
  - publishes `crm.lead.created`
- `services/workflow-service`
  - consumes `crm.lead.created`
  - tracks processed events by `eventId`
  - retries CRM callback mutations
  - writes failure state and supports DLQ routing

### Parent / child visibility

- CRM records belong to child companies.
- `PARENT_ADMIN` can read across descendant child companies.
- `CHILD_MANAGER`, `SALES_REP`, and `VIEWER` are isolated to their own child company.
- Authorization is checked in backend permission helpers, not in the UI alone.

### Async workflow

1. A user creates a lead from the web app.
2. `crm-service` validates access and stores the lead with `scoringStatus=PENDING`.
3. `crm-service` publishes `crm.lead.created` to Kafka.
4. `workflow-service` consumes the event and records processing state keyed by `eventId`.
5. The worker calculates a deterministic score and follow-up note.
6. The worker calls an internal CRM GraphQL mutation protected by `x-internal-token`.
7. `crm-service` updates the lead to `COMPLETED` or `FAILED` and upserts the follow-up activity by `workflow_event_id`.
8. The web app polls through the gateway and shows the transition from pending to completed.

See:

- [Architecture Notes](./libs/docs/architecture.md)
- [Access Control Notes](./libs/docs/access-control.md)
- [Async Workflow Notes](./libs/docs/async-workflow.md)
- [ADR 0001](./libs/docs/adrs/0001-service-split.md)

## 4. How to Run

```bash
cp .env.example .env
docker compose up --build
```

The compose setup intentionally exposes only the app/service ports needed for review. Database and Kafka ports stay internal to avoid host-port collisions.

## 5. Service URLs

- Web: `http://localhost:3000`
- Gateway GraphQL: `http://localhost:4000/graphql`
- Gateway health: `http://localhost:4000/health`
- Auth service GraphQL: `http://localhost:8001/graphql/`
- Company service GraphQL: `http://localhost:8002/graphql/`
- CRM service GraphQL: `http://localhost:8003/graphql/`
- Workflow service GraphQL: `http://localhost:8004/graphql/`

## 6. Seed Credentials / Demo Data

The app uses a seed-user selector instead of a full auth flow. This keeps the challenge focused on authorization boundaries and eventual consistency.

### Seed users

- `Priya Parent`
  - role: `PARENT_ADMIN`
  - scope: `ParentCo`, `ChildCoA`, `ChildCoB`
- `Maya Manager`
  - role: `CHILD_MANAGER`
  - scope: `ChildCoA`
- `Ben Branch`
  - role: `CHILD_MANAGER`
  - scope: `ChildCoB`
- `Sara Sales`
  - role: `SALES_REP`
  - scope: `ChildCoA`
- `Vic Viewer`
  - role: `VIEWER`
  - scope: `ChildCoA`

### Seed companies

- `ParentCo`
- `ChildCoA`
- `ChildCoB`

### Seed CRM data

- one completed scored lead in `ChildCoA`
- one pending lead in `ChildCoA`
- one failed lead in `ChildCoB`
- one follow-up activity for a completed lead
- one workflow-error activity for a failed lead
- one deal in each child company

Canonical IDs live in [libs/contracts/seed-data.json](./libs/contracts/seed-data.json).

## 7. Async Workflow

Topic: `crm.lead.created`

Payload contract:

```json
{
  "eventType": "LeadCreated",
  "eventId": "uuid",
  "leadId": "uuid",
  "companyId": "uuid",
  "createdByUserId": "uuid",
  "occurredAt": "ISO8601 timestamp",
  "version": 1
}
```

Idempotency / failure handling in the MVP:

- `workflow-service` stores processed events by `eventId`
- duplicate events are skipped once marked `COMPLETED`
- lead processing retries use exponential backoff controlled by `WORKFLOW_MAX_RETRIES` and `WORKFLOW_RETRY_BASE_DELAY_SECONDS`
- CRM follow-up activities are upserted on `workflow_event_id` so duplicate delivery does not create duplicate tasks
- CRM callback writes `FAILED` state when retries are exhausted
- failed deliveries are also published to `crm.lead.created.dlq`
- structured workflow logs include `eventId`, retry attempt, and processing duration

## 8. Access Control

### Roles

- `PARENT_ADMIN`
- `CHILD_MANAGER`
- `SALES_REP`
- `VIEWER`

### Read rules

- parent admins can read child-company CRM data across the hierarchy
- child-scoped roles can read only their own child company

### Mutation rules

- `createLead` is allowed for `PARENT_ADMIN`, `CHILD_MANAGER`, and `SALES_REP`
- `VIEWER` is read-only
- internal workflow update mutations require `x-internal-token`
- cross-user auth context lookups and workflow event introspection require `x-internal-token`

The frontend mirrors visibility for clarity by switching `VIEWER` into a read-only panel, but service resolvers and permission helpers are the real enforcement point.

## 9. Testing

### Verified locally

- `npm test`
- `npm run build:web`
- `npm run build:gateway`
- `npm run test:e2e`
- `docker compose build`
- `docker compose up --build`
- end-to-end smoke path through the running stack:
  - query seeded users
  - query parent-admin visible companies
  - verify `VIEWER` receives a denied `createLead` mutation without leaked stack traces
  - create a lead as `Maya Manager`
  - observe `PENDING -> COMPLETED` plus generated follow-up activity

### CI validation path

- GitHub Actions runs the web and gateway production builds
- `npm test` runs frontend component tests, gateway integration tests, and all four Django service suites
- service tests run on the GitHub runner with `USE_POSTGRES=false`, so they use SQLite instead of trying to resolve Compose-only Postgres hostnames
- a separate Playwright job boots the full Docker Compose stack and runs browser e2e coverage
- `docker compose config` validates the checked-in stack definition on every run
- the current workflow does not require any GitHub repository secrets

### Current automated test coverage

- frontend component tests for user switching and read-only viewer behavior
- gateway integration tests for auth-header forwarding, request context, and aborted-request handling
- auth membership model sanity
- auth cross-user `accessContext` guard
- hierarchy visibility logic
- CRM authorization rules for parent access, sibling isolation, and viewer mutation denial
- CRM exact-duplicate lead rejection and publish-failure rollback
- workflow handler duplicate-event behavior and completion path
- workflow event query internal-token guard
- Playwright e2e coverage for viewer read-only mode and manager lead creation with async completion

### Next tests to add

- contract-level GraphQL resolver tests around gateway composition drift
- workflow failure-path coverage that asserts DLQ payload contents end to end
- load or soak coverage for repeated lead creation and retry pressure

## 10. Assumptions

- I assumed a seed-user selector was acceptable in place of real login for the challenge
- I chose to build one strong async workflow instead of several shallow ones
- I treated synchronous service-to-service GraphQL lookups for auth/company context as acceptable for an MVP
- I kept subgraph URLs exposed for review even though the frontend only uses the gateway

## 11. Tradeoffs

- the workflow service uses its own Postgres database for idempotency even though the original prompt only explicitly listed three database containers
- service apps run with Django `syncdb` style unmigrated models to keep the repo small and the startup path deterministic
- the scoring function is intentionally lightweight and deterministic rather than pretending to be a real ML service
- the web app uses polling instead of subscriptions to make eventual consistency obvious with less infrastructure
- CRM rejects exact duplicate leads within the same child company when `title + contactEmail` match, which keeps the demo resistant to accidental double-submit without trying to solve full real-world lead deduplication

## 12. Future Improvements

See the roadmap in:

- [`event_driven_crm_document_package/upgrades/01_missing_and_future_proofing_gap_analysis.md`](./event_driven_crm_document_package/upgrades/01_missing_and_future_proofing_gap_analysis.md)
- [`event_driven_crm_document_package/upgrades/02_security_privacy_compliance_recommendations.md`](./event_driven_crm_document_package/upgrades/02_security_privacy_compliance_recommendations.md)
- [`event_driven_crm_document_package/upgrades/04_scalability_reliability_operability_roadmap.md`](./event_driven_crm_document_package/upgrades/04_scalability_reliability_operability_roadmap.md)

## 13. Walkthrough Notes

If I were walking through this live, I would focus on:

- why the service split is `auth + company + crm + workflow` instead of a single Django app
- where authorization is enforced on the server and how the UI deliberately mirrors, but does not own, those rules
- why the Kafka workflow uses event-id idempotency, bounded retries, DLQ routing, and activity upserts
- why the browser only talks to the gateway and why the gateway sanitizes downstream errors
- what I would harden next for production: stronger auth, contract tests, observability, and deployment-specific secrets management
