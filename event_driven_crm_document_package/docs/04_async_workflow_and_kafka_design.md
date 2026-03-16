# Async Workflow Design

## Primary async workflow

### Workflow chosen
Lead creation followed by asynchronous enrichment/scoring/follow-up generation.

## Request-response phase
1. User submits `createLead`
2. `crm-service` validates user role and company access
3. Lead is stored with:
   - `status = NEW`
   - `scoringStatus = PENDING`
4. `crm-service` publishes Kafka event:
   - topic: `crm.lead.created`

## Async processing phase
1. `workflow-service` consumes `crm.lead.created`
2. Worker checks idempotency store
3. Worker marks processing state
4. Worker calculates score and follow-up task
5. Worker writes:
   - lead score
   - `scoringStatus = COMPLETED`
   - follow-up activity

## UI behavior

Frontend must show:
- lead appears immediately
- score or follow-up may appear after delay
- processing status clearly visible
- error/failed state if processing fails

## Event shape

```json
{
  "eventType": "LeadCreated",
  "eventId": "uuid",
  "leadId": "uuid",
  "companyId": "uuid",
  "createdByUserId": "uuid",
  "occurredAt": "ISO8601 timestamp",
  "version": 1
}
```

## Queue design concerns

### Duplicate delivery
Handle with:
- event id
- idempotency table or processed-event table
- no duplicate follow-up activity creation

### Retries
Handle with:
- retry count metadata
- bounded retries
- exponential backoff if needed
- poison event or DLQ strategy

### Failure handling
Handle with:
- structured logs
- failed status on lead if processing irrecoverably fails
- dead-letter topic for manual inspection

### Observability
Include:
- structured logs
- event IDs in logs
- processing duration logs
- success/failure counters if time allows
