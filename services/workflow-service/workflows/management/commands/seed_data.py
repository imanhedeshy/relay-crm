from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Workflow service does not need seed data."

    def handle(self, *_args, **_options):
        self.stdout.write(self.style.SUCCESS("Workflow seed skipped"))
