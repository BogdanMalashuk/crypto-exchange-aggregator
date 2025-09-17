import httpx
import logging
from typing import Optional, List, Dict, Any
from .auth.jwt_client import jwt_client

logger = logging.getLogger("gateway.api_client")

DJANGO_URL = "http://127.0.0.1:8001"


async def get_trades(user_id: Optional[int] = None, symbol: Optional[str] = None, sold: Optional[bool] = None) -> List[Dict[str, Any]]:
    url = f"{DJANGO_URL}/trades/"
    access_token = await jwt_client.get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
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
