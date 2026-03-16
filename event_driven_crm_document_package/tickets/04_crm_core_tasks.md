# Epic 4 Tasks: CRM Core

## Status
Complete.

- [x] Define `Lead`
- [x] Define `Deal`
- [x] Define `Activity`
- [x] Add GraphQL types and resolvers
- [x] Implement `createLead`
- [x] Enforce company scoping on reads and writes
- [x] Build basic lead list UI
- [x] Build lead creation form
- [x] Build company-scoped CRM pages
- [x] Add role-aware read-only state for viewer users
- [x] Handle user switching without stale company scope

## Implementation Notes
- The dashboard polls CRM every 3 seconds so asynchronous scoring updates are visible.
- The selected company scope resets safely when the viewer changes, preventing stale cross-user authorization errors.
