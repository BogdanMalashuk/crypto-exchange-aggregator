import json
import logging
from kafka import KafkaProducer

logger = logging.getLogger(__name__)

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def send_kafka_event(topic: str, event: dict):
    try:
        producer.send(topic, event)
        producer.flush()
        logger.info(f"Sent event to {topic}: {event}")
    except Exception as e:
        logger.exception(f"Failed to send Kafka event: {e}")
