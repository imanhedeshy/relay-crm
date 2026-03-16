# Docker Compose and Runtime Plan

## Mandatory outcome

The entire system must run with:

```bash
docker compose up --build
```

## Services to include
- `web`
- `gateway`
- `auth-service`
- `company-service`
- `crm-service`
- `workflow-service`
- `auth-db`
- `company-db`
- `crm-db`
- `zookeeper`
- `kafka`

## Recommended ports
- `web` -> `3000`
- `gateway` -> `4000`
- `auth-service` -> `8001`
- `company-service` -> `8002`
- `crm-service` -> `8003`

## Seed data

Recommended seed users:
- parent admin
- child manager A
- child manager B
- sales rep

Recommended seed companies:
- ParentCo
- ChildCoA
- ChildCoB

Recommended seed CRM records:
- a few leads per child company
- one pre-scored lead
- one pending lead
- one failed lead for demo if time permits
