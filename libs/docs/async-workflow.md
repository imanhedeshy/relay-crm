# Async Workflow Notes

1. `createLead` stores a lead with `scoringStatus=PENDING`.
2. `crm-service` publishes a `crm.lead.created` event to Kafka.
3. `workflow-service` consumes the event and records processing state by `eventId`.
4. The worker computes a deterministic score, generates a follow-up note, and updates the lead through an internal GraphQL mutation on `crm-service`.
5. Failed handler attempts are retried with exponential backoff.
6. When retries are exhausted, the workflow marks the lead `FAILED`, writes a workflow-error activity, and publishes the event to `crm.lead.created.dlq`.
7. The web app polls the gateway and shows `PENDING`, `COMPLETED`, or `FAILED`.
8. Structured workflow logs include the event id, attempt number, retry decision, and processing duration.
