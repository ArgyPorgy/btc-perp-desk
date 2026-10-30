# Desk lessons: wins, mistakes, misses and the rules they produced

Read this at the start of every run. Every closed trade gets a dated entry: wins with what made them work (so it can
be repeated), losses and misses with what went wrong (so it isn't). when it changes how the desk trades,
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
10. **Zoom out for swings.** Swings are read on 1D and 4H first (1D decides), scalps on 1m-1h. The S/R flip retest works
    on the daily chart (BTC +0.32R n=46, ETH +0.25R n=45) and is ~0R on the 4h: the timeframe is part of the setup.
11. **Outside ideas are welcome, then tested.** A trader's setup (e.g. @MuroCrypto's HYPE daily flip) gets coded and
    backtested; if it holds, it joins the scanner.
12. **A limit order is a decision made at one moment.** Scalp limits expire after 2h by default, and every run re-checks
    a pending limit against the current picture (leader, flow, structure); if the reason it was placed is gone, cancel.
13. **Check the leader.** ETH/HYPE/alt longs need BTC holding its structure (key level, 1h EMA200, gamma pin). If BTC
    breaks down while an alt long is pending, cancel; if it breaks while the alt long is open, judge the thesis, don't
    just "wait for the stop".
14. **Correlated longs count as one bet.** Two crypto longs at the same time are one risk, not two. Only one at full
    scalp size unless each has its own catalyst; otherwise size each down so the pair risks ~0.35%.
15. **Targets must clear supply.** A target beyond a call wall + bear OBs that already rejected price that day needs a
    reason; otherwise take the target before the supply (or skip if that leaves < 1.5R).
16. **Location: enter AT the zone, stop BEYOND it.** Longs are bought inside demand (bull OB / FVG / flipped level /
    put wall), with the stop below the whole zone and the swing low ("strong low"); shorts mirror that. Never a stop
    inside or on top of a demand zone, never an entry mid-range between zones. Check it on the chart (LuxAlgo-style
    OB/FVG/strong-weak high-low view) before placing; snapshot.js lists the same zones.
17. **Every order change is announced as an ORDER UPDATE** (new / moved / cancelled, with entry, stop, target) in the
    reply, so the user can mirror it. The HYPE long was moved four times (X1 85.5 -> X5 88.9 -> X6 92.2 -> X8 95.3);
    the user only had X1, so their book and the paper book diverged (X8 filled and lost; their X1 never filled).
18. **Crypto Twitter is ~30 min ahead of the news wires.** The Binance hack was on X at ~20:50 and on CoinDesk at 21:12.
    x.com is blocked here, so a rumor the user reports from X is treated as live risk at once (size down, no fresh
    longs into it, look for the tape's confirmation e.g. the exchange token underperforming), not as unconfirmed noise.
19. **No counter-trend longs during a live exchange crisis.** Until the venue resumes withdrawals or its token recovers,
    supports are temporary: the next shoe (here a withdrawal halt) breaks them. Trade with the stress or stand aside.
    Exception used 2026-10-30 04:13: a TESTED swing signal (S10/S20) after the venue token recovered most of its drop
    and official confirmation moved price < 0.2%: taken at reduced size (0.35%), with any opposing scalp closed.
20. **Never tighten a stop to just under equal lows (or over equal highs).** Two touches at the same price are where
    everyone's stops sit, and they get swept. Tighten only to beyond a level that was already swept, or at least
    0.5 ATR(15m) past the structure; otherwise leave the original invalidation stop alone.

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
| 2026-10-29 | HYPE news trend 79 -> 97 (+22%): three pullback limits (X1 85.5, X5 88.9, X6 92.2) each set 3-6% under price, each left behind; moved up only after price ran. | missed most of the move (no fill, no loss) | In a news-driven trend (OI rising, funding normal, strong taker delta) pullbacks are shallow: set entries at the nearest structure (last 5m/15m breakout level, 15m EMA20), or split: half at the shallow level, half deeper. |
| 2026-10-29 17:50 | **X8** HYPE long 95.30 stopped at 93.90 (−1.07R, −$38). Low 93.67 in the 17:45 candle, then 93.05, back to 94.3 within 15 min. The stop was 1.5% away while HYPE's 1h ATR was 1.8%: a noise stop for a trade meant to last hours, placed at an obvious level (just under 93.8) where stops cluster. | −$38 | Scalp stops go beyond the nearest swing low AND at least ~1x the 1h ATR from entry (size down to keep $ risk); never just under an obvious level. |
| 2026-10-29 18:35 | **X7** ETH long 2,350 stopped at 2,326 (−1.10R, −$39). Placed 15:40 as a breakout-retest while BTC was ripping; it filled at 17:05, 85 min later, AFTER BTC had rejected the 82k call wall (81,944 at 16:00) and lost the 81k pin, and after ETH itself had been rejected at 2,378.8 with 15m delta −18k (16:15). I flagged "risk: BTC" at 17:16 and held. ETH then lost the old range top 2,330 with BTC under its 1h EMA200: the breakout failed (a real thesis loss, not a wick). The target 2,398 also sat behind the 2,360 call wall and bear OBs 2,365–2,391 that had rejected price. And X7 + X8 were two correlated crypto longs filled 25 min apart: both lost (−$77 together). | −$39 (−$77 with X8) | Rules 12–15: stale limits expire/re-check, leader check, correlated longs = one bet, targets must clear supply. Done right: stop honoured, loss = the planned 0.35%, floors never in danger. |
| 2026-10-29 18:40 | User (LuxAlgo chart): "your stop is where the bounce is supposed to come from; you took the trade in the middle." True: X7's entry 2,350 was mid-range; its stop 2,326 sat on top of the demand zone (5m bull OB 2,312–2,325, 15m bull OB 2,296–2,313, put wall 2,300, strong low 2,292), all printed in my own snapshot. ETH then traded straight into that zone. | part of X7's −$39 | Rule 16 (location). Re-entered correctly as X10a/b: limits 2,322 / 2,312 inside the zone, stop 2,288 below it, target 2,362 before supply. |
| 2026-10-29 21:12 | **X14** BTC short 79,150: the stop (79,650) sat inside the 5m bear FVG 79,099–79,750, so a normal fill-the-gap squeeze would take it out; and the short was entered as the catalyst (Binance panic) was already fading (BNB bouncing). Closed at −0.18R. | −$6 | Rule 16 applies to shorts too: stop ABOVE the whole supply zone. Re-check the catalyst before a limit fills (rule 12). |
| 2026-10-29 23:45 | **X17** BTC base long 78,650 stopped at 78,450 (−0.56R, −$11). Bought the 78.2k base during an escalating exchange crisis; at 23:37 "Binance halts withdrawals amid $5.3B hack" broke the base to 77,896. Done right: the stop was tightened from 78,150 under the higher low at 22:12, so the loss was $11 instead of $20 (77,896 took out both). | −$11 | Rule 19: no counter-trend longs during a live exchange crisis. |
| 2026-10-30 13:50 | **SW1a/SW1b** (open, −0.75R): the tested S10/S20 stop (0.1% under the 76,472 sweep wick = 76,395.5) sits INSIDE the 4h/1d demand the user flagged (4h bull OB 74,909–77,324, daily FVG 73,400–76,510, daily EMA200 76,423). A normal sweep into that support takes the stop before the bounce. Rule 16 was checked for scalps but not for the mechanical swing stop. | open; ≤ −1R if hit | A tested setup's stop is kept (never widened), but check it against the HTF zones at entry. When it sits inside support, plan the re-entry at the zone with the stop beyond it at the same time (done late here: X23 limit 75,700 / stop 74,750). Backlog: test S10/S20 with the stop under the nearest 4h/1d order block instead of the wick. |
| 2026-10-30 14:10 | **X22** HYPE range-floor long 90.85 stopped at 90.60 (−0.57R, −$14). At +1R I tightened the stop from 90.25 to 90.60, 0.1 under the post-fill double low 90.70/90.72, because BTC lost 77k. HYPE swept those equal lows to 90.51 and turned back up to 90.9; the original stop 90.25 was never touched. | −$14 actual; the untightened plan (SH7) hit 92.3 by 15:14 = +2.42R, so the tightening cost ~3R (~$75) | Rule 20. Cutting risk was right in spirit (BTC breaking support); parking the stop on obvious liquidity was the mistake. Better: scale out half, or leave the stop at the real invalidation. |

## Shadow trades (skipped or cancelled plan trades)
| ID | Trade | Why skipped | Result |
|---|---|---|---|
| S1 | BTC long 80,409 (15m close > 80,350 at 14:15), stop 79,990, target 81,037.5 | Cancelled on the backtest, not re-placed, then skipped as "chasing" | **+1.50R** (target hit in the 14:30 candle, high 81,525) |

Running total: **+1.50R** missed by overriding the plan.

## Wins: what made them work
| Date (UTC) | Trade | Result | What made it work (repeat this) |
|---|---|---|---|
| 2026-10-27 | **L1** BTC swing long 79,752 → 81,057 (S20: 4h sweep of the 20-day low 79,179, closed back above) | **+1.88R, +$187.68** | Tested setup, entered at the 4h close exactly as specified; stop under the sweep wick (real invalidation); held one-shot through FOMC as the event study allowed, no early exit despite three tests of 81k; target sat under the 81k put wall. @MuroCrypto called the same "bounce below 80" that day: independent reads agreed. |
| 2026-10-29 | **S1** (shadow) BTC release breakout long 80,409 → 81,037 | +1.50R (missed) | The plan itself was right: two-sided OCO around the 80k gamma pin, entry only on a 15m close out of the range, stop back inside. Hot PCE was absorbed (taker flow flipped +1k), so the break came up. Lesson: trust the two-sided plan (rules 5-6). |
| 2026-10-29 | **D1F** HYPE (scanner, retro-check): daily close 76.65 on Oct 24 retesting a flipped level (73.0) above a rising SMA100, stop 69.2 | 2R target 91.57 traded today (+2R) | Zoomed-out daily structure + trend filter; the same trade @MuroCrypto posted on Oct 26 at ~77.3 (+17%). Not a desk trade (setup added today); logged so the pattern's live record starts here. |
| 2026-10-29 20:35 | **X13** BTC scalp short 80,420 -> 79,880 | **+1.64R, +$33.20** | Reacted to a top-impact headline (Iran naval blockade) the same run; shorted the RETEST of the broken gamma flip inside a 15m bear FVG (location at supply, rule 16), stop above the FVG and 1h EMA50, target in front of the next bull OB; sized 0.2% for the day stop. |
| 2026-10-29 20:14 | **Early exit** of X11a/X11c ETH longs at 2,314 (−$3.89 total) | saved ~$36 (shadows S2/S3 both hit the 2,288 stop) | Rule 13 worked: the leader (BTC) broke its gamma flip on new risk-off news, so the zone thesis was re-judged instead of waiting for the stop. |
| 2026-10-29 21:12 | **X14 exit** at 79,158 (−$6) | saved ~$29 (shadow S4: stop 79,650 hit at 21:15, high 79,766) | Read the base forming (three held lows, fading delta, trapped OI, BNB bouncing) and the stop sitting inside a bear FVG; cut instead of hoping. |
| 2026-10-30 01:35 | **X15** BTC short 77,967 -> 76,700 (base-break continuation) | **+1.21R, +$24.50** | Two-sided plan kept both sides: when the 78.2k base broke on the withdrawal-halt news, the short side triggered on a 15m close (no anticipation). Stop tightened only to structure (78,300, above the broken base) as BNB bounced; target set ahead of the next level. |
| 2026-10-30 04:13 | **X19 exit** at 78,050 (−$12) when the tested S10/S20 long fired | saved ~$8 (shadow S5: stop 78,350 hit) | Didn't hold a scalp against a tested opposite signal; flipped to the tested side at reduced size. |

## Process wins
- 2026-10-29: kept every order inside the daily-loss floor; cancelled X4 when BTC broke the other way instead of hoping.
- 2026-10-29: the news terminal caught the ICE/NYSE Hyperliquid catalyst the hour it moved HYPE.

## Review cadence
- Every run: read **Current rules**; log any new mistake, miss or shadow trade here and in the journal.
- After every 10 closed scalps: win rate, avg R, shadow total. If shadows are net positive, I'm overriding too much; if
  the scalp book is net negative after 20, change it or cut it.
