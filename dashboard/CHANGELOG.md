# Dashboard changelog
Newest first. Every change: date (UTC), what, why.

## 2026-10-25
- **News terminal.** `server.py` replaces the plain file server: it serves the page and polls 23 RSS feeds plus the ForexFactory calendar in the background. `news.py` tags each headline with impact 0–3 and merges duplicates. New: a News / Calendar tab in the right panel, a "Next US catalyst" countdown in the header, a red banner for new impact-3 headlines, purple chart markers (Layers → News markers), and BTC's 15-minute and since-then move on every headline. Why: catalysts (FOMC, CPI, tariffs, war) decide whether to enter, hold or step aside, and the desk had no view of them.
- **Gamma, Tape and Liquidations moved into tabs** to make room for news. Gamma levels are still drawn on the chart and still feed the scorecard.
- **Restored `vendor/`** (the chart library), which didn't come across when the project moved to Documents. Added a CDN fallback if the file goes missing again.
- **Tests:** `tests/test_news.py` (16 headline cases).

## 2026-10-25 (late)
- News rule: "sanctions" now needs a country or sanctioning-body context. Why: a US county probation program ("Swift and Sure Sanctions") showed up as a geopolitical headline. Test case added.

## 2026-10-26
- News rules: a crash in a foreign market (e.g. Brazil after its election) is no longer flagged as a US market crash, and clickbait like "smart money shock" is excluded. Routine Russian strikes on Ukrainian cities now count as ongoing conflict (impact 2), not escalation (3); strikes on NATO members still count as 3. Why: three of today's five impact-3 headlines were these, and BTC barely moved on them (≤0.2% in 15m). Tests: 20/20.

## 2026-10-27
- News rule: tariff headlines about a domestic budget (chancellor, budget, fuel duty) are capped at impact 2. Why: the UK budget's food-tariff cut showed up as an impact-3 TARIFFS headline, but it isn't a trade-war action and BTC moved under 0.1% in the 15 minutes after. Test case added (21/21).
- `tests/test_indicators.js` now finds `quant/gex.py` relative to its own file, so it passes when run from the project root (the scheduled desk runs it that way) as well as from `dashboard/`. Before this, the gamma cross-check crashed with "file not found".

## 2026-10-28
- **Multi-market: BTC / ETH / HOOD.** Header buttons switch markets (or use `?s=ETHUSDT` / `?s=HOODUSDT`; the last one picked is remembered). All three are Binance USDⓈ-M perps on the same API, and HOODUSDT is Binance's 24/7 TradFi perp on Robinhood stock, so every panel works on each: candles, delta/CVD, OI, footprint, heatmap, tape, liquidations, scorecard, structure, VWAP, profile. Price decimals, footprint row sizes, tape size filter and units adapt per market. Options gamma uses Deribit BTC or ETH options; HOOD has no listed options, so its gamma panel says so.
- `tools/snapshot.js` takes a symbol: `node tools/snapshot.js ETHUSDT`.
- News: Robinhood and Ethereum Google News searches, plus HOOD / ETH rules. The 15m/since reaction on each headline is measured in the market you're viewing. Tests 23/23.
- News fetch: each feed now has a 30s cap on the whole body read, on top of the 12s per-socket timeout. Why: in the 07:00 UTC desk run, `news.py --hours 3` took over 5 minutes with 7 feeds failing (resets and handshake/read timeouts). A server that keeps sending bytes slowly never trips the per-socket timeout, which threatens the scheduled run. This does not bound DNS or connect hangs. Tests: news 23/23; indicators offline all ok, but the live section failed to connect to a Cloudflare-fronted API (network, unrelated).

## 2026-10-29
- **HYPE added; HOOD moved to Nasdaq.** Markets are now BTC / ETH / HYPE (Binance USDⓈ-M perps) and HOOD (Nasdaq, regular session). HOOD candles come from Yahoo Finance through `server.py` (`/api/stock`, new `stocks.py`), polled every 15s; the page hides what a stock doesn't have (funding, OI, taker delta/CVD, footprint, tape, liquidations, 4h) and shows day change, previous close and session open/closed instead. Old `?s=HOODUSDT` links open HOOD. Why: Robinhood trades on Nasdaq; the Binance TradFi perp is a thinner proxy.
- `tools/snapshot.js HOOD` reads Nasdaq (15m/1h/1d), `HYPEUSDT` works like the other perps.
- News: Hyperliquid Google News search and a HYPE rule. Why: "NYSE owner takes steps to bring Hyperliquid perpetual futures to U.S." (HYPE +9% that hour) scored impact 1. Tests 24/24. HYPE replaces HOODUSDT in the per-market headline reactions; HOOD reactions use Nasdaq 1m candles.
- `quant/fapi.py` (the geo-block fallback) moved to port 8797, off the dashboard's 8787.

- **Paper desk on the chart.** `server.py` serves `/api/paper` (the paper desk's state); the page draws this market's open positions (entry / stop / target) and pending orders as price lines, refreshed every 30s, plus a "Paper desk" header stat (P&L %, open, pending). `?rest=http://127.0.0.1:8797` points the page at `quant/fapi.py` where Binance is geo-blocked (local URLs only).
