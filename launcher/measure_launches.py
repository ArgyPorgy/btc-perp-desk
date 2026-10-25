"""Measure what happens to fresh pump.fun launches (read-only, no API key needed).

Collects every new coin for COLLECT seconds from PumpPortal's free new-token stream, then WATCH seconds after
collection ends reads each coin's bonding-curve SOL balance from Solana. SOL in the curve minus rent minus the
creator's dev buy = net SOL that other traders put in.
  python measure_launches.py [collect_seconds] [watch_seconds] [rpc_url]
"""
import asyncio
import json
import statistics
import sys
import time

import requests
import websockets

COLLECT = int(sys.argv[1]) if len(sys.argv) > 1 else 120
WATCH = int(sys.argv[2]) if len(sys.argv) > 2 else 300
RPC = sys.argv[3] if len(sys.argv) > 3 else "https://api.mainnet-beta.solana.com"


def rpc(method, params):
    return requests.post(RPC, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=30).json()


async def collect():
    coins = []
    async with websockets.connect("wss://pumpportal.fun/api/data", ping_interval=20) as ws:
        await ws.send(json.dumps({"method": "subscribeNewToken"}))
        end = time.time() + COLLECT
        while time.time() < end:
            try:
                m = json.loads(await asyncio.wait_for(ws.recv(), 5))
            except asyncio.TimeoutError:
                continue
            if m.get("txType") == "create" and m.get("bondingCurveKey"):
                coins.append({"curve": m["bondingCurveKey"], "dev_buy": float(m.get("solAmount") or 0),
                              "t": time.time()})
    return coins


coins = asyncio.run(collect())
print(f"new coins in {COLLECT}s: {len(coins)} ({len(coins) / COLLECT * 3600:.0f}/hour); waiting {WATCH}s...")
time.sleep(WATCH)
real = []
for i in range(0, len(coins), 100):
    batch = coins[i:i + 100]
    res = rpc("getMultipleAccounts", [[c["curve"] for c in batch], {"encoding": "base64", "dataSlice": {"offset": 0, "length": 0}}])
    for c, acc in zip(batch, res["result"]["value"]):
        if acc:
            c["lamports"] = acc["lamports"]
            real.append(c)
size = len(requests.post(RPC, json={"jsonrpc": "2.0", "id": 1, "method": "getAccountInfo",
                                    "params": [real[0]["curve"], {"encoding": "base64"}]}, timeout=30)
           .json()["result"]["value"]["data"][0]) * 3 // 4
rent = rpc("getMinimumBalanceForRentExemption", [size])["result"] / 1e9
inflow = [max(0.0, c["lamports"] / 1e9 - rent - c["dev_buy"]) for c in real]
age = statistics.median(time.time() - c["t"] for c in real) / 60
print(f"checked {len(real)} coins, median age {age:.1f} min (curve rent {rent:.4f} SOL)")
for x in (0.01, 0.1, 0.5, 1, 5):
    print(f"  {sum(v > x for v in inflow) / len(real):6.1%} had more than {x} SOL of outside net buying")
print(f"  median outside net buying: {statistics.median(inflow):.3f} SOL, top coin {max(inflow):.2f} SOL")
print(f"  creators' dev buys: median {statistics.median(c['dev_buy'] for c in real):.3f} SOL")
