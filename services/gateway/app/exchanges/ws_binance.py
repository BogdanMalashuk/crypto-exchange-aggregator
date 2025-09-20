import json
import logging
import websockets
from urllib.parse import urlencode
from decimal import Decimal
from ..price_cache import price_cache
import asyncio


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger("gateway.binance")
BINANCE_WS_BASE = "wss://stream.binance.com:9443/stream"


class BinanceWSClient:
    def __init__(self, user_id: int, symbols: list[str]):
        self.user_id = user_id
        self.symbols = [s.lower() for s in symbols]
        self._running = False

    def _build_url(self):
        streams = "/".join(f"{s}@trade" for s in self.symbols)
        return f"{BINANCE_WS_BASE}?{urlencode({'streams': streams})}"

    async def start(self):
        url = self._build_url()
        self._running = True
        while self._running:
            try:
                async with websockets.connect(url, ping_interval=20) as ws:
                    logger.info("Connected to Binance WS: %s", url)
                    async for raw in ws:
                        msg = json.loads(raw)
                        data = msg.get("data", {})
                        price_str = data.get("p")
                        symbol = data.get("s")
                        if symbol and price_str:
                            price = Decimal(price_str)
                            await price_cache.set_price(symbol, float(price))
            except Exception as e:
                if self._running:
                    logger.info("Binance WS error, reconnecting: %s", e)
                    await asyncio.sleep(5)
            finally:
                logger.info("Disconnected from Binance WS")

    async def stop(self):
        self._running = False
