import asyncio
import json
import logging
import websockets
from ..price_cache import price_cache

logger = logging.getLogger("gateway.bybit")

BYBIT_WS_BASE = "wss://stream.bybit.com/v5/public/spot"


class BybitWSClient:
    def __init__(self, symbols: list[str]):
        self.symbols = [s.upper() for s in symbols]
        self._task = None
        self._running = False

    def _build_subscribe_msg(self):
        return json.dumps({
            "op": "subscribe",
            "args": [f"trade.{s}" for s in self.symbols]
        })

    async def _run(self):
        url = BYBIT_WS_BASE
        logger.info("Connecting to Bybit WS: %s", url)
        self._running = True
        while self._running:
            try:
                async with websockets.connect(url, ping_interval=20) as ws:
                    subscribe_msg = self._build_subscribe_msg()
                    logger.info("Subscribing to Bybit trades: %s", subscribe_msg)
                    await ws.send(subscribe_msg)

                    async for raw in ws:
                        msg = json.loads(raw)
                        topic = msg.get("topic")
                        data = msg.get("data")

                        if topic and data:
                            trades = data if isinstance(data, list) else [data]
                            for t in trades:
                                price = t.get("p")
                                if price:
                                    symbol = topic.split(".")[-1]
                                    logger.info("Bybit trade: %s price=%s", symbol, price)
                                    await price_cache.set_price(symbol, float(price))
            except Exception as e:
                logger.exception("Bybit WS error, reconnecting: %s", e)
                await asyncio.sleep(5)

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
