import asyncio
import logging
from decimal import Decimal
from typing import Dict, Optional
import aiohttp

logger = logging.getLogger("gateway.price_cache")

BINANCE_REST_BASE = "https://api.binance.com/api/v3/ticker/price"
UPDATE_INTERVAL = 30  # сек


class PriceCache:
    def __init__(self, symbols: list[str] = None):
        self._prices: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self.symbols = [s.upper() for s in symbols] if symbols else []

    async def start(self):
        """Запуск фонового обновления цен через REST"""
        if not self._task:
            self._task = asyncio.create_task(self._update_prices_rest())
            logger.info("PriceCache updater started")

    async def stop(self):
        """Остановка фонового обновления"""
        self._running = False
        if self._task:
            await self._task
            self._task = None
            logger.info("PriceCache updater stopped")

    async def _update_prices_rest(self):
        """Фоновая задача обновления цен с Binance REST API"""
        self._running = True
        while self._running:
            try:
                if not self.symbols:
                    await asyncio.sleep(UPDATE_INTERVAL)
                    continue

                async with aiohttp.ClientSession() as session:
                    for symbol in self.symbols:
                        url = f"{BINANCE_REST_BASE}?symbol={symbol}"
                        try:
                            async with session.get(url, timeout=10) as resp:
                                if resp.status != 200:
                                    logger.warning("Failed to fetch price for %s: %s", symbol, resp.status)
                                    continue
                                data = await resp.json()
                                price = float(data.get("price", 0))
                                if price > 0:
                                    await self.set_price(symbol, price)
                                    logger.debug("Updated %s price via REST: %s", symbol, price)
                        except Exception as e:
                            logger.error("Error fetching price for %s: %s", symbol, e)

                await asyncio.sleep(UPDATE_INTERVAL)

            except Exception as e:
                logger.exception("PriceCache REST updater error: %s", e)
                await asyncio.sleep(5)

    async def set_price(self, symbol: str, price: float):
        """Установить цену в кэш"""
        symbol = symbol.upper()
        async with self._lock:
            self._prices[symbol] = {"price": Decimal(str(price))}

    async def get_price(self, symbol: str, wait_if_missing: bool = True) -> Optional[Decimal]:
        """
        Получить цену из кэша.
        Если wait_if_missing=True и цены нет, ждём до 1 секунды, чтобы REST успел обновить.
        """
        symbol = symbol.upper()
        async with self._lock:
            item = self._prices.get(symbol)
            if item:
                return item["price"]

        if wait_if_missing:
            await asyncio.sleep(0.5)
            async with self._lock:
                item = self._prices.get(symbol)
                if item:
                    return item["price"]
        return None


# Глобальный кэш цен
price_cache = PriceCache()
