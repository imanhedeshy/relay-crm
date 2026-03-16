import logging

from django.db import transaction

from ariadne import MutationType, ObjectType, QueryType
from ariadne.contrib.federation import FederatedObjectType, make_federated_schema
from graphql import GraphQLError

from crm.events import publish_lead_created
from crm.models import Activity, ActivityKind, Deal, Lead, AsyncStatus
from crm.permissions import AuthorizationError, READ_ROLES, WRITE_ROLES, authorize_company_access
from crm.service_clients import fetch_access_context, fetch_visible_companies

type_defs = """
    enum LeadStatus {
      NEW
      QUALIFIED
    }

    enum AsyncStatus {
      PENDING
      COMPLETED
      FAILED
    }

    enum ActivityKind {
      FOLLOW_UP
      NOTE
      WORKFLOW_ERROR
    }

    enum DealStage {
      DISCOVERY
      PROPOSAL
      WON
    }

    type Company @key(fields: "id") {
      id: ID!
    }

    type User @key(fields: "id") {
      id: ID!
    }

    type Lead @key(fields: "id") {
      id: ID!
      company: Company!
      createdBy: User!
      title: String!
      contactName: String!
      contactEmail: String!
      status: LeadStatus!
      scoringStatus: AsyncStatus!
      score: Int
      createdAt: String!
      updatedAt: String!
      activities: [Activity!]!
    }

    type Activity @key(fields: "id") {
      id: ID!
      lead: Lead!
      kind: ActivityKind!
      note: String!
      createdAt: String!
    }

    type Deal @key(fields: "id") {
      id: ID!
      name: String!
      stage: DealStage!
      valueCents: Int!
    }

    input CreateLeadInput {
      companyId: ID!
      title: String!
      contactName: String!
      contactEmail: String!
    }

    input ApplyLeadWorkflowResultInput {
      leadId: ID!
      eventId: ID!
      score: Int
      followUpNote: String!
      markFailed: Boolean
      failureReason: String
    }

    type Query {
      leads(companyId: ID!): [Lead!]!
      lead(id: ID!): Lead
      activities(companyId: ID!): [Activity!]!
      deals(companyId: ID!): [Deal!]!
    }

    type Mutation {
      createLead(input: CreateLeadInput!): Lead!
      applyLeadWorkflowResult(input: ApplyLeadWorkflowResultInput!): Lead!
    }
"""

query = QueryType()
mutation = MutationType()
lead = FederatedObjectType("Lead")
activity = FederatedObjectType("Activity")
deal = FederatedObjectType("Deal")
logger = logging.getLogger(__name__)


def _request_user_id(info):
    return info.context.headers.get("x-user-id")


def _resolve_access(info, company_id: str, allowed_roles):
    user_id = _request_user_id(info)
    if not user_id:
        raise GraphQLError("Authentication required.")
    access_context = fetch_access_context(user_id)
    if not access_context:
        raise GraphQLError("Authentication required.")
    visible_companies = fetch_visible_companies(user_id)
    try:
        authorize_company_access(access_context, visible_companies, company_id, allowed_roles)
    except AuthorizationError as error:
        raise GraphQLError(str(error)) from error
    return access_context, visible_companies


def _require_internal_token(info):
    provided_token = info.context.headers.get("x-internal-token")
    expected_token = __import__("os").getenv("INTERNAL_SERVICE_TOKEN", "relay-internal-token")
    if not provided_token or provided_token != expected_token:
        raise GraphQLError("Internal service token required.")


def _clean_create_lead_input(input):
    title = input["title"].strip()
    contact_name = input["contactName"].strip()
    contact_email = input["contactEmail"].strip().lower()

    if not title:
        raise GraphQLError("Lead title is required.")
    if not contact_name:
        raise GraphQLError("Contact name is required.")
    if not contact_email:
        raise GraphQLError("Contact email is required.")

    return {
        "companyId": input["companyId"],
        "title": title,
        "contactName": contact_name,
        "contactEmail": contact_email,
    }


def _find_duplicate_lead(company_id, title, contact_email):
    return (
        Lead.objects.filter(
            company_id=company_id,
            title__iexact=title,
            contact_email__iexact=contact_email,
        )
        .order_by("-created_at")
        .first()
    )


@query.field("leads")
def resolve_leads(_obj, info, companyId):
    _resolve_access(info, companyId, READ_ROLES)
    return Lead.objects.filter(company_id=companyId).prefetch_related("activities").all()


@query.field("lead")
def resolve_lead(_obj, info, id):
    lead_obj = Lead.objects.filter(id=id).first()
    if not lead_obj:
        return None
    _resolve_access(info, str(lead_obj.company_id), READ_ROLES)
    return lead_obj


@query.field("activities")
def resolve_activities(_obj, info, companyId):
    _resolve_access(info, companyId, READ_ROLES)
    return Activity.objects.filter(company_id=companyId).select_related("lead").all()


@query.field("deals")
def resolve_deals(_obj, info, companyId):
    _resolve_access(info, companyId, READ_ROLES)
    return Deal.objects.filter(company_id=companyId).all()


@mutation.field("createLead")
def resolve_create_lead(_obj, info, input):
    user_id = _request_user_id(info)
    clean_input = _clean_create_lead_input(input)
    _resolve_access(info, clean_input["companyId"], WRITE_ROLES)

    existing_lead = _find_duplicate_lead(
        clean_input["companyId"],
        clean_input["title"],
        clean_input["contactEmail"],
    )
    if existing_lead:
        raise GraphQLError("A lead with this title and contact email already exists in the selected company.")

    with transaction.atomic():
        lead_obj = Lead.objects.create(
            company_id=clean_input["companyId"],
            created_by_user_id=user_id,
            title=clean_input["title"],
            contact_name=clean_input["contactName"],
            contact_email=clean_input["contactEmail"],
            scoring_status=AsyncStatus.PENDING,
        )
        try:
            publish_lead_created(lead_obj)
        except Exception as error:
            logger.exception("publish_lead_created_failed", extra={"lead_id": str(lead_obj.id)})
            raise GraphQLError("Failed to queue the lead workflow. Please try again.") from error

    return lead_obj


@mutation.field("applyLeadWorkflowResult")
def resolve_apply_workflow_result(_obj, info, input):
    _require_internal_token(info)
    lead_obj = Lead.objects.filter(id=input["leadId"]).first()
    if not lead_obj:
        raise GraphQLError("Lead not found.")

    mark_failed = input.get("markFailed") or False
    if mark_failed and not input.get("failureReason"):
        raise GraphQLError("Failure reason is required when markFailed is true.")
    if not mark_failed and input.get("score") is None:
        raise GraphQLError("Score is required unless the workflow is marked failed.")
    lead_obj.score = None if mark_failed else input.get("score")
    lead_obj.scoring_status = AsyncStatus.FAILED if mark_failed else AsyncStatus.COMPLETED
    lead_obj.save(update_fields=["score", "scoring_status", "updated_at"])

    activity_kind = ActivityKind.WORKFLOW_ERROR if mark_failed else ActivityKind.FOLLOW_UP
    note = input.get("failureReason") if mark_failed else input["followUpNote"]
    Activity.objects.update_or_create(
        workflow_event_id=input["eventId"],
        defaults={
            "lead": lead_obj,
            "company_id": lead_obj.company_id,
            "kind": activity_kind,
            "note": note,
        },
    )
    return lead_obj


@lead.reference_resolver
def resolve_lead_reference(_obj, _info, representation):
    return Lead.objects.filter(id=representation["id"]).first()


@lead.field("company")
def resolve_lead_company(obj, *_args):
    return {"id": str(obj.company_id)}


@lead.field("createdBy")
def resolve_lead_created_by(obj, *_args):
    return {"id": str(obj.created_by_user_id)}


@lead.field("contactName")
def resolve_contact_name(obj, *_args):
    return obj.contact_name


@lead.field("contactEmail")
def resolve_contact_email(obj, *_args):
    return obj.contact_email


@lead.field("scoringStatus")
def resolve_scoring_status(obj, *_args):
    return obj.scoring_status


@lead.field("createdAt")
def resolve_created_at(obj, *_args):
    return obj.created_at.isoformat()


@lead.field("updatedAt")
def resolve_updated_at(obj, *_args):
    return obj.updated_at.isoformat()


@lead.field("activities")
def resolve_lead_activities(obj, *_args):
    activities = getattr(obj, "activities", None)
    if hasattr(activities, "all"):
        return activities.all()
    return Activity.objects.filter(lead=obj)


@activity.reference_resolver
def resolve_activity_reference(_obj, _info, representation):
    return Activity.objects.select_related("lead").filter(id=representation["id"]).first()


@activity.field("lead")
def resolve_activity_lead(obj, *_args):
    return obj.lead


@activity.field("createdAt")
def resolve_activity_created_at(obj, *_args):
    return obj.created_at.isoformat()


@deal.reference_resolver
def resolve_deal_reference(_obj, _info, representation):
    return Deal.objects.filter(id=representation["id"]).first()


@deal.field("valueCents")
def resolve_value_cents(obj, *_args):
    return obj.value_cents


schema = make_federated_schema(type_defs, [query, mutation, lead, activity, deal])
