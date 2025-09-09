import json
import logging
from kafka import KafkaConsumer
from django.conf import settings
import redis

logger = logging.getLogger(__name__)


class BaseKafkaConsumer:
    def __init__(self, topics, group_id=None, bootstrap_servers=None):
        self.topics = topics if isinstance(topics, list) else [topics]
        self.group_id = group_id or settings.KAFKA_GROUP_ID
        self.bootstrap_servers = bootstrap_servers or settings.KAFKA_BOOTSTRAP_SERVERS.split(",")
        self.redis = redis.from_url(settings.REDIS_URL)
        self.consumer = KafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            enable_auto_commit=False,
            auto_offset_reset=settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
            value_deserializer=lambda b: json.loads(b.decode("utf-8"))
        )
        self.idempotency_ttl = settings.KAFKA_IDEMPOTENCY_TTL

    def is_processed(self, event_id: str) -> bool:
        if not event_id:
            return False
        key = f"kafka:processed:{event_id}"
        return self.redis.exists(key)

    def mark_processed(self, event_id: str):
        if not event_id:
            return
        key = f"kafka:processed:{event_id}"
        self.redis.set(key, 1, ex=self.idempotency_ttl)

    def publish_to_dlq(self, message_value):
        logger.error("Publishing to DLQ: %s", message_value)

    def handle_message(self, message):
        raise NotImplementedError()

    def run(self):
        logger.info("Starting consumer for topics: %s", self.topics)
        try:
            for msg in self.consumer:
                try:
                    payload = msg.value
                    event_id = payload.get("event_id") or payload.get("external_id")
                    if self.is_processed(event_id):
                        logger.debug("Skipping already processed event %s", event_id)
                        self.consumer.commit()
                        continue

                    self.handle_message(payload)
                    self.mark_processed(event_id)
                    self.consumer.commit()
                except Exception as e:
                    logger.exception("Error handling kafka message: %s", e)
                    self.publish_to_dlq(msg.value)
                    self.consumer.commit()
        finally:
            logger.info("Closing consumer")
            self.consumer.close()
