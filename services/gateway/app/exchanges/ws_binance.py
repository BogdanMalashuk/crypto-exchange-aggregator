import asyncio
import json
import logging
import websockets
from urllib.parse import urlencode
from ..price_cache import price_cache

logger = logging.getLogger("gateway.binance")

BINANCE_WS_BASE = 'wss://stream.binance.com:9443/stream'


class BinanceWSClient:
    def __init__(self, symbols: list[str]):
        self.symbols = [s.lower() for s in symbols]
        self._task = None
        self._running = False

    def _build_url(self):
        streams = "/".join(f"{s}@trade" for s in self.symbols)
        return f"{BINANCE_WS_BASE}?{urlencode({'streams': streams})}"

    async def _run(self):
        url = self._build_url()
        self._running = True
        while self._running:
            try:
                logger.info("Connecting to Binance WS: %s", url)
                async with websockets.connect(url, ping_interval=20) as ws:
                    logger.info("Connected to Binance WS")
                    async for raw in ws:
                        msg = json.loads(raw)
                        data = msg.get("data", {})
                        price = data.get("p")
                        symbol = data.get("s")
                        if symbol and price:
                            await price_cache.set_price(symbol, float(price))
            except Exception as e:
                logger.exception("Binance WS error, reconnecting: %s", e)
                await asyncio.sleep(5)
            finally:
                logger.warning("Disconnected from Binance WS")

    def start(self, loop: asyncio.AbstractEventLoop):
        if self._task is None:
            self._task = loop.create_task(self._run())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
