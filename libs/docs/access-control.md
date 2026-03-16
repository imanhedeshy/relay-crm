# Access Control Notes

Authorization is enforced in service resolvers and service-layer helpers.

- `PARENT_ADMIN` can access all descendants of their parent company.
- `CHILD_MANAGER`, `SALES_REP`, and `VIEWER` are limited to their own child company.
- `VIEWER` is read-only and cannot call `createLead`.
- The frontend mirrors those boundaries for clarity, but the backend still rejects unauthorized reads and mutations.
