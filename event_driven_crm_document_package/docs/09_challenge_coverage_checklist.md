# Challenge Coverage Checklist

## Current Coverage Status
- [x] Backend uses Python, Django, and GraphQL
- [x] Frontend uses React and Apollo Client
- [x] Nx workspace is present
- [x] GraphQL federation is implemented through the gateway
- [x] Kafka drives one meaningful async workflow
- [x] Docker Compose runs the full stack end to end
- [x] Multiple backend services are used instead of a monolith
- [x] Frontend communicates only with the gateway
- [x] Parent-child company hierarchy is implemented
- [x] Access control is enforced server-side
- [x] Loading, error, and eventual-consistency states are visible in the UI
- [x] README documents run instructions, architecture, async workflow, assumptions, and tradeoffs
- [x] Source code, Compose config, and reviewer-facing docs are ready
- [x] Git repository packaging and remote push are complete
- [x] GitHub Actions validates builds, service tests, and `docker compose config`

## Goes Beyond the Challenge
See `upgrades/` for the gap analysis and next-step recommendations around:
- security hardening
- privacy and compliance
- accessibility and i18n
- observability and operability
- scalability and long-term evolution
