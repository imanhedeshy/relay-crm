READ_ROLES = {"PARENT_ADMIN", "CHILD_MANAGER", "SALES_REP", "VIEWER"}
WRITE_ROLES = {"PARENT_ADMIN", "CHILD_MANAGER", "SALES_REP"}


class AuthorizationError(Exception):
    pass


def authorize_company_access(access_context, visible_companies, company_id: str, allowed_roles):
    company_type = visible_companies.get(company_id)
    if company_type != "CHILD":
        raise AuthorizationError("Requested company is outside the allowed child-company scope.")

    for membership in access_context["memberships"]:
        if membership["role"] not in allowed_roles:
            continue
        if membership["role"] == "PARENT_ADMIN" and company_id in visible_companies:
            return
        if membership["companyId"] == company_id:
            return

    raise AuthorizationError("You do not have permission to access this company.")
