# Repository Structure

```text
event-driven-crm/
├── README.md
├── docker-compose.yml
├── .env.example
├── package.json
├── nx.json
├── tsconfig.base.json
├── .gitignore
│
├── apps/
│   ├── web/
│   └── gateway/
│
├── services/
│   ├── auth-service/
│   ├── company-service/
│   ├── crm-service/
│   └── workflow-service/
│
├── libs/
│   ├── contracts/
│   ├── docs/
│   └── scripts/
│
├── infra/
│   ├── kafka/
│   └── postgres/
│
└── .github/
    └── workflows/
```

## Detailed layout

### `apps/web`
Contains:
- React app
- Apollo Client setup
- feature-based folders:
  - auth
  - companies
  - leads
  - deals
  - async-status
- lightweight shared components
- route definitions
- frontend environment config

### `apps/gateway`
Contains:
- Apollo Gateway bootstrap
- service registration / service list
- context creation
- request-level auth propagation
- optional lightweight telemetry hooks

### `services/auth-service`
Contains:
- Django project
- authz app
- GraphQL schema/resolvers
- role and membership models
- permission utility functions

### `services/company-service`
Contains:
- Django project
- companies app
- hierarchy traversal logic
- GraphQL schema/resolvers
- company visibility utilities

### `services/crm-service`
Contains:
- Django project
- CRM models
- mutations
- GraphQL resolvers
- event publishing utilities
- permission enforcement around CRUD actions

### `services/workflow-service`
Contains:
- Kafka consumers
- event handlers
- retry logic
- idempotency store helpers
- worker bootstrapping

### `libs/contracts`
Contains:
- event payload examples
- contract notes
- cross-service entity reference guidance

### `libs/docs`
Contains:
- architecture notes
- permissions notes
- async workflow notes

### `libs/scripts`
Contains:
- wait-for-it scripts
- seed scripts
- topic init scripts

### `infra`
Contains:
- kafka topic setup
- postgres init scripts
- optional local monitoring stubs
