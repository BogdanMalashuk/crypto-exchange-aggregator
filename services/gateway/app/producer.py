import asyncio
import json
import logging
from aiokafka import AIOKafkaProducer

logger = logging.getLogger("gateway.kafka_producer")

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "trade.profit.detected"
MAX_RETRIES = 5
RETRY_BASE_DELAY = 1


class KafkaProducer:
    def __init__(self):
        self._producer = None
        self._lock = asyncio.Lock()

    async def start(self):
        async with self._lock:
            if self._producer is None:
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                await self._producer.start()
                logger.info("Kafka producer started")

    async def stop(self):
        async with self._lock:
            if self._producer:
                await self._producer.stop()
                self._producer = None
                logger.info("Kafka producer stopped")

    async def send_profit_trade_event(self, event: dict):
        if self._producer is None:
            await self.start()

        attempt = 0
        while attempt < MAX_RETRIES:
            try:
                await self._producer.send_and_wait(TOPIC, event)
                logger.info("Sent profit event to Kafka: %s", event)
                return
            except Exception as e:
                attempt += 1
                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))  # экспоненциальная задержка
                logger.warning("Failed to send Kafka event (attempt %d/%d): %s. Retrying in %.1f sec",
                               attempt, MAX_RETRIES, e, delay)
                await asyncio.sleep(delay)
        logger.error("Failed to send Kafka event after %d attempts: %s", MAX_RETRIES, event)


kafka_producer = KafkaProducer()


async def send_profit_trade_event(event: dict):
    await kafka_producer.send_profit_trade_event(event)
