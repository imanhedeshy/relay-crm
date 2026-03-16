# Epic 1 Tasks: Workspace and Infrastructure

## Status
Complete.

- [x] Initialize root workspace files
- [x] Add Nx config
- [x] Create frontend app scaffold
- [x] Create gateway scaffold
- [x] Create Django service scaffolds
- [x] Create worker scaffold
- [x] Define `.env.example`
- [x] Create `docker-compose.yml`
- [x] Add Kafka and Zookeeper services
- [x] Add Postgres services
- [x] Add topic creation strategy
- [x] Add seed data script
- [x] Add service health checks and startup ordering
- [x] Reduce noisy local Kafka startup logs
- [x] Verify `docker compose up --build` works end to end

## Implementation Notes
- Gateway and web wait on healthy upstream services instead of racing startup.
- Kafka and the workflow worker both restart on failure to make local demos more resilient.
- The workflow service creates missing topics on startup, which removed the need for a separate one-off topic init container.
