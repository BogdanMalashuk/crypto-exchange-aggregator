import json
from aiokafka import AIOKafkaProducer

producer: AIOKafkaProducer | None = None


async def start_kafka(app):
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()
    app.state.kafka_producer = producer


async def stop_kafka(app):
    global producer
    if producer:
        await producer.stop()


async def publish_event(topic: str, event: dict, key: str | None = None):
    if not producer:
        raise RuntimeError("Kafka producer is not initialized")
    await producer.send_and_wait(topic, event, key=key.encode("utf-8") if key else None)
