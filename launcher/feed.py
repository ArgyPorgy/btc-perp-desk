"""One shared PumpPortal websocket for live trades on the coins we launched (PumpPortal asks for one connection).

Token-trade subscriptions need a PumpPortal API key whose linked wallet holds >= 0.02 SOL
(billed 0.01 SOL per 10,000 messages received).
"""
import asyncio
import json
import logging

import websockets

log = logging.getLogger("feed")
URL = "wss://pumpportal.fun/api/data"


class TradeFeed:
    def __init__(self, api_key: str):
        self.url = f"{URL}?api-key={api_key}"
        self.queues: dict = {}
        self.ws = None
        self.error = None

    async def run(self):
        backoff = 1
        while True:
            try:
                async with websockets.connect(self.url, ping_interval=20) as ws:
                    self.ws, backoff = ws, 1
                    if self.queues:
                        await ws.send(json.dumps({"method": "subscribeTokenTrade", "keys": list(self.queues)}))
                    async for raw in ws:
                        try:
                            msg = json.loads(raw)
                        except json.JSONDecodeError:
                            continue
                        text = msg.get("message") or msg.get("errors")
                        if text and "mint" not in msg:
                            if "only available" in str(text) or "error" in str(text).lower():
                                self.error = str(text)
                                log.error("PumpPortal rejected the trade feed: %s", text)
                            continue
                        q = self.queues.get(msg.get("mint"))
                        if q is not None and msg.get("txType") in ("create", "buy", "sell"):
                            q.put_nowait(msg)
            except Exception as e:
                log.warning("trade feed dropped (%s), reconnecting", e)
            self.ws = None
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)

    async def watch(self, mint: str) -> asyncio.Queue:
        q = self.queues.setdefault(mint, asyncio.Queue())
        if self.ws:
            await self.ws.send(json.dumps({"method": "subscribeTokenTrade", "keys": [mint]}))
        return q

    async def unwatch(self, mint: str):
        self.queues.pop(mint, None)
        if self.ws:
            try:
                await self.ws.send(json.dumps({"method": "unsubscribeTokenTrade", "keys": [mint]}))
            except Exception:
                pass
