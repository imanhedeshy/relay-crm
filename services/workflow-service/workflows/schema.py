import os

from ariadne import QueryType
from ariadne.contrib.federation import FederatedObjectType, make_federated_schema
from graphql import GraphQLError

from workflows.models import ProcessedEvent

type_defs = """
    type WorkflowEvent @key(fields: "id") {
      id: ID!
      eventId: ID!
      leadId: ID!
      status: String!
      retryCount: Int!
      lastError: String
      processedAt: String
      updatedAt: String!
    }

    type WorkflowHealth {
      kafkaTopic: String!
      dlqTopic: String!
    }

    type Query {
      workflowEvents: [WorkflowEvent!]!
      workflowHealth: WorkflowHealth!
    }
"""

query = QueryType()
workflow_event = FederatedObjectType("WorkflowEvent")


def _require_internal_token(info):
    provided_token = info.context.headers.get("x-internal-token")
    expected_token = os.getenv("INTERNAL_SERVICE_TOKEN", "relay-internal-token")
    if not provided_token or provided_token != expected_token:
        raise GraphQLError("Internal service token required.")


@query.field("workflowEvents")
def resolve_workflow_events(_obj, info):
    _require_internal_token(info)
    return ProcessedEvent.objects.all()


@query.field("workflowHealth")
def resolve_workflow_health(*_args):
    return {
        "kafkaTopic": os.getenv("KAFKA_TOPIC_LEAD_CREATED", "crm.lead.created"),
        "dlqTopic": os.getenv("KAFKA_TOPIC_LEAD_CREATED_DLQ", "crm.lead.created.dlq"),
    }


@workflow_event.reference_resolver
def resolve_workflow_event_reference(_obj, _info, representation):
    return ProcessedEvent.objects.filter(id=representation["id"]).first()


@workflow_event.field("id")
def resolve_model_id(obj, *_args):
    return str(obj.id)


@workflow_event.field("eventId")
def resolve_event_id(obj, *_args):
    return str(obj.event_id)


@workflow_event.field("leadId")
def resolve_lead_id(obj, *_args):
    return str(obj.lead_id)


@workflow_event.field("retryCount")
def resolve_retry_count(obj, *_args):
    return obj.retry_count


@workflow_event.field("lastError")
def resolve_last_error(obj, *_args):
    return obj.last_error or None


@workflow_event.field("processedAt")
def resolve_processed_at(obj, *_args):
    return obj.processed_at.isoformat() if obj.processed_at else None


@workflow_event.field("updatedAt")
def resolve_updated_at(obj, *_args):
    return obj.updated_at.isoformat()


schema = make_federated_schema(type_defs, [query, workflow_event])
