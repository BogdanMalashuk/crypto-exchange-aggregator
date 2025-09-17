import httpx
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("gateway.jwt_client")

DJANGO_URL = "http://127.0.0.1:8001"
SERVICE_EMAIL = "service@service.com"
SERVICE_PASSWORD = "testpassword"


class JWTClient:
    def __init__(self):
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._expires_at: Optional[datetime] = None
        self._lock = asyncio.Lock()

    async def _login(self) -> None:
        url = f"{DJANGO_URL}/api/auth/login/"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json={
                "email": SERVICE_EMAIL,
                "password": SERVICE_PASSWORD,
            })
            resp.raise_for_status()
            data = resp.json()

        self._access_token = data["access"]
        self._refresh_token = data["refresh"]
        self._expires_at = datetime.now() + timedelta(minutes=5)
        logger.info("JWT login successful, new tokens obtained")

    async def _refresh(self) -> bool:
        if not self._refresh_token:
            return False

        url = f"{DJANGO_URL}/api/auth/token/refresh/"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json={"refresh": self._refresh_token})

        if resp.status_code != 200:
            logger.warning("Failed to refresh token: %s", resp.text)
            return False

        data = resp.json()
        self._access_token = data["access"]
        self._expires_at = datetime.now() + timedelta(minutes=5)
        logger.info("JWT access token refreshed")
        return True

    async def get_access_token(self) -> str:
        async with self._lock:
            if (
                self._access_token is None
                or self._expires_at is None
                or datetime.utcnow() >= self._expires_at
            ):
                if not await self._refresh():
                    await self._login()
            return self._access_token


jwt_client = JWTClient()
