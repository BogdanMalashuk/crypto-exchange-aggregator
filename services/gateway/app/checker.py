import asyncio
import logging
from decimal import Decimal
from .price_cache import price_cache
from .producer import send_profit_trade_event
from .api_client import get_all_open_trades

logger = logging.getLogger("gateway.checker")

CHECK_INTERVAL = 10


class Checker:
    def __init__(self):
        self._task = None
        self._running = False

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def _fetch_open_trades(self):
        try:
            trades = await get_all_open_trades()
            return [t for t in trades if not t.get("sold")]
        except Exception as e:
            logger.error("Не удалось получить открытые трейды: %s", e)
            return []

    async def _run(self):
        self._running = True
        while self._running:
            try:
                trades = await self._fetch_open_trades()
                for trade in trades:
                    symbol = trade["symbol"]
                    quantity = Decimal(str(trade["quantity"]))
                    buy_price = Decimal(str(trade["buy_price"]))

                    current_price = await price_cache.get_price(symbol)
                    if current_price is None:
                        continue
                    current_price = Decimal(str(current_price))

                    if current_price > buy_price and quantity > 0:
                        event = {
                            "trade_id": trade["id"],
                            "user": trade["user"],
                            "symbol": symbol,
                            "quantity": str(quantity),
                            "buy_price": str(buy_price),
                            "current_price": str(current_price),
                        }
                        logger.info("Profit detected, publishing: %s", event)
                        await send_profit_trade_event(event)

                await asyncio.sleep(CHECK_INTERVAL)
            except Exception as e:
                logger.exception("Checker error: %s", e)
                await asyncio.sleep(5)

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None


checker = Checker()
