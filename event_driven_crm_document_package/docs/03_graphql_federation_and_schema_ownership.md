# GraphQL Schema Ownership and Federation Plan

## Goal

Keep schemas:
- clean
- understandable
- minimally federated
- clearly owned by service

## Auth service owns

- `User`
- `Membership`
- `UserRole`
- identity and company membership lookups

## Company service owns

- `Company`
- `CompanyType`
- hierarchy traversal
- child company visibility logic

## CRM service owns

- `Lead`
- `Deal`
- `Contact`
- `Activity`
- `LeadStatus`
- `AsyncStatus`
- mutations such as `createLead`

## Federation model

Use a simple entity-reference model.

### CRM extends
- `Company` by external `id`
- `User` by external `id`

### Why not more?
Because the challenge explicitly asks for meaningful federation without unnecessary complexity. Use federation where it clarifies ownership, not everywhere just to look advanced.

## Gateway responsibility

Frontend must talk only to gateway.

Gateway will:
- compose subgraphs
- inject auth context
- hide service boundaries from the frontend
- be the only external GraphQL entrypoint
