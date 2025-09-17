import httpx
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("gateway.api_client")

DJANGO = "http://127.0.0.1:8001"    
JWT_TOKEN = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU3NTM5NDA0LCJpYXQiOjE3NTY5MzQ2MDQsImp0aSI6IjliMTRlZjZjMmNlNTQxOTRhOTMyNDI5MDYwNGIxZjk4IiwidXNlcl9pZCI6IjIifQ.WoDG_wLRUfI5vfTekElAL-G8Ax3UTWU43LoOMePRb6g")


async def get_trades(user_id: Optional[int] = None, symbol: Optional[str] = None, sold: Optional[bool] = None) -> List[Dict[str, Any]]:
    url = f"{DJANGO}/trades/"
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"} if JWT_TOKEN else {}
    params = {}
    if user_id is not None:
        params["user_id"] = user_id
    if symbol:
        params["symbol"] = symbol
    if sold is not None:
        params["sold"] = "true" if sold else "false"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params, headers=headers)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error("Ошибка при запросе сделок: %s, body: %s", e, resp.text)
            raise
        return resp.json()


async def get_all_open_trades() -> List[Dict[str, Any]]:
    return await get_trades(sold=False)
