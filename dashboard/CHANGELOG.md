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
