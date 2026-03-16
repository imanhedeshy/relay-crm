from dataclasses import dataclass
from datetime import datetime, timezone


def calculate_score(event):
    token = event["leadId"].replace("-", "")[:8]
    score = 50 + (int(token, 16) % 51)
    return min(score, 100)


def build_follow_up_note(score: int):
    if score >= 85:
        return "High-intent lead. Reach out within 24 hours and tailor the pitch to expansion timing."
    if score >= 70:
        return "Qualified lead. Schedule a discovery call this week and confirm budget owner."
    return "Early-stage lead. Send a nurture email and create a follow-up task for next week."


class LeadCreatedHandler:
    def __init__(self, state_store, crm_client, logger):
        self.state_store = state_store
        self.crm_client = crm_client
        self.logger = logger

    def handle(self, event):
        event_id = event["eventId"]
        existing_status = self.state_store.status(event_id)
        if existing_status == "COMPLETED":
            self.logger.info("duplicate_event_skipped", eventId=event_id, leadId=event["leadId"])
            return "duplicate"

        self.state_store.mark_processing(event_id, event["leadId"])
        score = calculate_score(event)
        follow_up_note = build_follow_up_note(score)
        self.crm_client(
            lead_id=event["leadId"],
            event_id=event_id,
            score=score,
            follow_up_note=follow_up_note,
            mark_failed=False,
            failure_reason=None,
        )
        self.state_store.mark_completed(event_id)
        self.logger.info("workflow_completed", eventId=event_id, leadId=event["leadId"], score=score)
        return "completed"

    def handle_failure(self, event, error_message: str):
        self.state_store.mark_failed(event["eventId"], error_message)
        self.crm_client(
            lead_id=event["leadId"],
            event_id=event["eventId"],
            score=None,
            follow_up_note="Workflow failed.",
            mark_failed=True,
            failure_reason=error_message,
        )


@dataclass
class InMemoryStateStore:
    records: dict

    def status(self, event_id):
        return self.records.get(event_id, {}).get("status")

    def mark_processing(self, event_id, lead_id):
        record = self.records.setdefault(event_id, {"leadId": lead_id, "retryCount": 0})
        record["status"] = "PROCESSING"
        record["retryCount"] += 1
        record["updatedAt"] = datetime.now(timezone.utc).isoformat()

    def mark_completed(self, event_id):
        record = self.records.setdefault(event_id, {})
        record["status"] = "COMPLETED"
        record["updatedAt"] = datetime.now(timezone.utc).isoformat()

    def mark_failed(self, event_id, error_message):
        record = self.records.setdefault(event_id, {})
        record["status"] = "FAILED"
        record["lastError"] = error_message
        record["updatedAt"] = datetime.now(timezone.utc).isoformat()
