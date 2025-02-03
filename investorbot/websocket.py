"""Client using the threading API."""

import json
import time
import investorbot.env as env
import asyncio
from websockets.asyncio.client import connect


async def __track_ticker():
    async with connect(
        "wss://stream.crypto.com/exchange/v1/market",
    ) as websocket:
        i = 0
        subscribe = json.dumps(
            {
                "id": 1,
                "method": "subscribe",
                "params": {"channels": ["ticker.BTC_USD"]},
                "nonce": env.time.now_in_ms(),
            }
        )

        await websocket.send(subscribe)

        while True:
            message = await websocket.recv()
            message_dict = json.loads(message)

            if message_dict["method"] == "public/heartbeat":
                response = json.dumps(
                    {"id": message_dict["id"], "method": "public/respond-heartbeat"}
                )
                await websocket.send(response)
                print(f"sending {response}")
            elif "result" in message_dict:
                output = message_dict["result"]["data"]

                print(json.dumps(output))
            time.sleep(0.1)
            if i % 10 == 0:
                print(f"increment {i}")
            i += 1


def track_ticker():
    asyncio.run(__track_ticker())
