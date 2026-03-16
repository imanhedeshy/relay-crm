# README Template

Use this README structure in the final repo.

## 1. Project Overview
- What the system is
- What subset of CRM was chosen
- Why the architecture is split into services

## 2. Tech Stack
- React
- Apollo Client
- Apollo Gateway
- Python / Django
- Ariadne
- Kafka
- PostgreSQL
- Docker Compose
- Nx

## 3. Architecture Summary
- service responsibilities
- gateway
- async workflow
- parent/child company hierarchy
- authorization model

## 4. How to Run
```bash
cp .env.example .env
docker compose up --build
```

## 5. Service URLs
- web
- gateway
- subgraph endpoints if exposed

## 6. Seed Credentials / Demo Data
- sample users
- sample roles
- sample companies

## 7. Async Workflow
- what event is published
- what consumer does
- how eventual consistency appears in the UI

## 8. Access Control
- role definitions
- parent-child visibility rules
- server-side enforcement explanation

## 9. Testing
- what is covered
- what is intentionally not covered yet
- what would be tested next

## 10. Assumptions
## 11. Tradeoffs
## 12. Future Improvements
Point to the `upgrades/` folder for full roadmap and recommendations.
