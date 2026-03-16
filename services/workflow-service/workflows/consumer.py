import json
import os
import time

import structlog
from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic

from workflows.crm_client import apply_workflow_result
from workflows.handler import LeadCreatedHandler
from workflows.store import DjangoStateStore

structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger("workflow-service")


def _consumer():
    return Consumer(
        {
            "bootstrap.servers": os.getenv("KAFKA_BROKER", "localhost:29092"),
            "group.id": "workflow-service",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def _producer():
    return Producer({"bootstrap.servers": os.getenv("KAFKA_BROKER", "localhost:29092")})


def _admin_client():
    return AdminClient({"bootstrap.servers": os.getenv("KAFKA_BROKER", "localhost:29092")})


def _send_to_dlq(producer, payload, error_message, retry_count):
    topic = os.getenv("KAFKA_TOPIC_LEAD_CREATED_DLQ", "crm.lead.created.dlq")
    message = json.dumps(
        {
            "payload": payload,
            "error": error_message,
            "retryCount": retry_count,
        }
    ).encode("utf-8")
    producer.produce(topic, message)
    producer.flush(5)
    logger.warning(
        "event_sent_to_dlq",
        topic=topic,
        eventId=payload["eventId"],
        leadId=payload["leadId"],
        retryCount=retry_count,
    )


def _duration_ms(start_time):
    return int((time.perf_counter() - start_time) * 1000)


def _workflow_retry_config():
    max_retries = max(1, int(os.getenv("WORKFLOW_MAX_RETRIES", "3")))
    base_delay_seconds = max(0.0, float(os.getenv("WORKFLOW_RETRY_BASE_DELAY_SECONDS", "1")))
    return max_retries, base_delay_seconds


def _process_event_with_retries(handler, payload, max_retries, base_delay_seconds):
    event_id = payload["eventId"]
    lead_id = payload["leadId"]

    for attempt in range(1, max_retries + 1):
        started_at = time.perf_counter()
        try:
            result = handler.handle(payload)
            logger.info(
                "workflow_processed",
                eventId=event_id,
                leadId=lead_id,
                attempt=attempt,
                maxAttempts=max_retries,
                durationMs=_duration_ms(started_at),
                result=result,
            )
            return result
        except Exception as error:
            will_retry = attempt < max_retries
            logger.warning(
                "workflow_attempt_failed",
                eventId=event_id,
                leadId=lead_id,
                attempt=attempt,
                maxAttempts=max_retries,
                durationMs=_duration_ms(started_at),
                error=str(error),
                willRetry=will_retry,
            )
            if not will_retry:
                raise
            time.sleep(base_delay_seconds * (2 ** (attempt - 1)))


def _ensure_topics():
    topic_names = [
        os.getenv("KAFKA_TOPIC_LEAD_CREATED", "crm.lead.created"),
        os.getenv("KAFKA_TOPIC_LEAD_CREATED_DLQ", "crm.lead.created.dlq"),
    ]

    attempt = 0
    while True:
        attempt += 1
        try:
            admin_client = _admin_client()
            metadata = admin_client.list_topics(timeout=10)
            missing_topics = [topic for topic in topic_names if topic not in metadata.topics]
            if missing_topics:
                futures = admin_client.create_topics(
                    [NewTopic(topic=topic, num_partitions=1, replication_factor=1) for topic in missing_topics]
                )
                for topic, future in futures.items():
                    try:
                        future.result(10)
                        logger.info("topic_created", topic=topic)
                    except Exception as error:
                        if "TOPIC_ALREADY_EXISTS" not in str(error):
                            raise
            logger.info("topics_ready", topics=topic_names)
            return
        except Exception as error:
            logger.warning("topic_setup_retry", attempt=attempt, error=str(error))
            time.sleep(2)


def poll_forever():
    _ensure_topics()
    consumer = _consumer()
    producer = _producer()
    handler = LeadCreatedHandler(DjangoStateStore(), apply_workflow_result, logger)
    max_retries, base_delay_seconds = _workflow_retry_config()

    topic = os.getenv("KAFKA_TOPIC_LEAD_CREATED", "crm.lead.created")
    consumer.subscribe([topic])
    logger.info(
        "consumer_started",
        topic=topic,
        maxRetries=max_retries,
        retryBaseDelaySeconds=base_delay_seconds,
    )

    while True:
        message = consumer.poll(1.0)
        if message is None:
            continue
        if message.error():
            logger.error("kafka_error", error=str(message.error()))
            time.sleep(1)
            continue

        payload = json.loads(message.value().decode("utf-8"))
        overall_started_at = time.perf_counter()
        logger.info("event_received", eventId=payload["eventId"], leadId=payload["leadId"])
        try:
            _process_event_with_retries(handler, payload, max_retries, base_delay_seconds)
            consumer.commit(message=message)
        except Exception as error:
            logger.error(
                "workflow_failed",
                eventId=payload["eventId"],
                leadId=payload["leadId"],
                error=str(error),
                totalDurationMs=_duration_ms(overall_started_at),
                maxAttempts=max_retries,
            )
            try:
                handler.handle_failure(payload, str(error))
            except Exception as followup_error:
                logger.error("crm_failure_mark_failed", eventId=payload["eventId"], error=str(followup_error))
            _send_to_dlq(producer, payload, str(error), max_retries)
            consumer.commit(message=message)
