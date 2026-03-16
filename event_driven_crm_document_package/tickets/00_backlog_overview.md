# Backlog Overview

## Status Snapshot
This challenge backlog is functionally complete in the current repository. All six epics are implemented end to end, the repository is pushed, and CI covers builds, service tests, and browser-level verification.

## Epic 1: Workspace and Infrastructure
- Status: complete
- Nx workspace, React web app, Apollo gateway, four Django services, and Docker Compose are wired together.
- Local runtime includes seeded data, health checks, restart behavior, and quieter Kafka logging for easier demos.

## Epic 2: Auth and Authorization
- Status: complete
- `auth-service` owns users and memberships, the gateway forwards `x-user-id`, and CRM permissions are enforced server-side.
- Read, write, and cross-company authorization paths are covered by service tests and live browser verification.

## Epic 3: Company Hierarchy
- Status: complete
- `company-service` models parent and child companies, exposes hierarchy queries, and seeds `ParentCo`, `ChildCoA`, and `ChildCoB`.
- Parent admins can traverse child scopes while child-company users stay isolated to their assigned company.

## Epic 4: CRM Core
- Status: complete
- CRM owns leads, deals, and activities plus company-scoped queries and mutations.
- The UI supports role-aware browsing, lead creation for write-capable roles, and a read-only state for `VIEWER`.

## Epic 5: Async Workflow
- Status: complete
- Lead creation publishes `LeadCreated`, Kafka drives scoring and follow-up creation, and the UI shows eventual consistency.
- Idempotency, retries with exponential backoff, DLQ routing, failure marking, and structured logs are all implemented.

## Epic 6: Documentation and Polish
- Status: complete in repo
- Root README, architecture notes, ADRs, contracts, and submission-oriented docs reflect the current implementation.
- The repository is pushed and the submission docs match the shipped system.
