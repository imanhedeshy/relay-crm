import json
import os
from urllib import error, request


def fetch_access_context(user_id: str):
    endpoint = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000/graphql/")
    payload = json.dumps(
        {
            "query": """
                query AccessContext($userId: ID) {
                  accessContext(userId: $userId) {
                    userId
                    fullName
                    memberships {
                      companyId
                      role
                    }
                  }
                }
            """,
            "variables": {"userId": user_id},
        }
    ).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-internal-token": os.getenv("INTERNAL_SERVICE_TOKEN", "relay-internal-token"),
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError("Auth service is unavailable.") from exc
    if body.get("errors"):
        raise RuntimeError(body["errors"][0]["message"])
    return body.get("data", {}).get("accessContext")
