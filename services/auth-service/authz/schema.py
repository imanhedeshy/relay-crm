import os

from django.db.models import Prefetch

from ariadne import ObjectType, QueryType
from ariadne.contrib.federation import FederatedObjectType, make_federated_schema
from graphql import GraphQLError

from authz.models import Membership, User

type_defs = """
    enum UserRole {
      PARENT_ADMIN
      CHILD_MANAGER
      SALES_REP
      VIEWER
    }

    type Membership {
      id: ID!
      companyId: ID!
      role: UserRole!
    }

    type User @key(fields: "id") {
      id: ID!
      fullName: String!
      email: String!
      memberships: [Membership!]!
    }

    type AccessContext {
      userId: ID!
      fullName: String!
      memberships: [Membership!]!
    }

    type Query {
      viewer: User
      users: [User!]!
      user(id: ID!): User
      accessContext(userId: ID): AccessContext
    }
"""

query = QueryType()
user = FederatedObjectType("User")
membership = ObjectType("Membership")
access_context = ObjectType("AccessContext")


def _current_user_id(info):
    request = info.context
    return request.headers.get("x-user-id")


def _require_internal_token(info):
    provided_token = info.context.headers.get("x-internal-token")
    expected_token = os.getenv("INTERNAL_SERVICE_TOKEN", "relay-internal-token")
    if not provided_token or provided_token != expected_token:
        raise GraphQLError("Internal service token required.")


@query.field("viewer")
def resolve_viewer(_obj, info):
    user_id = _current_user_id(info)
    if not user_id:
        return None
    return User.objects.prefetch_related("memberships").filter(id=user_id).first()


@query.field("users")
def resolve_users(*_args):
    return User.objects.prefetch_related("memberships").all()


@query.field("user")
def resolve_user(*_args, id):
    return User.objects.prefetch_related("memberships").filter(id=id).first()


@query.field("accessContext")
def resolve_access_context(_obj, info, userId=None):
    current_user_id = _current_user_id(info)
    target_user_id = userId or current_user_id
    if not target_user_id:
        return None
    if userId and userId != current_user_id:
        _require_internal_token(info)
    target = (
        User.objects.prefetch_related(Prefetch("memberships", queryset=Membership.objects.order_by("role", "company_id")))
        .filter(id=target_user_id)
        .first()
    )
    if not target:
        return None
    return {
        "userId": str(target.id),
        "fullName": target.full_name,
        "memberships": list(target.memberships.all()),
    }


@user.reference_resolver
def resolve_user_reference(_, _info, representation):
    return User.objects.prefetch_related("memberships").filter(id=representation["id"]).first()


@user.field("fullName")
def resolve_full_name(obj, *_args):
    return obj.full_name


@user.field("memberships")
def resolve_memberships(obj, *_args):
    memberships = getattr(obj, "memberships", None)
    if hasattr(memberships, "all"):
        return memberships.all()
    return Membership.objects.filter(user=obj)


@membership.field("companyId")
def resolve_membership_company(obj, *_args):
    return str(obj.company_id)


@access_context.field("fullName")
def resolve_access_context_name(obj, *_args):
    return obj["fullName"]


schema = make_federated_schema(type_defs, [query, user, membership, access_context])
