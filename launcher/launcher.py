"""Tweet-triggered pump.fun launcher.

  python launcher.py                                   # dry run against live tweets (no transactions)
  python launcher.py --replay fixtures/sample_tweets.json   # dry run on a saved file of tweets
  python launcher.py --live                            # real launches (also needs "dry_run": false in config)

Create a file named STOP in this folder to pause launching without killing open positions.
"""
import argparse
import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path

from naming import Namer
from ledger import Ledger, Limits
from media import fetch_image, render_card
from settings import EST_FEES_PER_LAUNCH_SOL, ROOT, load_config, load_env
from tweets import ReplaySource, TwitterApiIo

log = logging.getLogger("launcher")


def decide_exit(mcap, base, elapsed_min, outside_buyers, cfg):
    """Pure exit rule so it can be tested offline. Returns a reason string or None."""
    if base and mcap:
        if mcap >= base * cfg.take_profit_multiple:
            return "take_profit"
        if mcap <= base * cfg.stop_loss_multiple:
            return "stop_loss"
    if outside_buyers == 0 and elapsed_min >= cfg.sell_if_no_outside_buyer_minutes:
        return "no_outside_buyers"
    if elapsed_min >= cfg.max_hold_minutes:
        return "time_limit"
    return None


def wanted(tweet, cfg) -> str:
    """Returns '' if the tweet should go to naming, otherwise why it was skipped."""
    if time.time() - tweet.created_ts > cfg.max_tweet_age_seconds:
        return "too old"
    if len(tweet.text.strip()) < 3 and not tweet.media_urls:
        return "empty"
    if cfg.keywords and not any(k.lower() in tweet.text.lower() for k in cfg.keywords):
        return "no keyword match"
    return ""


class Bot:
    def __init__(self, cfg, live: bool, source):
        self.cfg, self.live, self.source = cfg, live, source
        self.namer = Namer(cfg.use_claude, cfg.claude_model)
        self.ledger = Ledger(ROOT / ("ledger.csv" if live else "ledger_dry_run.csv"))
        self.limits = Limits(cfg, ROOT / ("state.json" if live else "state_dry_run.json"))
        self.seen = set()
        self.tasks = set()
        self.pump = self.feed = None
        if live:
            from solders.keypair import Keypair
            from feed import TradeFeed
            from pump import Pump
            missing = [k for k in ("SOLANA_PRIVATE_KEY", "RPC_URL", "PINATA_JWT", "PUMPPORTAL_API_KEY")
                       if not os.environ.get(k)]
            if missing:
                raise SystemExit(f"Live mode needs these in .env: {', '.join(missing)}")
            self.pump = Pump(Keypair.from_base58_string(os.environ["SOLANA_PRIVATE_KEY"]),
                             os.environ["RPC_URL"], os.environ["PINATA_JWT"])
            self.feed = TradeFeed(os.environ["PUMPPORTAL_API_KEY"])

    async def run(self):
        if self.feed:
            asyncio.create_task(self.feed.run())
            bal = await asyncio.to_thread(self.pump.balance_sol)
            log.info("LIVE wallet %s balance %.4f SOL", self.pump.pubkey, bal)
            if bal < self.cfg.dev_buy_sol + EST_FEES_PER_LAUNCH_SOL:
                log.warning("Balance is below one launch (dev buy + fees)")
        since = time.time() - 60
        last_claim = time.time()
        while True:
            if (ROOT / "STOP").exists():
                log.info("STOP file present - not launching (open positions still managed)")
            else:
                try:
                    tweets = await asyncio.to_thread(self.source.fetch_new, since)
                except Exception as e:
                    log.warning("tweet fetch failed: %s", e)
                    tweets = []
                for t in sorted(tweets, key=lambda t: t.created_ts):
                    since = max(since, t.created_ts - 5)
                    if t.id in self.seen:
                        continue
                    if len(self.seen) > 20000:  # long runs: since_time already excludes old tweets
                        self.seen.clear()
                    self.seen.add(t.id)
                    await self.consider(t)
            if self.live and time.time() - last_claim > self.cfg.claim_creator_fees_every_hours * 3600:
                last_claim = time.time()
                try:
                    sig = await asyncio.to_thread(self.pump.claim_creator_fees, self.cfg.priority_fee_sol)
                    log.info("claimed creator fees: https://solscan.io/tx/%s", sig)
                except Exception as e:
                    log.info("creator fee claim skipped: %s", e)
            if getattr(self.source, "exhausted", False) and not self.tasks:
                return
            await asyncio.sleep(self.cfg.poll_seconds if not getattr(self.source, "exhausted", False) else 0.5)

    async def consider(self, t):
        why = wanted(t, self.cfg)
        if why:
            log.info("skip @%s %s: %s", t.author, t.id, why)
            return
        idea = await asyncio.to_thread(self.namer.name, t.text, t.author)
        if not idea.launch:
            log.info("skip @%s: %s", t.author, idea.reason)
            return
        if self.live and idea.source == "rules" and not self.cfg.rules_fallback_live:
            log.info("skip @%s: Claude naming unavailable and rules_fallback_live is off", t.author)
            return
        ok, why = self.limits.check(t.author, idea.ticker, self.cfg.dev_buy_sol)
        if not ok:
            log.info("skip $%s: %s", idea.ticker, why)
            return
        # Reserve the budget now, before any await, so two tweets in one poll can't both slip under a limit.
        self.limits.record(t.author, idea.ticker, self.cfg.dev_buy_sol)
        img = None
        for url in t.media_urls[:1]:
            img = await asyncio.to_thread(fetch_image, url)
        image, mime = img or render_card(idea.ticker, idea.name)
        row = {"time": datetime.now().isoformat(timespec="seconds"), "mode": "live" if self.live else "dry_run",
               "tweet_url": t.url, "author": t.author, "name": idea.name, "ticker": idea.ticker,
               "dev_buy_sol": self.cfg.dev_buy_sol}
        if not self.live:
            out = ROOT / "out"
            out.mkdir(exist_ok=True)
            (out / f"{idea.ticker}.png").write_bytes(image)
            self.ledger.write({**row, "status": "would_launch"})
            log.info("DRY RUN would launch %s ($%s) from %s [%s]  -> %s", idea.name, idea.ticker, t.url,
                     idea.source, idea.description)
            return
        task = asyncio.create_task(self.launch(t, idea, image, mime, row))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    async def launch(self, t, idea, image, mime, row):
        from solders.keypair import Keypair
        cfg = self.cfg
        mint_kp = Keypair()
        mint = str(mint_kp.pubkey())
        try:
            uri = await asyncio.to_thread(self.pump.upload_metadata, idea.name, idea.ticker, idea.description,
                                          image, mime, t.url)
            q = await self.feed.watch(mint)  # subscribe before creating so our own first trade is seen
            sig = await asyncio.to_thread(self.pump.create, mint_kp, idea.name, idea.ticker, uri,
                                          cfg.dev_buy_sol, cfg.slippage_pct, cfg.priority_fee_sol)
            ok = await asyncio.to_thread(self.pump.confirm, sig)
        except Exception as e:
            log.error("launch failed for $%s: %s", idea.ticker, e)
            await self.feed.unwatch(mint)
            self.ledger.write({**row, "mint": mint, "status": f"failed: {e}"[:200]})
            return
        row.update(mint=mint, create_tx=sig)
        if not ok:
            log.error("create tx not confirmed: %s", sig)
            await self.feed.unwatch(mint)
            self.ledger.write({**row, "status": "create_not_confirmed"})
            return
        log.info("LAUNCHED %s ($%s) https://pump.fun/coin/%s", idea.name, idea.ticker, mint)
        await self.manage(mint, q, row)

    async def manage(self, mint, q, row):
        cfg, me = self.cfg, self.pump.pubkey
        start, base, cur, peak, buyers = time.monotonic(), None, None, 1.0, set()
        while True:
            try:
                msg = await asyncio.wait_for(q.get(), timeout=5)
                cur = float(msg.get("marketCapSol") or 0) or cur
                if base is None and cur:
                    base = cur
                if msg.get("txType") == "buy" and msg.get("traderPublicKey") != me:
                    buyers.add(msg.get("traderPublicKey"))
                if base and cur:
                    peak = max(peak, cur / base)
            except asyncio.TimeoutError:
                pass
            elapsed = (time.monotonic() - start) / 60
            if self.feed.error:  # no trade data: buyers=0 would be meaningless, so only the time limit applies
                reason = "no_trade_data" if elapsed >= cfg.max_hold_minutes else None
            else:
                reason = decide_exit(cur, base, elapsed, len(buyers), cfg)
            if reason:
                break
        row.update(status="closed", outside_buyers=len(buyers), peak_multiple=round(peak, 2), exit_reason=reason)
        if cfg.dev_buy_sol > 0:
            sell_sig, sol_back = await self.sell(mint, q)
            row.update(sell_tx=sell_sig, sol_back=sol_back,
                       pnl_sol_est="" if sol_back == "" else round(sol_back - cfg.dev_buy_sol - EST_FEES_PER_LAUNCH_SOL, 4))
        await self.feed.unwatch(mint)
        self.ledger.write(row)
        log.info("CLOSED $%s: %s, %d outside buyers, peak %.2fx, back %s SOL", row["ticker"], reason,
                 len(buyers), peak, row.get("sol_back", "-"))

    async def sell(self, mint, q):
        for attempt in range(2):
            try:
                sig = await asyncio.to_thread(self.pump.sell_all, mint, self.cfg.slippage_pct, self.cfg.priority_fee_sol)
                if await asyncio.to_thread(self.pump.confirm, sig):
                    sol_back = ""
                    end = time.monotonic() + 15
                    while time.monotonic() < end:  # read our own sell from the feed for the SOL received
                        try:
                            msg = await asyncio.wait_for(q.get(), timeout=end - time.monotonic())
                        except asyncio.TimeoutError:
                            break
                        if msg.get("traderPublicKey") == self.pump.pubkey and msg.get("txType") == "sell":
                            sol_back = round(float(msg.get("solAmount") or 0), 4)
                            break
                    return sig, sol_back
            except Exception as e:
                log.warning("sell attempt %d failed for %s: %s", attempt + 1, mint, e)
            await asyncio.sleep(5)
        return "SELL FAILED - sell manually", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config.json"))
    ap.add_argument("--replay", help="JSON file of tweets to replay (always dry run)")
    ap.add_argument("--live", action="store_true", help="send real transactions (config dry_run must be false)")
    args = ap.parse_args()
    (ROOT / "logs").mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler(ROOT / "logs" / "launcher.log")])
    load_env()
    cfg = load_config(Path(args.config))
    live = args.live and not cfg.dry_run and not args.replay
    if args.live and not live:
        log.warning("--live ignored: set \"dry_run\": false in config (and don't use --replay) to go live")
    if args.replay:
        source = ReplaySource(Path(args.replay))
    else:
        source = TwitterApiIo(os.environ["TWITTERAPI_KEY"], cfg.accounts, cfg.ignore_replies, cfg.ignore_retweets)
    log.info("mode=%s accounts=%d dev_buy=%.3f SOL max/day=%d launches, %.2f SOL", "LIVE" if live else "DRY RUN",
             len(cfg.accounts), cfg.dev_buy_sol, cfg.max_launches_per_day, cfg.max_sol_per_day)
    asyncio.run(Bot(cfg, live, source).run())


if __name__ == "__main__":
    main()
