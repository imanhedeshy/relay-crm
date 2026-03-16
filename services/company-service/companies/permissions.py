from companies.models import Company
from companies.service_clients import fetch_access_context


def descendant_ids(start_company_id: str):
    seen = set()
    frontier = [start_company_id]

    while frontier:
        current = frontier.pop(0)
        if current in seen:
            continue
        seen.add(current)
        children = Company.objects.filter(parent_id=current).values_list("id", flat=True)
        frontier.extend(str(child_id) for child_id in children)

    return seen


def visible_company_ids_for_user(user_id: str):
    context = fetch_access_context(user_id)
    if not context:
        return set()
    visible = set()

    for membership in context["memberships"]:
        role = membership["role"]
        company_id = membership["companyId"]
        if role == "PARENT_ADMIN":
            visible.update(descendant_ids(company_id))
        else:
            visible.add(company_id)

    return visible
