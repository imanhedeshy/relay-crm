# How to Use This Package With Codex

1. Put this document package at the root of your working directory or upload it alongside the repository scaffold.
2. Give Codex:
   - the challenge PDF
   - `prompts/codex_ultra_prompt.md`
   - the `docs/` folder
   - the `upgrades/` folder
   - the `tickets/` folder
3. Instruct Codex to treat:
   - `docs/` as MVP architecture and implementation source of truth
   - `upgrades/` as future-state recommendations and hardening guidance
   - `tickets/` as execution backlog and checklist
4. Ask Codex to generate the repository incrementally:
   - first structure and Compose
   - then backend services
   - then gateway
   - then frontend
   - then worker
   - then docs/tests
5. Validate with a clean run:
   - clone
   - `cp .env.example .env`
   - `docker compose up --build`
