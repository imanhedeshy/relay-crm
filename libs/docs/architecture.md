# Architecture Notes

The system is intentionally split into four Python services plus a gateway and web client.

- `auth-service` owns users, roles, and memberships.
- `company-service` owns the company tree and computes visible companies.
- `crm-service` owns leads, deals, activities, and Kafka event publication.
- `workflow-service` owns background processing state, retries, DLQ routing, and Kafka consumption.
- `gateway` is the only GraphQL endpoint used by the browser and forwards the selected `x-user-id` context to subgraphs.
- `web` is a React + Apollo client that persists the seeded demo user and performs a clean reload when the reviewer switches roles.

The main asynchronous workflow is `LeadCreated -> score lead -> create follow-up activity`.
