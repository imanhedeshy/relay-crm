from unittest.mock import patch

from django.test import TestCase

from companies.models import Company, CompanyType
from companies.permissions import visible_company_ids_for_user


class VisibilityTests(TestCase):
    def setUp(self):
        Company.objects.create(id="11111111-1111-4111-8111-111111111111", name="Parent", company_type=CompanyType.PARENT)
        Company.objects.create(
            id="22222222-2222-4222-8222-222222222222",
            name="Child A",
            company_type=CompanyType.CHILD,
            parent_id="11111111-1111-4111-8111-111111111111",
        )
        Company.objects.create(
            id="33333333-3333-4333-8333-333333333333",
            name="Child B",
            company_type=CompanyType.CHILD,
            parent_id="11111111-1111-4111-8111-111111111111",
        )

    @patch("companies.permissions.fetch_access_context")
    def test_parent_admin_sees_all_descendants(self, access_context):
        access_context.return_value = {
            "memberships": [
                {
                    "companyId": "11111111-1111-4111-8111-111111111111",
                    "role": "PARENT_ADMIN",
                }
            ]
        }

        visible = visible_company_ids_for_user("user-1")

        self.assertEqual(
            visible,
            {
                "11111111-1111-4111-8111-111111111111",
                "22222222-2222-4222-8222-222222222222",
                "33333333-3333-4333-8333-333333333333",
            },
        )

    @patch("companies.permissions.fetch_access_context")
    def test_child_user_is_scoped_to_own_company(self, access_context):
        access_context.return_value = {
            "memberships": [
                {
                    "companyId": "22222222-2222-4222-8222-222222222222",
                    "role": "CHILD_MANAGER",
                }
            ]
        }

        self.assertEqual(visible_company_ids_for_user("user-1"), {"22222222-2222-4222-8222-222222222222"})
