import json
from pathlib import Path

from django.core.management.base import BaseCommand

from authz.models import Membership, User


class Command(BaseCommand):
    help = "Seed the auth service with demo users and memberships."

    def handle(self, *_args, **_options):
        seed_path = Path(__file__).resolve().parents[5] / "libs" / "contracts" / "seed-data.json"
        payload = json.loads(seed_path.read_text())

        for user_payload in payload["users"].values():
            User.objects.update_or_create(
                id=user_payload["id"],
                defaults={
                    "full_name": user_payload["fullName"],
                    "email": user_payload["email"],
                },
            )

        for membership_payload in payload["memberships"]:
            Membership.objects.update_or_create(
                user_id=membership_payload["userId"],
                company_id=membership_payload["companyId"],
                role=membership_payload["role"],
                defaults={},
            )

        self.stdout.write(self.style.SUCCESS("Seeded auth data"))
