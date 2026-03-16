import json
import os
from urllib import error, request


def _post_graphql(url: str, query: str, variables=None, headers=None, service_name="Upstream service"):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    request_headers = {"Content-Type": "application/json", **(headers or {})}
    req = request.Request(url, data=payload, headers=request_headers, method="POST")
    try:
        with request.urlopen(req, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{service_name} is unavailable.") from exc
    if body.get("errors"):
        raise RuntimeError(body["errors"][0]["message"])
    return body.get("data", {})


def fetch_access_context(user_id: str):
    return _post_graphql(
        os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000/graphql/"),
        """
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
        {"userId": user_id},
        headers={"x-internal-token": os.getenv("INTERNAL_SERVICE_TOKEN", "relay-internal-token")},
        service_name="Auth service",
    ).get("accessContext")


def fetch_visible_companies(user_id: str):
    companies = _post_graphql(
        os.getenv("COMPANY_SERVICE_URL", "http://company-service:8000/graphql/"),
        """
            query VisibleCompanies {
              companies {
                id
                companyType
              }
            }
        """,
        headers={"x-user-id": user_id},
        service_name="Company service",
    ).get("companies", [])
    return {company["id"]: company["companyType"] for company in companies}
