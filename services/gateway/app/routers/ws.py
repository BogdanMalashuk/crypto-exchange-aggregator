import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..exchanges.ws_manager import ws_manager

router = APIRouter(prefix="/users", tags=["ws"])


def _default_symbols() -> List[str]:
    raw = os.getenv("BINANCE_SYMBOLS", "BTCUSDT,ETHUSDT")
    return [s.strip().upper() for s in raw.split(",") if s.strip()]


class StartWSRequest(BaseModel):
    symbols: Optional[List[str]] = None


@router.post("/{user_id}/exchanges/{exchange}/ws/start")
async def start_ws(user_id: int, exchange: str, body: StartWSRequest | None = None):
    symbols = (body.symbols if body and body.symbols else _default_symbols())
    try:
        started = ws_manager.start(user_id, exchange, symbols)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not started:
        raise HTTPException(status_code=400, detail="Already running")
    return {"detail": f"Started WS for {exchange} (user {user_id})", "symbols": symbols}


@router.post("/{user_id}/exchanges/{exchange}/ws/stop")
async def stop_ws(user_id: int, exchange: str):
    stopped = await ws_manager.stop(user_id, exchange)
    if not stopped:
        raise HTTPException(status_code=400, detail="Not running")
    return {"detail": f"Stopped WS for {exchange} (user {user_id})"}
