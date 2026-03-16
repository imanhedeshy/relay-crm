# Codex Prompt: Build the Event-Driven CRM Challenge

You are building a complete take-home technical challenge repository for an event-driven CRM system.

Your output must be production-quality enough to demonstrate strong engineering judgment, but intentionally scoped to a well-designed MVP.

## Primary mission

Build a small event-driven CRM that fully satisfies the challenge requirements and is easy to run, easy to review, and easy to explain in an interview.

## Challenge requirements you must satisfy

- Backend: Python, Django, GraphQL
- Frontend: React, Apollo Client
- Architecture / Infrastructure: Nx workspace, GraphQL Federation, Kafka, Docker & Docker Compose
- Multiple backend services, not a single monolith
- Each backend service exposes a GraphQL API
- A GraphQL gateway federates these APIs
- Frontend communicates only with the gateway
- Kafka is used for asynchronous processing
- All services run together using Docker Compose
- CRM supports:
  - customer-related data
  - multiple companies
  - parent and child company hierarchy
  - access control based on user roles
  - at least one asynchronous workflow using a queue system
- UI must reflect eventual consistency
- Access control must be enforced server-side
- README must explain:
  - how to run
  - service URLs
  - architecture
  - asynchronous workflow
  - assumptions and tradeoffs

## Important implementation philosophy

Do not overbuild.
Do not create a giant CRM.
Do not create unnecessary services.
Do not add complexity that hurts clarity.

Prefer a small, clean, well-explained subset.

## Required architecture

Create a monorepo with this structure:

- `apps/web`
- `apps/gateway`
- `services/auth-service`
- `services/company-service`
- `services/crm-service`
- `services/workflow-service`
- `libs/contracts`
- `libs/docs`
- `libs/scripts`
- `infra/kafka`
- `infra/postgres`

## Exact service responsibilities

### auth-service
Owns:
- users
- memberships
- roles
- company access metadata

### company-service
Owns:
- companies
- parent/child hierarchy
- visibility lineage

### crm-service
Owns:
- leads
- deals
- activities
- mutations
- publishing Kafka events

### workflow-service
Owns:
- Kafka consumers
- retry logic
- idempotency
- asynchronous side effects

### gateway
Owns:
- Apollo federation gateway
- auth context propagation
- subgraph composition

### web
Owns:
- React app
- Apollo Client
- loading/error states
- role-aware screens
- async state visibility

## Required async workflow

Implement exactly one strong async workflow:

### LeadCreated flow
1. User creates a lead in the frontend
2. Frontend sends GraphQL mutation to gateway
3. Gateway routes to crm-service
4. crm-service validates access, stores lead, sets `scoringStatus = PENDING`
5. crm-service publishes `LeadCreated` event to Kafka
6. workflow-service consumes event
7. worker performs lightweight scoring/follow-up generation
8. worker updates lead `score` and `scoringStatus = COMPLETED`
9. worker creates follow-up activity
10. frontend visibly reflects pending -> completed state

## Queue design requirements

You must include thoughtful handling for:
- duplicate message delivery
- retries
- failure handling
- observability

Implement at least:
- `eventId`-based idempotency
- basic retry strategy
- failed status update or failed-event handling
- structured logs including event IDs

## Parent-child company rules

- CRM data belongs to child companies
- Parent admins may view across their child companies
- Child companies must be isolated from each other

## User roles

Implement at least:
- `PARENT_ADMIN`
- `CHILD_MANAGER`
- `SALES_REP`
- `VIEWER`

## Access control

Access must be enforced server-side.
Do not rely on frontend-only restrictions.

Implement reusable permission helpers in backend services.

## Required packages

### Root
- nx
- @nx/js
- @nx/react
- @nx/vite
- typescript

### Web
- react
- react-dom
- react-router-dom
- @apollo/client
- graphql
- vite
- @vitejs/plugin-react

### Gateway
- @apollo/server
- @apollo/gateway
- graphql
- express
- cors
- tsx

### Python services
- Django
- ariadne
- psycopg[binary]
- python-dotenv
- gunicorn

### Async worker
- confluent-kafka
- tenacity
- structlog

## Docker Compose requirements

The following services must be runnable together:
- web
- gateway
- auth-service
- company-service
- crm-service
- workflow-service
- auth-db
- company-db
- crm-db
- zookeeper
- kafka

Must work with:
`docker compose up --build`

## Frontend scope

Do not overbuild the UI.

Required screens:
- simple login/user selector or seed-user selection mechanism
- company hierarchy or company selector
- lead list
- lead creation form
- detail or list state showing async scoring status
- basic deals/activities view if feasible

Requirements:
- loading states
- error states
- clear async status
- role-aware visibility

## Testing requirements

Add some meaningful tests around:
- authorization logic
- hierarchy visibility
- async workflow handler logic

If something is not fully tested, document what would be tested next.

## Documentation requirements

Generate:
- top-level `README.md`
- architecture notes
- ADRs
- assumptions and tradeoffs section
- service URL list
- async workflow explanation
- seed data explanation

## Package files to honor

The repository you generate should align with the planning documents in this package, especially:
- `docs/01_architecture_blueprint.md`
- `docs/02_repository_structure.md`
- `docs/03_graphql_federation_and_schema_ownership.md`
- `docs/04_async_workflow_and_kafka_design.md`
- `docs/05_access_control_and_multi_tenancy.md`
- `docs/06_docker_compose_runtime_and_seed_strategy.md`
- `docs/07_libraries_packages_and_tooling.md`
- `docs/08_readme_template.md`
- `docs/09_challenge_coverage_checklist.md`

And it should treat the files under `upgrades/` as future-state guidance, not necessarily full MVP scope.

## Engineering standards

Code must be:
- modular
- typed where practical
- consistent
- documented
- readable
- security-aware
- backend-enforced for permissions
- clear about ownership boundaries

## Explicit anti-goals

Do not:
- implement a giant monolith
- add random services that do not help challenge coverage
- use frontend-only access control
- add decorative Kafka with no real business effect
- optimize for visual polish over architecture
- hide assumptions
- create unclear or magical bootstrapping steps

## Deliverables

Produce:
- full repo source code
- docker-compose.yml
- .env.example
- README.md
- seed data support
- all necessary Dockerfiles
- runnable local system
- enough code and documentation to discuss architecture, tradeoffs, retries, duplicates, and permissions in depth

Build the project completely and coherently, using the planning package as the implementation source of truth.
