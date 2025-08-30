from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
import logging
from .producer import start_kafka, stop_kafka
from .exchanges.binance_ws import BinanceWSClient
from .checker import checker

logger = logging.getLogger("gateway.main")

BINANCE_SYMBOLS = ["BTCUSDT", "ETHUSDT"]


binance_client = BinanceWSClient(symbols=BINANCE_SYMBOLS)


@asynccontextmanager
async def lifespan(application: FastAPI):
    loop = asyncio.get_event_loop()

    await start_kafka(application)

    binance_client.start(loop)
    logger.info("Binance WS client started")

    checker.start(loop)
    logger.info("Checker started")

    yield

    await checker.stop()
    await binance_client.stop()
    await stop_kafka(application)


app = FastAPI(
    title="Crypto Gateway Service",
    lifespan=lifespan,
)

