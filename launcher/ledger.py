"""Spending limits (persisted across restarts) and the results ledger every launch is written to."""
import csv
import json
import time
from pathlib import Path

from settings import EST_FEES_PER_LAUNCH_SOL

DAY = 86400
FIELDS = ["time", "mode", "tweet_url", "author", "name", "ticker", "mint", "dev_buy_sol", "create_tx",
          "status", "outside_buyers", "peak_multiple", "exit_reason", "sell_tx", "sol_back", "pnl_sol_est"]


class Limits:
    def __init__(self, cfg, path: Path):
        self.cfg, self.path = cfg, path
        self.state = json.loads(path.read_text()) if path.exists() else {"launches": []}

    def _recent(self, seconds):
        cutoff = time.time() - seconds
        return [l for l in self.state["launches"] if l["ts"] >= cutoff]

    def check(self, author: str, ticker: str, dev_buy: float):
        today = self._recent(DAY)
        if len(today) >= self.cfg.max_launches_per_day:
            return False, "daily launch limit reached"
        spent = sum(l["sol"] for l in today)
        if spent + dev_buy + EST_FEES_PER_LAUNCH_SOL > self.cfg.max_sol_per_day:
            return False, f"daily SOL limit reached ({spent:.3f} SOL used)"
        if today and time.time() - max(l["ts"] for l in today) < self.cfg.min_seconds_between_launches:
            return False, "too soon after the last launch"
        if any(l["author"].lower() == author.lower()
               for l in self._recent(self.cfg.author_cooldown_minutes * 60)):
            return False, f"already launched off @{author} recently"
        if any(l["ticker"] == ticker for l in today):
            return False, f"${ticker} already launched today"
        return True, ""

    def record(self, author: str, ticker: str, dev_buy: float):
        self.state["launches"].append({"ts": time.time(), "author": author, "ticker": ticker,
                                       "sol": dev_buy + EST_FEES_PER_LAUNCH_SOL})
        self.state["launches"] = self._recent(2 * DAY)
        self.path.write_text(json.dumps(self.state))


class Ledger:
    def __init__(self, path: Path):
        self.path = path
        if not path.exists():
            with path.open("w", newline="") as f:
                csv.DictWriter(f, FIELDS).writeheader()

    def write(self, row: dict):
        with self.path.open("a", newline="") as f:
            csv.DictWriter(f, FIELDS).writerow({k: row.get(k, "") for k in FIELDS})
