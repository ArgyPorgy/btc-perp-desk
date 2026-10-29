# Desk lessons: mistakes, misses and the rules they produced

Read this at the start of every run. Every mistake or miss gets a dated entry; when it changes how the desk trades,
the rule goes into **Current rules** too. Skipped or cancelled plan trades are also logged as shadow trades in
`paper_desk.py shadow`, so the report shows what my overrides cost (+R) or saved (−R).

## Current rules (newest last)
1. **Account first.** Propr Turbo 1-Step: +9% to pass ($10,900). Fail below $9,700 (static 3%) or 3% under the 00:00 UTC
   balance (daily). `paper_desk.py` enforces both and caps open + pending risk at half the room. Never widen a stop.
2. **Both directions, both styles.** Swings (tested setups) and scalps (chart reads), long or short. A long-only desk
   was a bias, not a view (2026-10-28).
3. **A backtest is one input, not a veto.** Weigh it with structure, trend, flow (taker delta, OI, funding), gamma,
   news and the chart itself. When a backtest is strongly negative, name the specific reason this case differs.
4. **Test before placing, where the pattern has history.** If it has none, label the trade untested.
5. **A two-sided plan stays two-sided** unless the chart (not a backtest alone) invalidates a side.
6. **Late triggers count.** If a planned trigger fired between runs and price is still within 0.25R of the planned
   entry, take it. That is the plan, not chasing.
7. **Score every override.** Each cancelled or skipped plan trade becomes a shadow trade.
8. **Look at the actual chart** (screenshot) before placing, not only the numbers: the numbers missed that HYPE had
   already reached X1's target before its entry could fill.
9. **Size from the stop, not from leverage.** Risk $ / stop distance = size; the 1x leverage setting is margin only.

## Mistakes and misses
| Date (UTC) | What happened | Cost | Lesson → rule |
|---|---|---|---|
| 2026-10-26 | Held L1 through several +1.5R–1.9R excursions; considered scalping it. Tested: take-profit + re-enter lowered R on the broad samples. | none (L1 hit target, +1.88R) | Kept one-shot holds for the tested swing setups. |
| 2026-10-28 | Desk was long-only because two narrow short tests lost; never tested shorts in a falling market. User pushed back. | opportunity | Rule 2. Short side tested properly: B20 bear-regime breakdown short added. |
| 2026-10-28 | The 4h schedule from the earlier session had silently disappeared; runs at 16:05 and 20:05 never happened. | missed the FOMC window | Check the scheduled task exists at the start of each session (`list_triggers`). |
| 2026-10-29 12:09 | Placed the first three scalps (BTC release breakout both ways, HYPE pullback) without testing them; user asked "are these backtested?" | none yet | Rule 4. `scalp_tests.py` written. |
| 2026-10-29 12:24 | Cancelled BOTH sides of the BTC release breakout (BRK1) on a −0.22R backtest, minutes after the user said a backtest is not a veto. | see S1 | Rule 3. |
| 2026-10-29 12:30 | Re-placed only the short side using confluence; kept the long off using the backtest. Inconsistent standard per side. | see S1 | Rule 5. |
| 2026-10-29 14:18 | Saw the 15m close 80,431 > 80,350 and called entering "chasing" with price at 80,420, i.e. at the planned entry. | **−1.5R missed (S1, ~$53)** | Rule 6. |
| 2026-10-29 | Sized risk at 1% swing / 0.5% scalp before checking the account's 3% max drawdown; then assumed a trailing drawdown. Propr's is static + daily. | none (caught before a loss) | Rule 1. Rules now coded in `paper_desk.py`. |
| 2026-10-29 | X1 (HYPE limit 85.5) chose a target (88.7) price had already reached before the entry could fill. | none (never filled) | Rule 8. |

## Shadow trades (skipped or cancelled plan trades)
| ID | Trade | Why skipped | Result |
|---|---|---|---|
| S1 | BTC long 80,409 (15m close > 80,350 at 14:15), stop 79,990, target 81,037.5 | Cancelled on the backtest, not re-placed, then skipped as "chasing" | **+1.50R** (target hit in the 14:30 candle, high 81,525) |

Running total: **+1.50R** missed by overriding the plan.

## What went right
- 2026-10-27 L1: tested S20 sweep long, held to target through FOMC with the stop: +1.88R.
- 2026-10-29: caught that BTC's release reaction was muted and that the short side never had a trigger; kept risk inside the
  daily floor at every step.

## Review cadence
- Every run: read **Current rules**; log any new mistake, miss or shadow trade here and in the journal.
- After every 10 closed scalps: win rate, avg R, shadow total. If shadows are net positive, I'm overriding too much; if
  the scalp book is net negative after 20, change it or cut it.
