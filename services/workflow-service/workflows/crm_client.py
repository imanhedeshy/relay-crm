import json
import os
from urllib import request

from tenacity import retry, stop_after_attempt, wait_fixed


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
def apply_workflow_result(*, lead_id: str, event_id: str, score: int | None, follow_up_note: str, mark_failed: bool, failure_reason: str | None = None):
    payload = json.dumps(
        {
            "query": """
                mutation ApplyLeadWorkflowResult($input: ApplyLeadWorkflowResultInput!) {
                  applyLeadWorkflowResult(input: $input) {
                    id
                    scoringStatus
                    score
                  }
                }
            """,
            "variables": {
                "input": {
                    "leadId": lead_id,
                    "eventId": event_id,
                    "score": score,
                    "followUpNote": follow_up_note,
                    "markFailed": mark_failed,
                    "failureReason": failure_reason,
                }
            },
        }
    ).encode("utf-8")
    req = request.Request(
        os.getenv("CRM_SERVICE_URL", "http://crm-service:8000/graphql/"),
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-internal-token": os.getenv("INTERNAL_SERVICE_TOKEN", "relay-internal-token"),
        },
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        body = json.loads(response.read().decode("utf-8"))
    if body.get("errors"):
        raise RuntimeError(body["errors"][0]["message"])
    return body["data"]["applyLeadWorkflowResult"]
