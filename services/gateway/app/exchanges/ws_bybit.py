import json
import logging
import websockets
from urllib.parse import urlencode
from decimal import Decimal
from ..price_cache import price_cache
from ..api_client import get_trades
from ..producer import send_profit_trade_event
import asyncio

logger = logging.getLogger("gateway.bybit")

BYBIT_WS_BASE = "wss://stream.bybit.com/realtime"


class BybitWSClient:
    def __init__(self, user_id: int, symbols: list[str]):
        self.user_id = user_id
        self.symbols = [s.upper() for s in symbols]  # Bybit использует заглавные
        self._running = False
        self._fired_trades = set()

    def _build_url(self):
        topics = [f"trade.{s}" for s in self.symbols]
        query = urlencode({"subscribe": ",".join(topics)})
        return f"{BYBIT_WS_BASE}?{query}"

    async def start(self):
        url = self._build_url()
        self._running = True
        while self._running:
            try:
                logger.info("Connecting to Bybit WS: %s", url)
                async with websockets.connect(url, ping_interval=20) as ws:
                    logger.info("Connected to Bybit WS")
                    async for raw in ws:
                        msg = json.loads(raw)
                        data_list = msg.get("data", [])
                        for data in data_list:
                            symbol = data.get("symbol")
                            price_str = data.get("price")
                            if symbol and price_str:
                                price = Decimal(price_str)
                                await price_cache.set_price(symbol, float(price))

                                trades = await get_trades(self.user_id, symbol)
                                for trade in trades:
                                    trade_id = trade.get("id")
                                    if not trade_id:
                                        continue
                                    buy_price = Decimal(str(trade["buy_price"]))
                                    if price > buy_price and trade_id not in self._fired_trades:
                                        event = {
                                            "user_id": self.user_id,
                                            "trade_id": trade_id,
                                            "symbol": symbol,
                                            "quantity": str(trade["quantity"]),
                                            "buy_price": str(buy_price),
                                            "current_price": str(price),
                                        }
                                        await send_profit_trade_event(event)
                                        self._fired_trades.add(trade_id)
            except Exception as e:
                if self._running:
                    logger.exception("Bybit WS error, reconnecting: %s", e)
                    await asyncio.sleep(5)
            finally:
                logger.warning("Disconnected from Bybit WS")

    async def stop(self):
        self._running = False
