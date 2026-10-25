# Dashboard changelog
Newest first. Every change: date (UTC), what, why.

## 2026-10-25
- **News terminal.** `server.py` replaces the plain file server: it serves the page and polls 23 RSS feeds plus the ForexFactory calendar in the background. `news.py` tags each headline with impact 0–3 and merges duplicates. New: a News / Calendar tab in the right panel, a "Next US catalyst" countdown in the header, a red banner for new impact-3 headlines, purple chart markers (Layers → News markers), and BTC's 15-minute and since-then move on every headline. Why: catalysts (FOMC, CPI, tariffs, war) decide whether to enter, hold or step aside, and the desk had no view of them.
- **Gamma, Tape and Liquidations moved into tabs** to make room for news. Gamma levels are still drawn on the chart and still feed the scorecard.
- **Restored `vendor/`** (the chart library), which didn't come across when the project moved to Documents. Added a CDN fallback if the file goes missing again.
- **Tests:** `tests/test_news.py` (16 headline cases).
