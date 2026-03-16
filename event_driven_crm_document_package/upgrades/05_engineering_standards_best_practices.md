# Engineering Standards and Best Practices

## Current Repo Strengths
- small service boundaries with clear ownership across auth, company, CRM, workflow, gateway, and web
- explicit permission helpers rather than scattered authorization logic
- environment-driven settings and Docker-first local runtime
- typed React query shapes and predictable local UI state
- explicit loading, empty, and error states in the dashboard
- architecture notes, ADRs, contracts, and README kept aligned with the code

## Python / Django Standards to Preserve
- keep GraphQL resolvers thin and delegate workflow behavior to dedicated helpers
- keep authorization centralized in permission helpers
- continue using typed helper objects or dataclasses where they make workflow code easier to reason about
- keep service settings modular and environment-driven

## TypeScript / React Standards to Preserve
- keep the Apollo client pointed only at the gateway
- keep role-aware UI behavior explicit instead of inferred indirectly
- avoid unnecessary global state beyond the selected demo user
- keep async status rendering and polling behavior easy to trace in one place

## Best Next Engineering Upgrades
- add GraphQL code generation for operation and schema typing
- introduce shared request correlation IDs across the stack
- standardize error envelopes across subgraphs
- expand service-level tests around federation edge cases and startup resilience
