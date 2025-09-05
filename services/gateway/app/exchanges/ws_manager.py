import asyncio
import logging
from typing import Dict, Tuple, Optional
from .ws_binance import BinanceWSClient
from .ws_bybit import BybitWSClient

logger = logging.getLogger("gateway.ws_manager")


class WSManager:
    def __init__(self):
        self._clients: Dict[Tuple[int, str], BinanceWSClient] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            self._loop = asyncio.get_event_loop()
        return self._loop

    def start(self, user_id: int, exchange: str, symbols: list[str]):
        key = (user_id, exchange.lower())
        if key in self._clients:
            return False

        loop = asyncio.get_event_loop()
        if exchange.lower() == "binance":
            client = BinanceWSClient(symbols)
        elif exchange.lower() == "bybit":
            client = BybitWSClient(symbols)
        else:
            raise ValueError(f"Unsupported exchange: {exchange}")

        client.start(loop)
        self._clients[key] = client
        return True

    async def stop(self, user_id: int, exchange: str) -> bool:
        key = (user_id, exchange.lower())
        client = self._clients.pop(key, None)
        if not client:
            return False

        await client.stop()
        logger.info("WS stopped: user=%s exchange=%s", user_id, exchange)
        return True

    async def stop_all(self):
        for key, client in list(self._clients.items()):
            try:
                await client.stop()
            except Exception as e:
                logger.exception("Error stopping WS %s: %s", key, e)
        self._clients.clear()
        self._loop = None


ws_manager = WSManager()
