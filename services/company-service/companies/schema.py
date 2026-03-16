from ariadne import ObjectType, QueryType
from ariadne.contrib.federation import FederatedObjectType, make_federated_schema

from companies.models import Company
from companies.permissions import visible_company_ids_for_user

type_defs = """
    enum CompanyType {
      PARENT
      CHILD
    }

    type Company @key(fields: "id") {
      id: ID!
      name: String!
      companyType: CompanyType!
      parentId: ID
      parent: Company
      children: [Company!]!
    }

    type Query {
      companies: [Company!]!
      company(id: ID!): Company
    }
"""

query = QueryType()
company = FederatedObjectType("Company")


def _visible_company_ids(info):
    user_id = info.context.headers.get("x-user-id")
    if not user_id:
        return set()
    return visible_company_ids_for_user(user_id)


@query.field("companies")
def resolve_companies(_obj, info):
    visible_ids = _visible_company_ids(info)
    if not visible_ids:
        return []
    return Company.objects.filter(id__in=visible_ids).order_by("company_type", "name")


@query.field("company")
def resolve_company(_obj, info, id):
    visible_ids = _visible_company_ids(info)
    if id not in visible_ids:
        return None
    return Company.objects.filter(id=id).first()


@company.reference_resolver
def resolve_company_reference(_obj, info, representation):
    visible_ids = _visible_company_ids(info)
    company_id = representation["id"]
    if company_id not in visible_ids:
        return None
    return Company.objects.filter(id=company_id).first()


@company.field("companyType")
def resolve_company_type(obj, *_args):
    return obj.company_type


@company.field("parentId")
def resolve_parent_id(obj, *_args):
    return str(obj.parent_id) if obj.parent_id else None


@company.field("children")
def resolve_children(obj, info, *_args):
    visible_ids = _visible_company_ids(info)
    return Company.objects.filter(parent=obj, id__in=visible_ids).order_by("name")


@company.field("parent")
def resolve_parent(obj, info, *_args):
    visible_ids = _visible_company_ids(info)
    if obj.parent_id and str(obj.parent_id) in visible_ids:
        return obj.parent
    return None


schema = make_federated_schema(type_defs, [query, company])
