import asyncio
import logging
from typing import Dict, Tuple
from .ws_binance import BinanceWSClient
from .ws_bybit import BybitWSClient

logger = logging.getLogger("gateway.ws_manager")


class WSManager:
    def __init__(self):
        # key = (user_id, exchange), value = client
        self._clients: Dict[Tuple[int, str], object] = {}
        self._tasks: Dict[Tuple[int, str], asyncio.Task] = {}

    async def start(self, user_id: int, exchange: str, symbols: list[str]) -> bool:
        """
        Запускаем WS-клиент. Возвращает False, если уже запущен.
        """
        key = (user_id, exchange.lower())
        if key in self._clients:
            return False

        if exchange.lower() == "binance":
            client = BinanceWSClient(user_id, symbols)
        elif exchange.lower() == "bybit":
            client = BybitWSClient(user_id, symbols)
        else:
            raise ValueError(f"Unsupported exchange: {exchange}")

        self._clients[key] = client
        task = asyncio.create_task(client.start())
        self._tasks[key] = task
        logger.info("WS started: user=%s exchange=%s symbols=%s", user_id, exchange, symbols)
        return True

    async def stop(self, user_id: int, exchange: str) -> bool:
        key = (user_id, exchange.lower())
        client = self._clients.pop(key, None)
        task = self._tasks.pop(key, None)
        if not client:
            return False

        try:
            await client.stop()
        except Exception as e:
            logger.error("Error stopping WS %s: %s", key, e)

        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        logger.info("WS stopped: user=%s exchange=%s", user_id, exchange)
        return True

    async def stop_all(self):
        for key in list(self._clients.keys()):
            await self.stop(*key)  # key = (user_id, exchange)
        logger.info("All WS connections stopped")


ws_manager = WSManager()
