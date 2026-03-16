# Epic 3 Tasks: Company Hierarchy

## Status
Complete.

- [x] Define `Company` model
- [x] Add `type` (parent/child)
- [x] Add parent-child relationships
- [x] Implement hierarchy queries
- [x] Implement child company lookup
- [x] Seed `ParentCo`, `ChildCoA`, and `ChildCoB`
- [x] Add tests for hierarchy visibility

## Implementation Notes
- Company visibility returned to the web app is already filtered to the selected viewer context.
- Parent admins can traverse child scopes; non-parent roles remain pinned to their assigned child company.
