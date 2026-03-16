# Epic 2 Tasks: Auth and Authorization

## Status
Complete.

- [x] Define `User`
- [x] Define `Membership`
- [x] Define `UserRole`
- [x] Add sample users and memberships
- [x] Implement `viewer` / `me`-style auth query
- [x] Implement auth context propagation through gateway
- [x] Create permission helpers
- [x] Enforce role checks in resolvers
- [x] Add tests for parent-admin access
- [x] Add tests for child-company isolation
- [x] Add tests for unauthorized access denial
- [x] Add read-only viewer behavior for CRM

## Implementation Notes
- The gateway forwards the seeded demo identity using `x-user-id`.
- CRM authorization is enforced server-side for both reads and writes.
- `VIEWER` can inspect scoped CRM data but cannot call `createLead`.
- Cross-user `accessContext` lookups now require `x-internal-token`, which closes an otherwise easy federation-side information leak.
