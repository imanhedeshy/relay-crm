from types import SimpleNamespace

from django.test import TestCase
from graphql import GraphQLError

from authz.models import Membership, Role, User
from authz.schema import resolve_access_context


class AccessContextTests(TestCase):
    def test_user_memberships_are_loaded(self):
        user = User.objects.create(full_name="Test User", email="test@example.com")
        Membership.objects.create(user=user, company_id="11111111-1111-4111-8111-111111111111", role=Role.VIEWER)

        self.assertEqual(user.memberships.count(), 1)

    def test_access_context_rejects_cross_user_lookup_without_internal_token(self):
        viewer = User.objects.create(full_name="Viewer", email="viewer@example.com")
        target = User.objects.create(full_name="Target", email="target@example.com")
        info = SimpleNamespace(context=SimpleNamespace(headers={"x-user-id": str(viewer.id)}))

        with self.assertRaisesMessage(GraphQLError, "Internal service token required."):
            resolve_access_context(None, info, userId=str(target.id))

    def test_access_context_allows_internal_cross_user_lookup(self):
        viewer = User.objects.create(full_name="Viewer", email="viewer@example.com")
        target = User.objects.create(full_name="Target", email="target@example.com")
        Membership.objects.create(user=target, company_id="11111111-1111-4111-8111-111111111111", role=Role.CHILD_MANAGER)
        info = SimpleNamespace(
            context=SimpleNamespace(
                headers={
                    "x-user-id": str(viewer.id),
                    "x-internal-token": "relay-internal-token",
                }
            )
        )

        result = resolve_access_context(None, info, userId=str(target.id))

        self.assertEqual(result["userId"], str(target.id))
        self.assertEqual(len(result["memberships"]), 1)
