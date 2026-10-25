// Multi-timeframe snapshot using the dashboard's own indicator code. Read-only.
//   node tools/snapshot.js
import { DAY, dayKey, weekKey, ema, atr, vwapBands, deltaCvd, structure, fairValueGaps, consolidation, volumeProfile, dailyAuction } from '../js/indicators.js';
import { fetchGex } from '../js/gex.js';

const REST = 'https://fapi.binance.com';
const get = async (u) => (await fetch(u)).json();
const bars = async (tf) => (await get(`${REST}/fapi/v1/klines?symbol=BTCUSDT&interval=${tf}&limit=1500`))
  .map((k) => ({ time: k[0] / 1000, open: +k[1], high: +k[2], low: +k[3], close: +k[4], volume: +k[5], takerBuy: +k[9] }));
const f = (x, d = 0) => (x == null || !isFinite(x) ? '—' : x.toLocaleString('en-US', { maximumFractionDigits: d, minimumFractionDigits: d }));
const pct = (a, b) => `${((a / b - 1) * 100).toFixed(2)}%`;

const [prem, oiNow, oiH, fund] = await Promise.all([
  get(`${REST}/fapi/v1/premiumIndex?symbol=BTCUSDT`), get(`${REST}/fapi/v1/openInterest?symbol=BTCUSDT`),
  get(`${REST}/futures/data/openInterestHist?symbol=BTCUSDT&period=1h&limit=168`), get(`${REST}/fapi/v1/fundingRate?symbol=BTCUSDT&limit=21`),
]);
const out = {};
for (const [tf, sec, swing] of [['1h', 3600, 20], ['4h', 14400, 20], ['1d', DAY, 10]]) {
  const b = await bars(tf);
  const n = b.length - 1, c = b[n].close;
  const e200 = ema(b.map((x) => x.close), 200)[n], e50 = ema(b.map((x) => x.close), 50)[n];
  const a = atr(b);
  const st = structure(b, swing);
  const last = st.events.at(-1), prev = st.events.slice(-4);
  const w = vwapBands(b, weekKey);
  const dv = sec < DAY ? vwapBands(b, dayKey) : null;
  const dc = deltaCvd(b, false);
  const k = 12;
  const flow = dc.delta.slice(-k).reduce((s, x) => s + x, 0);
  const prof = volumeProfile(b, Math.max(0, b.length - 300), n, 48, 0.7);
  const cons = consolidation(b, a);
  const fv = fairValueGaps(b, a);
  const auc = dailyAuction(b, sec, 60);
  const hi20 = Math.max(...b.slice(-20).map((x) => x.high)), lo20 = Math.min(...b.slice(-20).map((x) => x.low));
  out[tf] = { c, e50, e200, atr: a[n], last, prev, w, dv, flow, k, prof, cons, fv, auc, ob: st.orderBlocks, sh: st.swingHigh, sl: st.swingLow, hi20, lo20, n };
  console.log(`\n=== ${tf} (${b.length} bars)  close ${f(c, 1)}`);
  console.log(`  trend:  EMA50 ${f(e50)} (${c > e50 ? 'above' : 'below'})   EMA200 ${f(e200)} (${c > e200 ? 'above' : 'below'}, ${pct(c, e200)})   ATR ${f(a[n])} (${(a[n] / c * 100).toFixed(2)}%)`);
  console.log(`  structure: last ${last.side > 0 ? 'UP' : 'DOWN'} ${last.kind} at ${f(last.level)} (${new Date(last.time * 1000).toISOString().slice(0, 16)}), recent: ${prev.map((e) => (e.side > 0 ? '↑' : '↓') + e.kind).join(' ')}`);
  console.log(`  swing high ${f(st.swingHigh?.price)}${st.swingHigh?.broken ? ' (broken)' : ''}   swing low ${f(st.swingLow?.price)}${st.swingLow?.broken ? ' (broken)' : ''}   20-bar range ${f(lo20)}–${f(hi20)}`);
  console.log(`  weekly VWAP ${f(w.vwap[n])} (${c > w.vwap[n] ? 'above' : 'below'})${dv ? `   session VWAP ${f(dv.vwap[n])} [-1σ ${f(dv.dn1[n])}, +1σ ${f(dv.up1[n])}]` : ''}`);
  console.log(`  volume profile (300 bars): POC ${f(prof.poc)}  VAH ${f(prof.vah)}  VAL ${f(prof.val)}  -> ${c > prof.vah ? 'above value' : c < prof.val ? 'below value' : 'inside value'}`);
  if (auc.prior[n]) console.log(`  prior day: POC ${f(auc.prior[n].poc)} VAH ${f(auc.prior[n].vah)} VAL ${f(auc.prior[n].val)}`);
  console.log(`  taker delta last ${k} bars: ${flow > 0 ? '+' : ''}${f(flow)} BTC   consolidation: ${cons.state === 2 ? 'in range' : cons.state === 1 ? 'broke up w/ volume' : cons.state === -1 ? 'broke down w/ volume' : 'none'}`);
  console.log(`  order blocks: ${st.orderBlocks.map((o) => `${o.side > 0 ? 'bull' : 'bear'} ${f(o.bottom)}–${f(o.top)}`).join(', ') || 'none'}`);
  console.log(`  open FVGs: ${fv.map((g) => `${g.side > 0 ? 'bull' : 'bear'} ${f(g.bottom)}–${f(g.top)}`).join(', ') || 'none'}`);
}
const oi = oiH.map((x) => +x.sumOpenInterest);
console.log(`\n=== positioning`);
console.log(`  mark ${f(+prem.markPrice, 1)} index ${f(+prem.indexPrice, 1)} basis ${((+prem.markPrice / +prem.indexPrice - 1) * 1e4).toFixed(1)} bp`);
console.log(`  funding now ${(+prem.lastFundingRate * 100).toFixed(4)}%  last 7d avg ${(fund.reduce((s, x) => s + +x.fundingRate, 0) / fund.length * 100).toFixed(4)}% per 8h`);
console.log(`  OI ${f(+oiNow.openInterest)} BTC   24h ${pct(oi.at(-1), oi.at(-25))}   7d ${pct(oi.at(-1), oi[0])}`);
try {
  for (const d of [7, 30, 9999]) {
    const g = await fetchGex('https://www.deribit.com/api/v2/public', d);
    console.log(`  gamma ${d > 999 ? 'all' : '≤' + d + 'd'}: net ${(g.total / 1e6).toFixed(1)}M/1%  flip ${f(g.flip)}  call wall ${f(g.callWall)}  put wall ${f(g.putWall)}  top ${g.top.slice(0, 3).map((s) => f(s.strike)).join(', ')}`);
  }
} catch (e) { console.log('  gamma: Deribit error', e.message); }
