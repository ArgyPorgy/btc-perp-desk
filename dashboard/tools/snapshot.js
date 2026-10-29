// Multi-timeframe snapshot using the dashboard's own indicator code. Read-only.
//   node tools/snapshot.js [BTCUSDT|ETHUSDT|HYPEUSDT|HOOD] [5m,15m,1h]   (default BTCUSDT, 1h,4h,1d; HOOD = Nasdaq via Yahoo)
import { DAY, dayKey, weekKey, ema, atr, vwapBands, deltaCvd, structure, fairValueGaps, consolidation, volumeProfile, dailyAuction } from '../js/indicators.js';
import { fetchGex } from '../js/gex.js';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// Behind an HTTPS proxy (the cloud desk runs), Node's fetch only uses it with NODE_USE_ENV_PROXY=1: re-run with it set.
if ((process.env.HTTPS_PROXY || process.env.https_proxy) && !process.env.NODE_USE_ENV_PROXY) {
  const r = spawnSync(process.execPath, process.argv.slice(1), { stdio: 'inherit', env: { ...process.env, NODE_USE_ENV_PROXY: '1', NODE_NO_WARNINGS: '1' } });
  process.exit(r.status ?? 1);
}

const SYM = (process.argv[2] || 'BTCUSDT').toUpperCase();
const STOCK = !SYM.endsWith('USDT'); // a Nasdaq ticker
// Binance futures REST, or the local fallback (quant/fapi.py) where fapi.binance.com is geo-blocked.
const REST = STOCK ? null : process.env.FAPI || execFileSync('python3', [fileURLToPath(new URL('../../quant/fapi.py', import.meta.url)), 'base'], { stdio: ['ignore', 'pipe', 'inherit'] }).toString().trim();
const UNIT = SYM.replace(/USDT$/, '');
const OPTIONS = { BTCUSDT: 'BTC', ETHUSDT: 'ETH' }[SYM];
const DP = UNIT === 'BTC' ? 0 : UNIT === 'HYPE' ? 3 : 2;
const get = async (u) => (await fetch(u, { headers: { 'User-Agent': 'Mozilla/5.0 (btc-perp-desk)' } })).json();
const YF = { '5m': ['5m', '60d'], '15m': ['15m', '60d'], '1h': ['60m', '730d'], '1d': ['1d', '10y'] };
const stockBars = async (tf) => { // Yahoo Finance, regular session; no taker split, so delta reads 0
  const r = (await get(`https://query1.finance.yahoo.com/v8/finance/chart/${SYM}?interval=${YF[tf][0]}&range=${YF[tf][1]}`)).chart.result[0];
  const q = r.indicators.quote[0];
  return r.timestamp.map((t, i) => ({ time: t, open: q.open[i], high: q.high[i], low: q.low[i], close: q.close[i], volume: q.volume[i] || 0, takerBuy: (q.volume[i] || 0) / 2 }))
    .filter((b) => b.close != null && (tf === '1d' || b.volume > 0));
};
const bars = async (tf) => (STOCK ? stockBars(tf) : (await get(`${REST}/fapi/v1/klines?symbol=${SYM}&interval=${tf}&limit=1500`))
  .map((k) => ({ time: k[0] / 1000, open: +k[1], high: +k[2], low: +k[3], close: +k[4], volume: +k[5], takerBuy: +k[9] })));
const f = (x, d = DP) => (x == null || !isFinite(x) ? '—' : x.toLocaleString('en-US', { maximumFractionDigits: d, minimumFractionDigits: d }));
const pct = (a, b) => `${((a / b - 1) * 100).toFixed(2)}%`;

const [prem, oiNow, oiH, fund] = STOCK ? [] : await Promise.all([
  get(`${REST}/fapi/v1/premiumIndex?symbol=${SYM}`), get(`${REST}/fapi/v1/openInterest?symbol=${SYM}`),
  get(`${REST}/futures/data/openInterestHist?symbol=${SYM}&period=1h&limit=168`), get(`${REST}/fapi/v1/fundingRate?symbol=${SYM}&limit=21`),
]);
const out = {};
const SEC = { '5m': 300, '15m': 900, '1h': 3600, '4h': 14400, '1d': DAY };
const TFS = process.argv[3] ? process.argv[3].split(',').filter((x) => SEC[x] && !(STOCK && x === '4h')) // e.g. 5m,15m,1h for scalps
  : STOCK ? ['15m', '1h', '1d'] : ['1h', '4h', '1d'];
for (const [tf, sec, swing] of TFS.map((x) => [x, SEC[x], x === '1d' ? 10 : 20])) {
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
  console.log(`  ${STOCK ? 'taker delta n/a (stock)' : `taker delta last ${k} bars: ${flow > 0 ? '+' : ''}${f(flow, 0)} ${UNIT}`}   consolidation: ${cons.state === 2 ? 'in range' : cons.state === 1 ? 'broke up w/ volume' : cons.state === -1 ? 'broke down w/ volume' : 'none'}`);
  console.log(`  order blocks: ${st.orderBlocks.map((o) => `${o.side > 0 ? 'bull' : 'bear'} ${f(o.bottom)}–${f(o.top)}`).join(', ') || 'none'}`);
  console.log(`  open FVGs: ${fv.map((g) => `${g.side > 0 ? 'bull' : 'bear'} ${f(g.bottom)}–${f(g.top)}`).join(', ') || 'none'}`);
}
if (STOCK) { console.log(`\n(${SYM} is a Nasdaq stock: regular-session candles from Yahoo; no funding, OI, taker delta or options here)`); process.exit(0); }
const oi = oiH.map((x) => +x.sumOpenInterest);
console.log(`\n=== positioning`);
console.log(`  mark ${f(+prem.markPrice, DP + 1)} index ${f(+prem.indexPrice, DP + 1)} basis ${((+prem.markPrice / +prem.indexPrice - 1) * 1e4).toFixed(1)} bp`);
console.log(`  funding now ${(+prem.lastFundingRate * 100).toFixed(4)}%  last 7d avg ${(fund.reduce((s, x) => s + +x.fundingRate, 0) / fund.length * 100).toFixed(4)}% per 8h`);
console.log(`  OI ${f(+oiNow.openInterest, 0)} ${UNIT}   24h ${pct(oi.at(-1), oi.at(-25))}   7d ${pct(oi.at(-1), oi[0])}`);
if (!OPTIONS) console.log(`  gamma: no listed options for ${UNIT} on Deribit`);
else try {
  for (const d of [7, 30, 9999]) {
    const g = await fetchGex('https://www.deribit.com/api/v2/public', d, 15000, OPTIONS);
    console.log(`  gamma ${d > 999 ? 'all' : '≤' + d + 'd'}: net ${(g.total / 1e6).toFixed(1)}M/1%  flip ${f(g.flip, 0)}  call wall ${f(g.callWall, 0)}  put wall ${f(g.putWall, 0)}  top ${g.top.slice(0, 3).map((s) => f(s.strike, 0)).join(', ')}`);
  }
} catch (e) { console.log('  gamma: Deribit error', e.message); }
