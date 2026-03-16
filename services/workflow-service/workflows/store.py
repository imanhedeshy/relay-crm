from django.utils import timezone

from workflows.models import ProcessedEvent, ProcessingStatus


class DjangoStateStore:
    def status(self, event_id):
        event = ProcessedEvent.objects.filter(event_id=event_id).first()
        return event.status if event else None

    def mark_processing(self, event_id, lead_id):
        event, _created = ProcessedEvent.objects.get_or_create(
            event_id=event_id,
            defaults={"lead_id": lead_id, "retry_count": 0},
        )
        event.lead_id = lead_id
        event.status = ProcessingStatus.PROCESSING
        event.retry_count += 1
        event.save(update_fields=["lead_id", "status", "retry_count", "updated_at"])

    def mark_completed(self, event_id):
        ProcessedEvent.objects.filter(event_id=event_id).update(
            status=ProcessingStatus.COMPLETED,
            processed_at=timezone.now(),
        )

    def mark_failed(self, event_id, error_message):
        ProcessedEvent.objects.filter(event_id=event_id).update(
            status=ProcessingStatus.FAILED,
            last_error=error_message,
        )
