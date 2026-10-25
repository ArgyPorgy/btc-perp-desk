# BTC Perp Desk

A local BTCUSDT-perpetual trading workstation: a live dashboard with a news terminal, a paper-trading desk with an
auditable journal, and the quant research behind every rule. Paper money only. Nothing here places real orders.

| Folder | What it is | Start |
|---|---|---|
| `dashboard/` | Live chart, order flow, footprint, heatmap, options gamma, scorecard, news + economic calendar | double-click `dashboard/start.command` → http://127.0.0.1:8787 |
| `quant/` | Paper desk (`paper_desk.py`), journal (`paper/journal.md`), backtests, research log | `python3 quant/paper_desk.py` |
| `orb/` | Earlier strategy backtests (ORB, averaging down, SMC) | `python3 orb/run_all.py` |
| `launcher/` | Tweet → pump.fun token deployer with hard guardrails (dry-run by default) | see `launcher/README.md` |
| root `*.py` | Stake Mines / Crash provably-fair verifiers and simulations | `python3 verifier.py` |

## Data sources and keys
The dashboard and the desk need **no API keys**: Binance USDⓈ-M futures and Deribit public market data, plus public RSS
feeds and the ForexFactory calendar for news. The launcher is the only part that uses keys; they go in `launcher/.env`
(template: `launcher/.env.example`), which git ignores.

Large caches (candles, crash history, news) aren't in the repo; the scripts rebuild them on first run.

## Automation
A Claude scheduled task (`btc-paper-desk-2h`) runs the desk every 2 hours: it reads the chart and news, manages the
paper book, and writes `quant/paper/journal.md`. `.claude/settings.json` holds the narrow permissions it needs.
