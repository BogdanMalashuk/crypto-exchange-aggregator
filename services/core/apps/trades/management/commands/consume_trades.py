import json
import logging
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from kafka import KafkaConsumer
from apps.trades.models import Trade, Sale
from apps.trades.exchanges.binance_order import create_sell_order

logger = logging.getLogger("core.kafka_consumer")

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "trade.profit.detected"
GROUP_ID = "trade_profit_consumer_group"


class Command(BaseCommand):
    help = "Consume trade profit events from Kafka"

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            group_id=GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        logger.info("Started Kafka consumer for %s", TOPIC)

        for message in consumer:
            try:
                data = message.value
                trade_id = data.get("trade_id")
                current_price = data.get("current_price")

                if not trade_id or current_price is None:
                    logger.warning("Invalid message: %s", data)
                    continue

                sell_price = Decimal(str(current_price))

                with transaction.atomic():
                    try:
                        trade = Trade.objects.select_for_update().get(id=trade_id)
                    except Trade.DoesNotExist:
                        logger.warning("Trade %s not found", trade_id)
                        continue

                    if trade.sold:
                        logger.info("Trade %s already sold", trade_id)
                        continue

                    quantity = trade.quantity
                    buy_price = trade.buy_price

                    try:
                        create_sell_order(trade.symbol, quantity)
                        logger.info("Created sell order for trade %s", trade_id)
                    except Exception as e:
                        logger.error("Sell order failed for %s: %s", trade_id, e)
                        continue

                    profit = (sell_price - buy_price) * quantity

                    Sale.objects.create(
                        trade=trade,
                        quantity=quantity,
                        sell_price=sell_price,
                        profit=profit
                    )

                    trade.sold = True
                    trade.sold_at = timezone.now()
                    trade.save(update_fields=["sold", "sold_at"])

                logger.info("Processed trade %s", trade_id)

            except Exception as e:
                logger.exception("Error processing message: %s", e)
