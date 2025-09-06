import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .price_cache import price_cache
from .checker import checker
from .producer import kafka_producer
from .exchanges.ws_manager import ws_manager
from .routers import ws
logger = logging.getLogger("gateway.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    logger.info("Starting services...")

    await price_cache.start()
    await checker.start()
    await kafka_producer.start()

    logger.info("All services started")
    yield

    # --- shutdown ---
    logger.info("Stopping services...")

    await ws_manager.stop_all()
    await checker.stop()
    await price_cache.stop()
    await kafka_producer.stop()

    logger.info("All services stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(ws.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
