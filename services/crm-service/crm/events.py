import json
import logging
import os
from datetime import datetime, timezone
from functools import lru_cache
from uuid import uuid4

from confluent_kafka import Producer

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def kafka_producer():
    return Producer({"bootstrap.servers": os.getenv("KAFKA_BROKER", "localhost:29092")})


def publish_lead_created(lead):
    event = {
        "eventType": "LeadCreated",
        "eventId": str(uuid4()),
        "leadId": str(lead.id),
        "companyId": str(lead.company_id),
        "createdByUserId": str(lead.created_by_user_id),
        "occurredAt": datetime.now(timezone.utc).isoformat(),
        "version": 1,
    }
    producer = kafka_producer()
    producer.produce(os.getenv("KAFKA_TOPIC_LEAD_CREATED", "crm.lead.created"), json.dumps(event).encode("utf-8"))
    producer.flush(5)
    logger.info(json.dumps({"message": "published lead created event", "eventId": event["eventId"], "leadId": event["leadId"]}))
    return event["eventId"]
