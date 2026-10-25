# Tweet → pump.fun launcher

Watches X accounts you choose. When one tweets something memeable, Claude names a coin, the bot makes an image,
deploys it on pump.fun through PumpPortal (signed on your machine), watches real trades, exits on your rules,
and logs every result so you can see whether it actually makes money.

## What it will not do (hard-coded, not in config)
- One wallet only. No multi-wallet supply, no bundles, no volume bot.
- No buying after launch. The only buy is the dev buy inside the create transaction (max 1 SOL).
- Every coin's description says it is not affiliated with the person who tweeted; names can't say official/verified/real.
- Daily launch and SOL caps, per-author and per-ticker cooldowns.
- Dry run unless config has `"dry_run": false` **and** you pass `--live`.

## Setup (once)
```
cd launcher
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # fill it in yourself - see below
cp config.example.json config.json   # edit accounts, limits, exits
```
`.env` needs:
| Key | Where | Cost |
|---|---|---|
| `SOLANA_PRIVATE_KEY` | a **fresh** wallet holding only what you'll risk | – |
| `RPC_URL` | Helius/QuickNode free tier (public RPC drops transactions) | free tier ok |
| `TWITTERAPI_KEY` | twitterapi.io | ~$0.00015 per request; 1 request per 8 accounts per poll → ~$1.30/day per 8 accounts at 10 s polling |
| `PINATA_JWT` | pinata.cloud (file upload scope) | free tier |
| `PUMPPORTAL_API_KEY` | pumpportal.fun; its linked wallet needs ≥ 0.02 SOL | 0.01 SOL per 10,000 trade messages |
| `ANTHROPIC_API_KEY` | console.anthropic.com | ~1–2¢ per tweet named (set `claude_model` to `claude-haiku-5-5` to cut that) |

Per launch on-chain: ~0.02–0.03 SOL in fees + your dev buy; PumpPortal takes 0.5% of each trade.

## Run
```
.venv/bin/python tests/test_offline.py && .venv/bin/python tests/test_live_path.py   # offline checks
.venv/bin/python launcher.py --replay fixtures/sample_tweets.json   # dry run on saved tweets
.venv/bin/python launcher.py                                        # dry run on live tweets (logs what it WOULD launch)
.venv/bin/python launcher.py --live                                 # real launches (config dry_run=false)
.venv/bin/python report.py                                          # did it work?
```
Pause launching anytime: `touch STOP` (open positions are still managed). Resume: `rm STOP`.

Leave it running on a Mac: `caffeinate -i .venv/bin/python launcher.py --live`
Better: a $5/month VPS with `tmux` so it survives your laptop sleeping.

## Exit rules (config)
Market cap measured against the first trade seen (your launch):
- `take_profit_multiple` (2.0) → sell all
- `stop_loss_multiple` (0.6) → sell all
- `sell_if_no_outside_buyer_minutes` (5) → nobody else bought, sell and move on
- `max_hold_minutes` (15) → sell whatever happens
With `dev_buy_sol: 0` nothing is sold; you only earn pump.fun creator fees (claimed every `claim_creator_fees_every_hours`).

## Files
`launcher.py` main loop · `tweets.py` X source · `naming.py` Claude naming + guardrails · `media.py` image ·
`pump.py` IPFS + PumpPortal + RPC · `feed.py` live trades · `ledger.py` limits + results · `report.py` summary ·
`measure_launches.py` read-only study of how fresh launches do.

Results: `ledger.csv` (live) / `ledger_dry_run.csv`; logs in `logs/launcher.log`.
