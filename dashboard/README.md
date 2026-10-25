# BTC Perp Desk

A local, always-live BTCUSDT perpetual dashboard. Data comes straight from Binance USDⓈ-M futures' public API
(the same feed TradingView's BINANCE:BTCUSDT.P uses) plus Deribit for options. Everything is computed in your browser.

## Start
Double-click `start.command` (macOS), or:
```
cd ~/Documents/BTC\ Perp\ Desk/dashboard && python3 server.py
```
then open http://127.0.0.1:8787. Leave the tab open; it reconnects by itself after drops or sleep.
`server.py` serves the page and runs the news feed; the old `python3 -m http.server` still shows the charts but no news.

## What's on screen
| Panel | Source | Exact or approximate |
|---|---|---|
| Candles, volume (1m–1d) | Binance klines + live kline stream | exact |
| Delta & CVD | Binance taker-buy volume per candle | exact (cross-checked against every trade) |
| Footprint (sells × buys per price, POC, 3:1 diagonal imbalances) | every aggTrade | exact; history = last ~20 min + everything while open |
| Time & sales | aggTrade stream | exact (min-size filter) |
| Liquidity heatmap | local order book, synced per Binance's rules | exact book; history only while the page is open |
| Liquidations | forceOrder stream | Binance sends at most the largest one per second |
| Open interest | Binance OI (5m history + live 15 s poll) | exact, 30-day history limit |
| Funding, mark, index | markPrice stream | exact |
| VWAP (session, ±1σ/2σ), weekly VWAP, EMA200 | computed | standard formulas |
| BOS / CHoCH, order blocks, FVGs, consolidation breakouts | computed | rule-based (see js/indicators.js) |
| Volume profile, POC / VAH / VAL, prior-day value area, initial balance | computed from candles | approximated from candle ranges |
| Options gamma: flip, call wall, put wall | Deribit option chain, Black-Scholes | walls solid, dealer sign assumed |
| Scorecard | all of the above | context, not a forecast |
| News (right panel, chart markers, alert banner) | 23 public RSS feeds via `server.py`: Fed, White House, SEC, Trump's Truth Social posts, CNBC, investingLive, Google News searches (Reuters/AP/Bloomberg/WSJ), BBC, Al Jazeera, Guardian, CoinDesk, The Block, Decrypt, Cointelegraph | headlines exact; impact tags are keyword rules |
| Calendar + "Next US catalyst" countdown | ForexFactory weekly calendar (USD high/medium, EUR/JPY/CNY/GBP high) | exact times; no actual values |

The header's health light turns green only when both streams are fresh, the order book is in sync, and the streamed
price matches Binance's REST price (checked every 30 s).

## News terminal
Every headline gets a category (Fed, data, policy, geo, markets, crypto) and an impact score:
**3** = can move BTC now (FOMC / Fed rate moves, US CPI/PCE/jobs prints, tariff actions, US–Iran/Russia/China escalation,
exchange hacks, ETF decisions), **2** = relevant, **1** = background. Previews, opinion and "could/might" headlines never
score 3. A headline from an unknown outlet is capped at 1 until a second outlet or a major one carries it. Duplicates
across sources are merged. Each item shows BTC's move 15 minutes after it came out and since then, so you can see whether
the market cared. New impact-3 headlines pop up as a red banner over the chart and get a purple marker on the candles
(toggle in Layers). The same feed in the terminal: `python3 news.py --hours 6 --min-impact 2`. Rules live in `news.py`;
`tests/test_news.py` pins their behaviour.

## Layers
"Layers ▾" toggles each overlay and sets swing length, profile bars, flow bars and gamma expiries. Settings are saved
in your browser. In the browser console, `desk` exposes live state (`desk.S`, `desk.book`, `desk.heat`).

## Tests
```
node tests/test_indicators.js   # math + live cross-checks vs Binance / Deribit / quant/gex.py
node tests/test_book_live.js    # two independently synced order books must match level-for-level
python3 tests/test_news.py      # news impact rules on known headlines
```
Changes to the desk are logged in `CHANGELOG.md`.

Charts: TradingView Lightweight Charts™ v4.2.3 (Apache-2.0, vendored in `vendor/`).
