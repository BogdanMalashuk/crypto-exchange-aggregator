import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .producer import start_kafka, stop_kafka
from .checker import checker
from .exchanges.ws_manager import ws_manager
from .routers import ws as ws_router

logger = logging.getLogger("gateway.main")


@asynccontextmanager
async def lifespan(application: FastAPI):
    await start_kafka(application)
    logger.info("Kafka started")

    checker.start(asyncio.get_event_loop())
    logger.info("Checker started")

    yield

    await checker.stop()
    await ws_manager.stop_all()
    await stop_kafka(application)


app = FastAPI(
    title="Crypto Gateway Service",
    lifespan=lifespan,
)

app.include_router(ws_router.router)
