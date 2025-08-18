import asyncio
import json
import websockets


async def market_stream(symbols=("BTCUSDT", "ETHUSDT")):
    url = "wss://stream.bybit.com/v5/public/spot"

    async with websockets.connect(url) as ws:
        args = [f"publicTrade.{s}" for s in symbols]
        subscribe_msg = {
            "op": "subscribe",
            "args": args
        }

        await ws.send(json.dumps(subscribe_msg))
        print(f"Connected to Bybit market streams: {symbols}")

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            # данные о сделках, по конкретному ТЗ изменить или добавить функционал

if __name__ == "__main__":
    asyncio.run(market_stream())
