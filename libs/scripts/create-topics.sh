#!/usr/bin/env sh
set -eu

kafka-topics --bootstrap-server "${KAFKA_BROKER:-kafka:9092}" --create --if-not-exists --topic "${KAFKA_TOPIC_LEAD_CREATED:-crm.lead.created}"
kafka-topics --bootstrap-server "${KAFKA_BROKER:-kafka:9092}" --create --if-not-exists --topic "${KAFKA_TOPIC_LEAD_CREATED_DLQ:-crm.lead.created.dlq}"
