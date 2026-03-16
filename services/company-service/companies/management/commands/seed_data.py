import json
from pathlib import Path

from django.core.management.base import BaseCommand

from companies.models import Company


class Command(BaseCommand):
    help = "Seed the company service with demo companies."

    def handle(self, *_args, **_options):
        seed_path = Path(__file__).resolve().parents[5] / "libs" / "contracts" / "seed-data.json"
        payload = json.loads(seed_path.read_text())

        ordered = ["parent", "childA", "childB"]
        for key in ordered:
            company = payload["companies"][key]
            Company.objects.update_or_create(
                id=company["id"],
                defaults={
                    "name": company["name"],
                    "company_type": company["companyType"],
                    "parent_id": company["parentId"],
                },
            )

        self.stdout.write(self.style.SUCCESS("Seeded company data"))
