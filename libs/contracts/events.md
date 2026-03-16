# Event Contracts

## `crm.lead.created`

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

The workflow service treats `eventId` as the idempotency key and writes failed deliveries to `crm.lead.created.dlq`.

## `crm.lead.created.dlq`

```json
{
  "payload": {
    "eventType": "LeadCreated",
    "eventId": "uuid",
    "leadId": "uuid",
    "companyId": "uuid",
    "createdByUserId": "uuid",
    "occurredAt": "ISO8601 timestamp",
    "version": 1
  },
  "error": "string",
  "retryCount": 3
}
```

The DLQ payload preserves the original event plus the terminal error and the number of processing attempts that were used before the message was abandoned.
