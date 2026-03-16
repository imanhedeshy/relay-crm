import uuid
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase
from graphql import GraphQLError

from crm.models import Lead
from crm.permissions import AuthorizationError, READ_ROLES, WRITE_ROLES, authorize_company_access
from crm.schema import resolve_create_lead


class AuthorizationTests(TestCase):
    def setUp(self):
        self.visible_companies = {
            "22222222-2222-4222-8222-222222222222": "CHILD",
            "33333333-3333-4333-8333-333333333333": "CHILD",
            "11111111-1111-4111-8111-111111111111": "PARENT",
        }

    def test_parent_admin_can_access_child_company(self):
        authorize_company_access(
            {"memberships": [{"companyId": "11111111-1111-4111-8111-111111111111", "role": "PARENT_ADMIN"}]},
            self.visible_companies,
            "22222222-2222-4222-8222-222222222222",
            READ_ROLES,
        )

    def test_child_manager_cannot_access_sibling_company(self):
        with self.assertRaises(AuthorizationError):
            authorize_company_access(
                {"memberships": [{"companyId": "22222222-2222-4222-8222-222222222222", "role": "CHILD_MANAGER"}]},
                self.visible_companies,
                "33333333-3333-4333-8333-333333333333",
                READ_ROLES,
            )

    def test_viewer_cannot_mutate(self):
        with self.assertRaises(AuthorizationError):
            authorize_company_access(
                {"memberships": [{"companyId": "22222222-2222-4222-8222-222222222222", "role": "VIEWER"}]},
                self.visible_companies,
                "22222222-2222-4222-8222-222222222222",
                WRITE_ROLES,
            )


class CreateLeadMutationTests(TestCase):
    def setUp(self):
        self.company_id = uuid.UUID("22222222-2222-4222-8222-222222222222")
        self.user_id = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
        self.info = SimpleNamespace(context=SimpleNamespace(headers={"x-user-id": str(self.user_id)}))

    @patch("crm.schema.publish_lead_created")
    @patch("crm.schema._resolve_access")
    def test_create_lead_rejects_exact_duplicate_in_same_company(self, resolve_access_mock, publish_lead_created_mock):
        resolve_access_mock.return_value = ({}, {})
        Lead.objects.create(
            company_id=self.company_id,
            created_by_user_id=self.user_id,
            title="Submit Check",
            contact_name="Submission Check",
            contact_email="submit-check@example.com",
        )

        with self.assertRaisesMessage(
            GraphQLError,
            "A lead with this title and contact email already exists in the selected company.",
        ):
            resolve_create_lead(
                None,
                self.info,
                {
                    "companyId": str(self.company_id),
                    "title": "  submit check  ",
                    "contactName": "Another Contact",
                    "contactEmail": "SUBMIT-CHECK@example.com",
                },
            )

        publish_lead_created_mock.assert_not_called()
        self.assertEqual(Lead.objects.count(), 1)

    @patch("crm.schema.publish_lead_created")
    @patch("crm.schema._resolve_access")
    def test_create_lead_normalizes_trimmed_input_before_persisting(self, resolve_access_mock, publish_lead_created_mock):
        resolve_access_mock.return_value = ({}, {})

        created = resolve_create_lead(
            None,
            self.info,
            {
                "companyId": str(self.company_id),
                "title": "  Quarterly Renewal  ",
                "contactName": "  Jordan Rivera  ",
                "contactEmail": "  JORDAN@example.com  ",
            },
        )

        publish_lead_created_mock.assert_called_once()
        self.assertEqual(created.title, "Quarterly Renewal")
        self.assertEqual(created.contact_name, "Jordan Rivera")
        self.assertEqual(created.contact_email, "jordan@example.com")

    @patch("crm.schema.publish_lead_created", side_effect=RuntimeError("broker unavailable"))
    @patch("crm.schema._resolve_access")
    def test_create_lead_returns_generic_publish_error_and_rolls_back(self, resolve_access_mock, _publish_lead_created_mock):
        resolve_access_mock.return_value = ({}, {})

        with self.assertRaisesMessage(GraphQLError, "Failed to queue the lead workflow. Please try again."):
            resolve_create_lead(
                None,
                self.info,
                {
                    "companyId": str(self.company_id),
                    "title": "Quarterly Renewal",
                    "contactName": "Jordan Rivera",
                    "contactEmail": "jordan@example.com",
                },
            )

        self.assertEqual(Lead.objects.count(), 0)
