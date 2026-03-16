# Epic 5 Tasks: Async Workflow

## Status
Complete.

- [x] Define `LeadCreated` event contract
- [x] Publish event on lead creation
- [x] Create Kafka consumer
- [x] Add idempotency handling
- [x] Add retry strategy
- [x] Add failure handling
- [x] Update lead status asynchronously
- [x] Create follow-up activity
- [x] Surface async state in frontend
- [x] Add tests around event handler logic
- [x] Add DLQ topic and payload contract
- [x] Add exponential backoff configuration
- [x] Keep the worker alive across broker startup races and crashes

## Implementation Notes
- The event contract publishes identifiers only, not contact PII.
- Workflow processing is stored in Postgres by `eventId`, so duplicate delivery does not create duplicate follow-up work.
- When retries are exhausted, CRM marks the lead failed, writes a workflow-error activity, and the original event is sent to `crm.lead.created.dlq`.
- Workflow event inspection is now treated as an internal-only query and requires `x-internal-token`.
