import json
import uuid
from pathlib import Path

from django.core.management.base import BaseCommand

from crm.models import Activity, Deal, Lead


class Command(BaseCommand):
    help = "Seed the CRM service with demo leads, activities, and deals."

    def handle(self, *_args, **_options):
        seed_path = Path(__file__).resolve().parents[5] / "libs" / "contracts" / "seed-data.json"
        payload = json.loads(seed_path.read_text())["crm"]

        for lead_payload in payload["leads"]:
            Lead.objects.update_or_create(
                id=lead_payload["id"],
                defaults={
                    "company_id": lead_payload["companyId"],
                    "created_by_user_id": lead_payload["createdByUserId"],
                    "title": lead_payload["title"],
                    "contact_name": lead_payload["contactName"],
                    "contact_email": lead_payload["contactEmail"],
                    "status": lead_payload["status"],
                    "scoring_status": lead_payload["scoringStatus"],
                    "score": lead_payload["score"],
                },
            )

        for activity_payload in payload["activities"]:
            lead_obj = Lead.objects.get(id=activity_payload["leadId"])
            Activity.objects.get_or_create(
                lead=lead_obj,
                kind=activity_payload["kind"],
                note=activity_payload["note"],
                defaults={
                    "company_id": activity_payload["companyId"],
                },
            )

        for deal_payload in payload["deals"]:
            Deal.objects.get_or_create(
                company_id=deal_payload["companyId"],
                name=deal_payload["name"],
                defaults={
                    "stage": deal_payload["stage"],
                    "value_cents": deal_payload["valueCents"],
                },
            )

        self.stdout.write(self.style.SUCCESS("Seeded CRM data"))
