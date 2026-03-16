# Access Control Model

## Hard requirement
Access control must be enforced server-side.

## User roles

Recommended:
- `PARENT_ADMIN`
- `CHILD_MANAGER`
- `SALES_REP`
- `VIEWER`

## Company hierarchy model

- parent companies own child companies logically
- CRM data belongs to child companies
- parent admins may view across children
- child users are isolated to their own child company
- sibling child companies cannot access one another

## Enforcement points

### Gateway
May:
- pass auth context
- reject obviously unauthenticated requests

### Service resolvers
Must:
- enforce company scope
- enforce role checks
- validate parent-child visibility
- reject unauthorized entity access

### Service layer / domain layer
Should:
- contain reusable permission helpers
- avoid duplicating authorization logic everywhere

## Test cases that must exist
- parent admin sees child company data
- child manager can see own child data
- child manager cannot see sibling child data
- unauthorized mutation fails
- frontend hidden routes are not treated as authorization
