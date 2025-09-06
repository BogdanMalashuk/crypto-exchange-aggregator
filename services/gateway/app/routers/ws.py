from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..exchanges.ws_manager import ws_manager

router = APIRouter(tags=["WebSocket"])


class StartRequest(BaseModel):
    symbols: list[str]


@router.post("/users/{user_id}/exchanges/{exchange}/ws/start")
async def start_ws(user_id: int, exchange: str, req: StartRequest):
    ok = await ws_manager.start(user_id, exchange, req.symbols)
    if not ok:
        raise HTTPException(status_code=400, detail="WS already running")
    return {"status": "started", "user_id": user_id, "exchange": exchange, "symbols": req.symbols}


@router.post("/users/{user_id}/exchanges/{exchange}/ws/stop")
async def stop_ws(user_id: int, exchange: str):
    ok = await ws_manager.stop(user_id, exchange)
    if not ok:
        raise HTTPException(status_code=404, detail="WS not found")
    return {"status": "stopped", "user_id": user_id, "exchange": exchange}
