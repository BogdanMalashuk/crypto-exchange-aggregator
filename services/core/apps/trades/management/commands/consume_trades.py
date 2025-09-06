import asyncio
import json
import logging
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from aiokafka import AIOKafkaConsumer
from apps.trades.models import Trade, Sale
from apps.trades.exchanges.binance_order import create_sell_order

logger = logging.getLogger("core.kafka_consumer")

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "trade.profit.detected"
GROUP_ID = "trade_profit_consumer_group"


class Command(BaseCommand):
    help = "Consume trade profit events from Kafka (async, thread-safe DB + external call)"

    def handle(self, *args, **options):
        # Запускаем async loop
        asyncio.run(self.consume())

    async def consume(self):
        consumer = AIOKafkaConsumer(
            TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=False,  # ручной коммит после успешной обработки
        )
        await consumer.start()
        logger.info("Started async Kafka consumer for %s", TOPIC)

        try:
            async for msg in consumer:
                data = msg.value
                try:
                    processed = await self.process_message(data)
                except Exception as e:
                    logger.exception("Unhandled error processing message: %s", e)
                    processed = False

                if processed:
                    try:
                        # commit offsets only after successful processing
                        await consumer.commit()
                    except Exception as e:
                        logger.error("Failed to commit offsets: %s", e)
        finally:
            await consumer.stop()
            logger.info("Kafka consumer stopped")

    async def process_message(self, data) -> bool:
        """
        Основная асинхронная обёртка: парсим данные, выполняем
        синхронную work (DB + вызов биржи) в thread через asyncio.to_thread.
        Возвращаем True при успешной обработке (тогда коммитим оффсет).
        """
        trade_id = data.get("trade_id")
        symbol = data.get("symbol")
        quantity_str = data.get("quantity")
        buy_price_str = data.get("buy_price")
        current_price_str = data.get("current_price")

        if not trade_id or not symbol or not quantity_str or not buy_price_str or not current_price_str:
            logger.warning("Invalid message: %s", data)
            return False

        try:
            quantity = Decimal(quantity_str)
            buy_price = Decimal(buy_price_str)
            sell_price = Decimal(current_price_str)
        except (InvalidOperation, TypeError) as e:
            logger.error("Decimal conversion error: %s, data: %s", e, data)
            return False

        if quantity <= 0:
            logger.info("Quantity <= 0, skipping trade %s", trade_id)
            return False

        # Выполним всю "тяжёлую" синхронную логику в отдельном потоке:
        try:
            result = await asyncio.to_thread(
                self._process_db_and_create_order,
                trade_id, symbol, quantity, buy_price, sell_price
            )
            return result
        except Exception as e:
            logger.exception("Error in threaded processing for trade %s: %s", trade_id, e)
            return False

    def _process_db_and_create_order(self, trade_id, symbol, quantity, buy_price, sell_price) -> bool:
        """
        Синхронный код: выполняется в отдельном потоке (через to_thread).
        Использует transaction.atomic и Django ORM как раньше.
        Возвращает True если успешно создали ордер и записали Sale + пометили trade как sold.
        """
        try:
            with transaction.atomic():
                try:
                    trade = Trade.objects.select_for_update().get(id=trade_id)
                except Trade.DoesNotExist:
                    logger.warning("Trade %s not found", trade_id)
                    return False

                if trade.sold:
                    logger.info("Trade %s already sold", trade_id)
                    return False

                try:
                    order = create_sell_order(symbol, float(quantity))
                    logger.info("Binance sell order created for trade %s: %s", trade_id, order)
                except Exception as e:
                    logger.error("Sell order failed for trade %s: %s", trade_id, e, exc_info=True)
                    return False

                profit = (sell_price - buy_price) * quantity
                Sale.objects.create(
                    trade=trade,
                    quantity=quantity,
                    sell_price=sell_price,
                    profit=profit,
                )

                trade.sold = True
                trade.sold_at = timezone.now()
                trade.save(update_fields=["sold", "sold_at"])

            logger.info("Processed and sold trade %s", trade_id)
            return True

        except Exception as e:
            logger.exception("DB/threaded processing error for trade %s: %s", trade_id, e)
            return False
