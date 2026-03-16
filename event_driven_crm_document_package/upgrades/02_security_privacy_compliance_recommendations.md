# Security, Privacy, Compliance, and Safety Recommendations

## Security Baseline Already Present
- all CRM authorization enforced server-side
- no direct frontend-to-service communication
- environment-variable driven configuration
- sanitized GraphQL errors at the gateway
- identifier-only Kafka events for `LeadCreated`
- explicit permission helpers instead of UI-only gating
- shared internal token required for cross-user auth context lookups and workflow event inspection

## Recommended Security Additions
- JWT-based auth or signed mock tokens instead of a local demo-user selector
- verification of trusted upstream identity headers between services
- rate limiting and timeout budgets at the gateway
- dependency vulnerability scanning in CI
- security headers and production CORS policy at the gateway and web layer

## Privacy-by-Design Recommendations
- document which CRM fields are PII and why they are required
- define retention expectations for leads, activities, and workflow state
- add delete/export workflows for demo data graduating to real data
- add audit logs for sensitive access and mutation events

## Safe Event Design Status
- current event payloads publish identifiers only, not contact names or emails
- event schemas are versioned
- workflow logs key on `eventId` and `leadId` rather than full CRM payload dumps

## Compliance-Focused Next Steps
- document lawful basis and business-purpose assumptions if this became a real product
- define encryption, backup, and incident-response expectations
- separate local challenge assumptions from production compliance requirements
