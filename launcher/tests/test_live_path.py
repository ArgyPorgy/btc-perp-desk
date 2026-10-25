"""Exercise the live launch -> monitor -> sell -> ledger path with a fake wallet and fake trade feed.
No network, no money.  .venv/bin/python tests/test_live_path.py
"""
import asyncio
import csv
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import launcher as L  # noqa: E402
from ledger import Ledger, Limits  # noqa: E402
from naming import CoinIdea  # noqa: E402
from settings import Config  # noqa: E402
from tweets import Tweet  # noqa: E402

ME = "MyWallet111"


class FakePump:
    pubkey = ME

    def __init__(self, script):
        self.script, self.sold = script, False

    def upload_metadata(self, *a):
        return "https://ipfs.io/ipfs/fake"

    def create(self, mint_kp, *a):
        self.mint = str(mint_kp.pubkey())
        return "CREATE_SIG"

    def confirm(self, sig, timeout=60):
        return True

    def sell_all(self, mint, *a):
        self.sold = True
        return "SELL_SIG"


class FakeFeed:
    def __init__(self, pump, events):
        self.pump, self.events, self.q, self.error = pump, events, None, None

    async def watch(self, mint):
        self.q = asyncio.Queue()
        asyncio.get_running_loop().call_later(0.05, self._play)
        return self.q

    def _play(self):
        for e in self.events:
            self.q.put_nowait({"mint": self.pump.mint, **e})

    async def unwatch(self, mint):
        pass


def run_case(events, sell_event=None, **cfg_kw):
    cfg = Config(accounts=["a"], dev_buy_sol=0.05, **cfg_kw)
    with tempfile.TemporaryDirectory() as d:
        bot = L.Bot.__new__(L.Bot)
        bot.cfg, bot.live, bot.tasks = cfg, True, set()
        bot.ledger = Ledger(Path(d) / "ledger.csv")
        bot.limits = Limits(cfg, Path(d) / "state.json")
        bot.pump = FakePump(None)
        bot.feed = FakeFeed(bot.pump, events)
        orig_sell = FakePump.sell_all

        def sell_and_report(self, mint, *a):
            sig = orig_sell(self, mint, *a)
            if sell_event:
                bot.feed.q.put_nowait({"mint": mint, **sell_event})
            return sig
        bot.pump.sell_all = sell_and_report.__get__(bot.pump)
        t = Tweet("1", "https://x.com/a/status/1", "doge to the moon", "a", time.time())
        idea = CoinIdea(True, "", "Moon Doge", "MDOGE", "desc", "claude")
        row = {"time": "now", "mode": "live", "tweet_url": t.url, "author": "a", "name": idea.name,
               "ticker": idea.ticker, "dev_buy_sol": cfg.dev_buy_sol}
        asyncio.run(bot.launch(t, idea, b"png", "image/png", row))
        rows = list(csv.DictReader((Path(d) / "ledger.csv").open()))
        return bot, rows


def test_take_profit():
    events = [{"txType": "create", "traderPublicKey": ME, "marketCapSol": 30, "solAmount": 0.05},
              {"txType": "buy", "traderPublicKey": "Alice", "marketCapSol": 45, "solAmount": 0.5},
              {"txType": "buy", "traderPublicKey": "Bob", "marketCapSol": 65, "solAmount": 0.7}]
    bot, rows = run_case(events, sell_event={"txType": "sell", "traderPublicKey": ME, "solAmount": 0.11})
    r = rows[0]
    assert bot.pump.sold and r["exit_reason"] == "take_profit" and r["outside_buyers"] == "2", r
    assert r["sol_back"] == "0.11" and abs(float(r["pnl_sol_est"]) - 0.03) < 1e-9, r
    assert r["create_tx"] == "CREATE_SIG" and r["sell_tx"] == "SELL_SIG"


def test_no_buyers_exit():
    events = [{"txType": "create", "traderPublicKey": ME, "marketCapSol": 30, "solAmount": 0.05}]
    bot, rows = run_case(events, sell_event={"txType": "sell", "traderPublicKey": ME, "solAmount": 0.048},
                         sell_if_no_outside_buyer_minutes=0.002)
    r = rows[0]
    assert r["exit_reason"] == "no_outside_buyers" and r["outside_buyers"] == "0" and float(r["pnl_sol_est"]) < 0, r


if __name__ == "__main__":
    test_take_profit()
    print("ok  test_take_profit")
    test_no_buyers_exit()
    print("ok  test_no_buyers_exit")
