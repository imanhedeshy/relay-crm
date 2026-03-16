# Submission and Review Checklist

## Before Coding Ends
- [x] Every challenge requirement is mapped to a concrete implementation
- [x] Service boundaries remain clean
- [x] One meaningful Kafka workflow is implemented
- [x] Parent-child access model is enforced on the server side

## Before Finalizing the Repo
- [x] `docker compose up --build` works from the current workspace
- [x] Frontend talks only to the gateway
- [x] Seed users and companies are available
- [x] Async status is visible in the UI
- [x] Authorization tests exist
- [x] Frontend component tests exist
- [x] Gateway integration tests exist
- [x] Playwright end-to-end coverage exists
- [x] README is complete
- [x] Assumptions are documented
- [x] Tradeoffs are documented

## Before Submission
- [x] Fresh clone dry run after repository initialization
- [x] Repo link ready after `git init`, commit, remote add, and push
- [x] GitHub Actions validation path is configured for runner-safe service tests
- [x] GitHub Actions validates the browser flow against the Docker Compose stack
- [x] README reviewed for clarity
- [x] Architectural story documented and review-ready
- [x] Async workflow explanation documented and review-ready
- [x] Permission model explanation documented and review-ready
