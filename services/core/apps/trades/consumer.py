import json
import logging
from decimal import Decimal
from kafka import KafkaConsumer
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.conf import settings

from .models import Lot, Trade, ProcessedEvent

logger = logging.getLogger("trades.consumer")

KAFKA_BROKERS = getattr(settings, "KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
TOPIC = getattr(settings, "KAFKA_TOPIC_TRADE_PROFIT", "trade.profit.detected")
GROUP_ID = "django-trade-consumer"


def process_message(event: dict):
    event_id = event.get("event_id")
    lot_id = event.get("lot_id")
    logger.info("Processing event %s for lot %s", event_id, lot_id)

    if not event_id:
        logger.warning("Event without event_id, skipping: %s", event)
        return

    with transaction.atomic():
        try:
            ProcessedEvent.objects.create(event_id=event_id)
        except IntegrityError:
            logger.info("Event %s already processed, skipping", event_id)
            return

        try:
            lot = (
                Lot.objects
                .select_for_update()
                .only("id", "remaining_amount", "profile", "exchange", "symbol")
                .get(id=lot_id)
            )
        except Lot.DoesNotExist:
            logger.warning("PurchaseLot %s not found, skipping", lot_id)
            return

        amount_requested = Decimal(str(event.get("amount", "0")))
        available = lot.remaining_amount or Decimal("0")
        sell_amount = min(amount_requested, available)

        if sell_amount <= 0:
            logger.info("Nothing to sell for lot %s (available=%s)", lot_id, available)
            return

        price = Decimal(str(event.get("price", "0")))
        profit = Decimal(str(event.get("profit", "0")))

        trade = Trade.objects.create(
            profile=lot.profile,
            exchange=lot.exchange,
            symbol=lot.symbol,
            side=Trade.Side.SELL,
            amount=sell_amount,
            price=price,
            profit=profit,
            timestamp=timezone.now(),
            purchase_lot=lot
        )

        lot.remaining_amount = available - sell_amount
        lot.save(update_fields=["remaining_amount"])

        logger.info(
            "Created SELL trade %s for lot %s; remaining %s",
            trade.id, lot_id, lot.remaining_amount
        )


def run_consumer():
    logger.info("Starting Kafka consumer for topic %s", TOPIC)
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=["127.0.0.1:9092"],
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id=GROUP_ID,
    )

    for msg in consumer:
        event = msg.value
        try:
            process_message(event)
            consumer.commit()
        except Exception as e:
            logger.exception("Error while processing event %s: %s", event, e)
