import json
import logging
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def send_kafka_event(topic: str, event: dict):
    try:
        producer.send(topic, event)
        producer.flush()
        logger.info(f"Sent event to {topic}: {event}")
    except Exception as e:
        logger.exception(f"Failed to send Kafka event: {e}")
