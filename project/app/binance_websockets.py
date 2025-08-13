import asyncio
import json
import websockets


async def market_stream(symbols=("btcusdt", "ethusdt")):
    streams = "/".join([f"{s}@trade" for s in symbols])
    url = f"wss://stream.binance.com:9443/stream?streams={streams}"

    async with websockets.connect(url) as ws:
        print(f"Connected to market streams: {symbols}")
        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            # данные о сделках, по конкретному ТЗ изменить или добавить функционал

if __name__ == "__main__":
    asyncio.run(market_stream())
