// Perp Desk: live Binance USDⓈ-M data (BTC, ETH, HYPE) and Nasdaq HOOD -> charts, order flow and context, computed locally.
import { MARKETS, MARKET, SYMBOL, STOCK, REST, WS_MARKET, WS_PUBLIC, DERIBIT, TIMEFRAMES, OI_PERIOD, HEATMAP_EVERY_SEC } from './config.js';
import { DAY, dayKey, weekKey, ema, atr, vwapBands, deltaCvd, structure, fairValueGaps, consolidation,
  volumeProfile, dailyAuction, scorecard, fmtQty } from './indicators.js';
import { OrderBook, Heatmap } from './book.js';
import { Footprint, backfillAggTrades } from './footprint.js';
import { fetchGex } from './gex.js';
import { BoxesPrimitive, ProfilePrimitive, HeatmapPrimitive } from './primitives.js';
import { News } from './news.js';

const LC = window.LightweightCharts;
const $ = (id) => document.getElementById(id);
const sym = SYMBOL.toLowerCase();

// ───────── settings (remembered in this browser)
const LAYERS = [['heatmap', 'Liquidity heatmap'], ['profile', 'Volume profile'], ['structure', 'BOS / CHoCH'],
  ['orderBlocks', 'Order blocks'], ['fvg', 'Fair value gaps'], ['consolidation', 'Consolidation ranges'],
  ['vwap', 'Session VWAP + bands'], ['weeklyVwap', 'Weekly VWAP'], ['priorValue', 'Prior-day value area'],
  ['ib', 'Initial balance'], ['gamma', 'Gamma levels'], ['liquidations', 'Liquidation markers'], ['ema200', 'EMA 200'],
  ['news', 'News markers (high impact)']];
const DEFAULTS = { tf: '15m', swingLen: 20, profileBars: 300, flowBars: 12, gexDays: 30, fpTf: 60 };
for (const [k] of LAYERS) DEFAULTS[k] = true;
const settings = (() => { try { return { ...DEFAULTS, ...JSON.parse(localStorage.getItem('btc-perp-desk') || '{}') }; } catch { return { ...DEFAULTS }; } })();
const save = () => { try { localStorage.setItem('btc-perp-desk', JSON.stringify(settings)); } catch { /* storage unavailable */ } };

// ───────── state
const startTf = TIMEFRAMES[settings.tf] ? settings.tf : '1h'; // stocks have no 4h
const S = { tf: startTf, tfSec: TIMEFRAMES[startTf], bars: [], stock: null, stockAt: 0, last: null, mark: null, index: null, funding: null,
  nextFunding: null, oiNow: null, oiHist: [], oiAligned: [], gex: null, liqs: [], tape: [], health: { market: 0, public: 0 },
  restDiff: null, ind: null };

// bars are regular, but be robust to gaps: logical index = position of the bar holding t + fraction inside it
function timeToLogical(t) {
  const b = S.bars;
  if (!b.length) return 0;
  let lo = 0, hi = b.length - 1;
  if (t >= b[hi].time) return hi + (t - b[hi].time) / S.tfSec;
  if (t <= b[0].time) return (t - b[0].time) / S.tfSec;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (b[m].time <= t) lo = m; else hi = m; }
  return lo + (t - b[lo].time) / (b[hi].time - b[lo].time);
}

// ───────── charts
const tickFmt = (t, type) => {
  const d = new Date(t * 1000);
  return type <= 2 ? d.toLocaleDateString([], { month: 'short', day: 'numeric' })
    : d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
};
const base = {
  layout: { background: { type: 'solid', color: '#0b0e14' }, textColor: '#9aa4b2', fontSize: 11 },
  grid: { vertLines: { color: '#141a23' }, horzLines: { color: '#141a23' } },
  rightPriceScale: { borderColor: '#1f2632', minimumWidth: 78 },
  timeScale: { borderColor: '#1f2632', timeVisible: true, secondsVisible: false, tickMarkFormatter: tickFmt, rightOffset: 12 },
  crosshair: { mode: LC.CrosshairMode.Normal },
  localization: { timeFormatter: (t) => new Date(t * 1000).toLocaleString([], { hour12: false }) },
  autoSize: true,
};
const main = LC.createChart($('chartMain'), base);
// lower panes follow the main chart (scroll / zoom the main chart); they don't drive it
const follower = { ...base, timeScale: { ...base.timeScale, visible: false }, handleScroll: false, handleScale: false };
const cvdChart = LC.createChart($('chartCvd'), follower);
const oiChart = LC.createChart($('chartOi'), follower);

const candles = main.addCandlestickSeries({ upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
  wickUpColor: '#26a69a', wickDownColor: '#ef5350' });
const volS = main.addHistogramSeries({ priceFormat: { type: 'volume' }, priceScaleId: 'vol', lastValueVisible: false, priceLineVisible: false });
main.priceScale('vol').applyOptions({ scaleMargins: { top: 0.86, bottom: 0 } });
// overlays never stretch the price scale: only candles decide the vertical zoom
const line = (opts) => main.addLineSeries({ lineWidth: 1, priceLineVisible: false, lastValueVisible: false, crosshairMarkerVisible: false,
  autoscaleInfoProvider: () => null, ...opts });
const L = {
  ema: line({ color: 'rgba(179,157,219,0.8)' }),
  vw: line({ color: '#4285f4', lineWidth: 2 }),
  vwU1: line({ color: 'rgba(66,133,244,0.45)' }), vwD1: line({ color: 'rgba(66,133,244,0.45)' }),
  vwU2: line({ color: 'rgba(66,133,244,0.22)' }), vwD2: line({ color: 'rgba(66,133,244,0.22)' }),
  wvw: line({ color: '#ff9800', lineWidth: 2 }),
  pPoc: line({ color: 'rgba(247,201,72,0.7)', lineType: LC.LineType.WithSteps, lineStyle: LC.LineStyle.Dashed }),
  pVah: line({ color: 'rgba(186,104,200,0.7)', lineType: LC.LineType.WithSteps, lineStyle: LC.LineStyle.Dashed }),
  pVal: line({ color: 'rgba(186,104,200,0.7)', lineType: LC.LineType.WithSteps, lineStyle: LC.LineStyle.Dashed }),
  ibH: line({ color: 'rgba(160,170,180,0.6)', lineType: LC.LineType.WithSteps, lineStyle: LC.LineStyle.Dotted }),
  ibL: line({ color: 'rgba(160,170,180,0.6)', lineType: LC.LineType.WithSteps, lineStyle: LC.LineStyle.Dotted }),
};
const heatP = new HeatmapPrimitive(timeToLogical, HEATMAP_EVERY_SEC, S.tfSec);
const boxP = new BoxesPrimitive(timeToLogical);
const profP = new ProfilePrimitive(timeToLogical);
candles.attachPrimitive(heatP);
candles.attachPrimitive(boxP);
candles.attachPrimitive(profP);

const deltaS = cvdChart.addHistogramSeries({ priceLineVisible: false, lastValueVisible: false, priceFormat: { type: 'volume' } });
const cvdS = cvdChart.addLineSeries({ priceScaleId: 'cvd', color: '#f7c948', lineWidth: 2, priceLineVisible: false, lastValueVisible: false });
cvdChart.priceScale('cvd').applyOptions({ scaleMargins: { top: 0.1, bottom: 0.1 } });
const oiS = oiChart.addLineSeries({ color: '#80cbc4', lineWidth: 2, priceLineVisible: false, priceFormat: { type: 'volume' } });

const followMain = () => {
  const r = main.timeScale().getVisibleLogicalRange();
  if (r) for (const c of [cvdChart, oiChart]) c.timeScale().setVisibleLogicalRange(r);
};
main.timeScale().subscribeVisibleLogicalRangeChange(followMain);
main.subscribeCrosshairMove((p) => {
  if (!p.time || !cvdChart.setCrosshairPosition) { cvdChart.clearCrosshairPosition?.(); oiChart.clearCrosshairPosition?.(); return; }
  const i = S.bars.findIndex((b) => b.time === p.time);
  if (i < 0 || !S.ind) return;
  cvdChart.setCrosshairPosition(S.ind.dc.delta[i], p.time, deltaS);
  if (S.oiAligned[i] != null) oiChart.setCrosshairPosition(S.oiAligned[i], p.time, oiS);
});

// ───────── helpers
const getJSON = async (url) => { const r = await fetch(url); if (!r.ok) throw new Error(`${r.status} ${url}`); return r.json(); };
const toBar = (k) => ({ time: k[0] / 1000, open: +k[1], high: +k[2], low: +k[3], close: +k[4], volume: +k[5], takerBuy: +k[9] });
const fmtP = (x, d = MARKET.dp) => (x == null || !isFinite(x) ? '—' : (+x).toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d }));
const series = (arr, f = (x) => x) => S.bars.map((b, i) => (arr[i] == null || !isFinite(f(arr[i])) ? { time: b.time } : { time: b.time, value: f(arr[i]) }));

// ───────── data loading
async function loadStock(tf) { // Nasdaq candles via server.py (Yahoo Finance), Binance kline layout
  const r = await getJSON(`api/stock?symbol=${SYMBOL}&tf=${tf}`);
  if (r.error) throw new Error(r.error);
  S.stock = r.meta; S.stockAt = Date.now();
  return r.bars.map(toBar);
}

async function loadBars(tf) {
  if (STOCK) return loadStock(tf);
  const need = tf === '1m' ? 3000 : 1500;
  let bars = [], end = null;
  while (bars.length < need) {
    const k = await getJSON(`${REST}/fapi/v1/klines?symbol=${SYMBOL}&interval=${tf}&limit=1500${end ? `&endTime=${end}` : ''}`);
    if (!k.length) break;
    const page = k.map(toBar);
    bars = page.concat(bars.filter((b) => b.time > page[page.length - 1].time));
    end = k[0][0] - 1;
    if (k.length < 1500) break;
  }
  return bars.slice(-need);
}

async function loadOiHistory(tf) {
  if (STOCK) { S.oiHist = []; return; }
  try {
    const h = await getJSON(`${REST}/futures/data/openInterestHist?symbol=${SYMBOL}&period=${OI_PERIOD[tf]}&limit=500`);
    S.oiHist = h.map((x) => ({ t: x.timestamp / 1000, oi: +x.sumOpenInterest }));
  } catch (e) { console.warn('OI history', e); S.oiHist = []; }
}

function alignOi() {
  const out = new Array(S.bars.length).fill(null);
  let j = 0;
  for (let i = 0; i < S.bars.length; i++) {
    while (j + 1 < S.oiHist.length && S.oiHist[j + 1].t <= S.bars[i].time) j++;
    if (S.oiHist.length && S.oiHist[j].t <= S.bars[i].time + S.tfSec) out[i] = S.oiHist[j].oi;
  }
  if (S.oiNow != null && out.length) out[out.length - 1] = S.oiNow;
  S.oiAligned = out;
}

// ───────── sockets with auto-reconnect
function socket(url, onMsg, key, onReopen) {
  let ws, timer, alive = true, opened = false;
  const connect = () => {
    ws = new WebSocket(url);
    ws.onopen = () => { if (opened && onReopen) onReopen(); opened = true; };
    ws.onmessage = (m) => { S.health[key] = Date.now(); onMsg(JSON.parse(m.data)); };
    ws.onclose = () => { if (alive) timer = setTimeout(connect, 2000); };
    ws.onerror = () => ws.close();
  };
  connect();
  return { close() { alive = false; clearTimeout(timer); ws.close(); } };
}

const book = new OrderBook(() => getJSON(`${REST}/fapi/v1/depth?symbol=${SYMBOL}&limit=1000`));
const heat = new Heatmap(HEATMAP_EVERY_SEC);
if (!STOCK) socket(`${WS_PUBLIC}${sym}@depth@100ms`, (m) => book.onEvent(m.data), 'public');

let marketWs = null, stockTimer = null;
function openMarket() {
  if (STOCK) { // no stream for Nasdaq: poll the server (it caches Yahoo for 10s)
    clearInterval(stockTimer);
    stockTimer = setInterval(async () => {
      try {
        const tf = S.tf, bars = await loadStock(tf);
        if (tf !== S.tf || !bars.length) return;
        S.bars = bars; S.last = bars[bars.length - 1].close;
        setAllData();
      } catch (e) { console.warn('stock poll', e); }
    }, 15000);
    return;
  }
  if (marketWs) marketWs.close();
  marketWs = socket(`${WS_MARKET}${sym}@kline_${S.tf}/${sym}@aggTrade/${sym}@markPrice@1s/${sym}@forceOrder`, onMarket, 'market', gapFill);
}

function onMarket(m) {
  const d = m.data;
  if (d.e === 'aggTrade') onTrade(d);
  else if (d.e === 'kline' && d.k.i === S.tf) onKline(d.k);
  else if (d.e === 'markPriceUpdate') { S.mark = +d.p; S.index = +d.i; S.funding = +d.r; S.nextFunding = d.T; }
  else if (d.e === 'forceOrder') onLiquidation(d.o);
}

function onKline(k) {
  const bar = { time: k.t / 1000, open: +k.o, high: +k.h, low: +k.l, close: +k.c, volume: +k.v, takerBuy: +k.V };
  const b = S.bars;
  if (!b.length || bar.time < b[b.length - 1].time) return;
  const isNew = bar.time > b[b.length - 1].time;
  if (isNew) b.push(bar); else b[b.length - 1] = bar;
  candles.update(bar);
  volS.update({ time: bar.time, value: bar.volume, color: bar.close >= bar.open ? 'rgba(38,166,154,0.35)' : 'rgba(239,83,80,0.35)' });
  if (isNew || k.x) recompute(); else scheduleRecompute();
}

async function gapFill() { // after a reconnect: refetch recent bars so no candle is missed
  try {
    const k = await getJSON(`${REST}/fapi/v1/klines?symbol=${SYMBOL}&interval=${S.tf}&limit=200`);
    const fresh = k.map(toBar);
    S.bars = S.bars.filter((b) => b.time < fresh[0].time).concat(fresh);
    setAllData();
  } catch (e) { console.warn('gap fill', e); }
}

// ───────── trades: tape + footprint
const fpTickKey = `fpTick_${SYMBOL}`; // footprint row size is per market
let fp = new Footprint(settings.fpTf, 40, MARKET.fpBase), fpReady = false, fpBuffer = [], fpMaxId = 0;
function onTrade(d) {
  S.last = +d.p;
  const t = { p: d.p, q: d.q, T: d.T, m: d.m, a: d.a };
  if (fpReady) { if (d.a > fpMaxId) { fp.add(t); fpMaxId = d.a; } } else fpBuffer.push(t);
  const min = +$('tapeMin').value || 0;
  if (+d.q >= min) { S.tape.unshift(t); if (S.tape.length > 200) S.tape.length = 200; tapeDirty = true; }
}

async function startFootprint() {
  if (STOCK) return;
  fp = new Footprint(settings.fpTf, 40, MARKET.fpBase); fpReady = false; fpBuffer = []; fpMaxId = 0;
  const now = Date.now();
  const startMs = Math.floor((now - Math.min(20 * 60e3, 30 * settings.fpTf * 1e3)) / (settings.fpTf * 1e3)) * settings.fpTf * 1e3;
  $('fpInfo').textContent = 'loading recent trades…';
  try {
    const r = await backfillAggTrades(REST, SYMBOL, startMs, (t) => { fp.add(t); fpMaxId = Math.max(fpMaxId, t.a); }, { maxRequests: 60 });
    if (!r.complete && isFinite(r.oldestMs)) { // budget ran out: drop the oldest, partially loaded candle
      const partial = Math.floor(r.oldestMs / 1000 / settings.fpTf) * settings.fpTf;
      fp.candles.delete(partial);
      fp.since = partial + settings.fpTf;
    }
  } catch (e) { console.warn('footprint backfill', e); }
  for (const t of fpBuffer) if (t.a > fpMaxId) { fp.add(t); fpMaxId = t.a; }
  fpBuffer = []; fpReady = true;
  $('fpInfo').textContent = `complete candles since ${new Date((fp.since || now / 1000) * 1000).toLocaleTimeString([], { hour12: false })}`;
}

function onLiquidation(o) {
  const l = { side: o.S === 'SELL' ? 'long' : 'short', qty: +o.q, price: +(o.ap || o.p), T: o.T };
  S.liqs.unshift(l);
  if (S.liqs.length > 100) S.liqs.length = 100;
  renderLiqs();
  setMarkers();
}

// ───────── indicators -> chart
let recomputeTimer = null;
function scheduleRecompute() { if (!recomputeTimer) recomputeTimer = setTimeout(() => { recomputeTimer = null; recompute(); }, 1500); }

function recompute() {
  const b = S.bars;
  if (b.length < 60) return;
  const intraday = S.tfSec < DAY;
  const atrA = atr(b);
  const ind = {
    ema: ema(b.map((x) => x.close), 200),
    v: intraday ? vwapBands(b, dayKey) : null,
    w: vwapBands(b, weekKey),
    dc: deltaCvd(b, true),
    st: structure(b, settings.swingLen),
    fvg: fairValueGaps(b, atrA),
    cons: consolidation(b, atrA),
    prof: volumeProfile(b, Math.max(0, b.length - settings.profileBars), b.length - 1, 48, 0.7),
    auc: dailyAuction(b, S.tfSec, 60),
  };
  S.ind = ind;
  alignOi();
  const on = (k, data) => (settings[k] ? data : []);
  L.ema.setData(on('ema200', series(ind.ema)));
  for (const [s, key] of [[L.vw, 'vwap'], [L.vwU1, 'up1'], [L.vwD1, 'dn1'], [L.vwU2, 'up2'], [L.vwD2, 'dn2']])
    s.setData(on('vwap', ind.v ? series(ind.v[key]) : []));
  L.wvw.setData(on('weeklyVwap', series(ind.w.vwap)));
  L.pPoc.setData(on('priorValue', series(ind.auc.prior, (x) => x?.poc)));
  L.pVah.setData(on('priorValue', series(ind.auc.prior, (x) => x?.vah)));
  L.pVal.setData(on('priorValue', series(ind.auc.prior, (x) => x?.val)));
  L.ibH.setData(on('ib', series(ind.auc.ib, (x) => x?.hi)));
  L.ibL.setData(on('ib', series(ind.auc.ib, (x) => x?.lo)));
  deltaS.setData(b.map((x, i) => ({ time: x.time, value: ind.dc.delta[i], color: ind.dc.delta[i] >= 0 ? 'rgba(38,166,154,0.7)' : 'rgba(239,83,80,0.7)' })));
  cvdS.setData(b.map((x, i) => ({ time: x.time, value: ind.dc.cvd[i] })));
  oiS.setData(series(S.oiAligned));
  followMain(); // setData can move the lower panes; snap them back to the main chart

  const items = [];
  if (settings.structure) for (const e of ind.st.events.slice(-12))
    items.push({ kind: 'line', t1: b[e.fromIdx].time, t2: e.time, price: e.level, color: e.side > 0 ? 'rgba(38,166,154,0.9)' : 'rgba(239,83,80,0.9)',
      dash: [4, 3], label: e.kind, labelBelow: e.side < 0 });
  if (settings.orderBlocks) for (const ob of ind.st.orderBlocks)
    items.push({ t1: ob.time, t2: null, top: ob.top, bottom: ob.bottom, fill: ob.side > 0 ? 'rgba(38,166,154,0.12)' : 'rgba(239,83,80,0.12)',
      stroke: ob.side > 0 ? 'rgba(38,166,154,0.5)' : 'rgba(239,83,80,0.5)', label: ob.side > 0 ? 'Bull OB' : 'Bear OB' });
  if (settings.fvg) for (const g of ind.fvg)
    items.push({ t1: g.time, t2: null, top: g.top, bottom: g.bottom, fill: g.side > 0 ? 'rgba(38,166,154,0.08)' : 'rgba(239,83,80,0.08)',
      label: 'FVG', labelColor: g.side > 0 ? 'rgba(38,166,154,0.8)' : 'rgba(239,83,80,0.8)' });
  if (settings.consolidation) for (const r of ind.cons.ranges.slice(-8))
    items.push({ t1: b[r.start].time, t2: b[Math.min(r.end, b.length - 1)].time, top: r.top, bottom: r.bottom, fill: 'rgba(140,148,160,0.08)',
      stroke: 'rgba(140,148,160,0.45)', label: r.active ? 'range' : r.result > 0 ? 'range ▲' : r.result < 0 ? 'range ▼' : '' });
  boxP.set(items);
  profP.visible = settings.profile;
  profP.set(ind.prof, b[Math.max(0, b.length - settings.profileBars)].time);
  heatP.visible = settings.heatmap;
  heatP.set(heat.cols, S.tfSec);
  setMarkers();
  renderScore();
}

function setAllData() {
  candles.setData(S.bars);
  volS.setData(S.bars.map((x) => ({ time: x.time, value: x.volume, color: x.close >= x.open ? 'rgba(38,166,154,0.35)' : 'rgba(239,83,80,0.35)' })));
  recompute();
}

function setMarkers() {
  const m = [];
  const ind = S.ind;
  if (ind && settings.consolidation) for (const r of ind.cons.ranges) if (r.result && r.breakIdx != null && S.bars[r.breakIdx])
    m.push({ time: S.bars[r.breakIdx].time, position: r.result > 0 ? 'belowBar' : 'aboveBar', color: r.result > 0 ? '#26a69a' : '#ef5350',
      shape: r.result > 0 ? 'arrowUp' : 'arrowDown', text: r.result > 0 ? 'vol breakout' : 'vol breakdown' });
  if (settings.liquidations && S.bars.length) for (const l of S.liqs) {
    const t = Math.floor(l.T / 1000 / S.tfSec) * S.tfSec;
    if (t < S.bars[0].time) continue;
    m.push({ time: t, position: l.side === 'long' ? 'belowBar' : 'aboveBar', color: l.side === 'long' ? '#ef5350' : '#26a69a',
      shape: 'circle', size: l.qty * l.price > 250000 ? 2 : 1, text: l.qty * l.price > 250000 ? `liq ${(l.qty * l.price / 1e6).toFixed(1)}M` : '' });
  }
  if (settings.news) m.push(...news.markers(S.bars, S.tfSec));
  m.sort((a, b) => a.time - b.time);
  candles.setMarkers(m);
}

// ───────── panels
function renderScore() {
  const b = S.bars, i = b.length - 1, ind = S.ind;
  if (!ind) return;
  const n = Math.min(settings.flowBars, i);
  const last = b[i];
  const oiA = S.oiAligned;
  const sc = scorecard({
    close: last.close, high: last.high, low: last.low, ema200: b.length >= 200 ? ind.ema[i] : null,
    vwap: ind.v?.vwap[i], up1: ind.v?.up1[i], dn1: ind.v?.dn1[i],
    lastBreak: ind.st.lastBreak, lastKind: ind.st.events.length ? ind.st.events[ind.st.events.length - 1].kind : '',
    profile: ind.prof, prior: ind.auc.prior[i],
    cvdChange: ind.dc.delta.slice(i - n + 1).reduce((a, x) => a + x, 0), flowBars: n, priceChange: last.close - b[i - n].close,
    oiChangePct: oiA[i] != null && oiA[i - n] != null ? (oiA[i] - oiA[i - n]) / oiA[i - n] * 100 : null,
    funding: S.funding, bookImbalance: book.synced ? book.imbalance(0.005) : null,
    gex: settings.gamma ? S.gex : null, consState: ind.cons.state, unit: MARKET.unit, noOptions: !MARKET.options, stock: STOCK,
  });
  $('score').innerHTML = sc.rows.map((r) => `<tr><td>${r.name}</td><td class="${r.score > 0 ? 'up' : r.score < 0 ? 'down' : 'muted'}">${r.score > 0 ? '▲' : r.score < 0 ? '▼' : '•'}</td><td class="${r.score > 0 ? 'up' : r.score < 0 ? 'down' : ''}">${r.text}</td></tr>`).join('');
  $('net').textContent = `net ${sc.net > 0 ? '+' : ''}${sc.net}`;
  $('net').className = `pill ${sc.net > 0 ? 'up' : sc.net < 0 ? 'down' : ''}`;
}

let gexLines = [], gexRetry = null;
async function refreshGex() {
  clearTimeout(gexRetry);
  if (!MARKET.options) { $('gex').textContent = `No listed options for ${MARKET.label} on Deribit, so no gamma levels.`; return; }
  try {
    S.gex = await fetchGex(DERIBIT, settings.gexDays, 15000, MARKET.options);
    $('gexWhen').textContent = `${settings.gexDays >= 9999 ? 'all expiries' : `≤${settings.gexDays}d`} · ${new Date().toLocaleTimeString([], { hour12: false })}`;
  } catch (e) {
    console.warn('gex', e);
    $('gex').textContent = `Deribit unreachable from this browser (${e.name === 'TimeoutError' ? 'timed out' : e.message}). `
      + 'An ad/privacy blocker can cause this. Retrying every minute.';
    gexRetry = setTimeout(refreshGex, 60e3);
    return;
  }
  const g = S.gex;
  $('gex').innerHTML = `<table>
    <tr><td>Net gamma</td><td class="${g.total > 0 ? 'up' : 'down'}">$${(g.total / 1e6).toFixed(1)}M / 1% ${g.total > 0 ? '(dampening)' : '(amplifying)'}</td></tr>
    <tr><td>Gamma flip</td><td>${isFinite(g.flip) ? fmtP(g.flip, 0) : 'none in ±25%'}</td></tr>
    <tr><td>Call wall</td><td class="up">${fmtP(g.callWall, 0)}</td></tr>
    <tr><td>Put wall</td><td class="down">${fmtP(g.putWall, 0)}</td></tr>
    ${g.top.slice(0, 4).map((s) => `<tr><td class="muted">${fmtP(s.strike, 0)}</td><td class="muted">calls ${(s.calls / 1e6).toFixed(0)}M · puts ${(s.puts / 1e6).toFixed(0)}M</td></tr>`).join('')}
  </table><p class="muted tiny">Strike walls are solid; the dealer long/short sign is an assumption.</p>`;
  drawGexLines();
  renderScore();
}
function drawGexLines() {
  for (const l of gexLines) candles.removePriceLine(l);
  gexLines = [];
  const g = S.gex;
  if (!g || !settings.gamma) return;
  const add = (price, color, title) => { if (isFinite(price)) gexLines.push(candles.createPriceLine({ price, color, lineWidth: 1, lineStyle: LC.LineStyle.LargeDashed, axisLabelVisible: true, title })); };
  add(g.flip, '#e040fb', 'γ flip');
  add(g.callWall, '#26a69a', 'call wall');
  add(g.putWall, '#ef5350', 'put wall');
}

// ───────── paper desk overlay: entry / stop / target of this market's open positions and pending orders
let paperLines = [];
async function refreshPaper() {
  let st;
  try { st = await getJSON('api/paper'); } catch { return; } // page not served by server.py
  for (const l of paperLines) candles.removePriceLine(l);
  paperLines = [];
  const mine = (x) => (x.symbol || 'BTCUSDT') === SYMBOL;
  const add = (price, color, title, style = LC.LineStyle.Solid) => { if (price != null && isFinite(price)) paperLines.push(candles.createPriceLine({ price: +price, color, lineWidth: 2, lineStyle: style, axisLabelVisible: true, title })); };
  for (const p of (st.positions || []).filter(mine)) {
    add(p.entry, '#4fc3f7', `${p.id} ${p.side} entry`);
    add(p.stop, '#ef5350', `${p.id} stop`, LC.LineStyle.Dashed);
    add(p.target, '#26a69a', `${p.id} target`, LC.LineStyle.Dashed);
  }
  for (const o of (st.orders || []).filter(mine)) {
    const lvl = o.level, stop = typeof o.stop === 'number' ? o.stop : null;
    const tgt = o.target ?? (stop != null && lvl != null ? lvl + (lvl - stop) * (o.target_r || 0) : null);
    add(lvl, '#b39ddb', `${o.id} ${o.side} ${o.trigger === 'limit' ? 'limit' : (o.tf || '4h') + ' ' + o.trigger.replace('_', ' ')}`, LC.LineStyle.Dotted);
    add(stop, 'rgba(239,83,80,0.6)', `${o.id} stop`, LC.LineStyle.Dotted);
    add(tgt, 'rgba(38,166,154,0.6)', `${o.id} target`, LC.LineStyle.Dotted);
  }
  if (st.equity) $('paper').textContent = `${((st.equity / st.start_equity - 1) * 100).toFixed(2)}% · ${(st.positions || []).length} open · ${(st.orders || []).length} pending`;
}
setInterval(refreshPaper, 30000);

let tapeDirty = false;
function renderTape() {
  if (!tapeDirty) return;
  tapeDirty = false;
  const big = Math.max(5, (+$('tapeMin').value || 0) * 10);
  $('tape').innerHTML = S.tape.slice(0, 120).map((t) => `<div class="${t.m ? 'down' : 'up'}${+t.q >= big ? ' big' : ''}"><span>${new Date(t.T).toLocaleTimeString([], { hour12: false })}</span><span>${fmtP(+t.p)}</span><span>${fmtQ(+t.q)}</span></div>`).join('');
}
function renderLiqs() {
  $('liqs').innerHTML = S.liqs.length ? S.liqs.slice(0, 40).map((l) => `<div class="${l.side === 'long' ? 'down' : 'up'}">${new Date(l.T).toLocaleTimeString([], { hour12: false })} · ${l.side} liq · ${fmtQ(l.qty)} ${MARKET.unit} @ ${fmtP(l.price)} ($${(l.qty * l.price / 1e3).toFixed(0)}k)</div>`).join('') : 'none yet';
}

function renderHeader() {
  $('last').textContent = fmtP(S.last);
  $('last').className = S.bars.length && S.last >= S.bars[S.bars.length - 1].open ? 'up' : 'down';
  if (STOCK) {
    const m = S.stock, age = (Date.now() - S.stockAt) / 1000;
    if (m?.prevClose) {
      const c = (S.last / m.prevClose - 1) * 100;
      $('dayChg').textContent = `${c >= 0 ? '+' : ''}${c.toFixed(2)}%`;
      $('dayChg').className = c >= 0 ? 'up' : 'down';
      $('prevClose').textContent = `prev close ${fmtP(m.prevClose)}`;
    }
    if (m) $('session').textContent = m.open ? 'open' : 'closed';
    $('health').className = `health ${age < 40 ? 'ok' : age > 120 ? 'bad' : 'warn'}`;
    $('health').querySelector('span').textContent = `Nasdaq ${m?.open ? 'open' : 'closed'} · Yahoo · ${Math.round(age)}s ago`;
    return;
  }
  $('mark').textContent = fmtP(S.mark);
  $('index').textContent = fmtP(S.index);
  if (S.funding != null) {
    $('funding').textContent = `${(S.funding * 100).toFixed(4)}%`;
    $('funding').className = S.funding >= 0 ? 'up' : 'down';
    const s = Math.max(0, Math.floor((S.nextFunding - Date.now()) / 1000));
    $('fundingIn').textContent = ` in ${Math.floor(s / 3600)}h ${String(Math.floor(s / 60) % 60).padStart(2, '0')}m`;
  }
  if (S.oiNow != null) {
    $('oi').textContent = `${S.oiNow >= 1e6 ? (S.oiNow / 1e6).toFixed(2) + 'M' : (S.oiNow / 1000).toFixed(1) + 'k'} ${MARKET.unit}`;
    if (S.oi1hAgo) { const c = (S.oiNow - S.oi1hAgo) / S.oi1hAgo * 100; $('oiChg').textContent = ` ${c >= 0 ? '+' : ''}${c.toFixed(2)}% 1h`; }
  }
  const now = Date.now(), ageM = (now - S.health.market) / 1000, ageP = (now - S.health.public) / 1000;
  const ok = ageM < 5 && ageP < 5 && book.synced && (S.restDiff == null || S.restDiff < 0.001);
  const bad = ageM > 15 || ageP > 15;
  $('health').className = `health ${ok ? 'ok' : bad ? 'bad' : 'warn'}`;
  $('health').querySelector('span').textContent = bad ? 'reconnecting…' : `${ok ? 'live' : 'degraded'} · book ${book.synced ? '✓' : 'syncing'}${S.restDiff != null ? ` · REST Δ ${(S.restDiff * 100).toFixed(3)}%` : ''}`;
}

// ───────── footprint canvas
function niceStep(x) { // 1-2-2.5-5 steps at any scale (BTC $10 rows, HOOD $0.01 rows)
  const p = 10 ** Math.floor(Math.log10(Math.max(x, MARKET.fpBase)));
  return [1, 2, 2.5, 5, 10].map((m) => m * p).find((s) => s >= x - 1e-12);
}
const r8 = (x) => Number(x.toFixed(8));
const decimalsOf = (step) => (step >= 1 ? 0 : Math.min(4, Math.ceil(-Math.log10(step) - 1e-9)));
function drawFootprint() {
  const cv = $('footprint'), dpr = window.devicePixelRatio || 1;
  const W = cv.clientWidth, H = cv.clientHeight;
  if (cv.width !== W * dpr || cv.height !== H * dpr) { cv.width = W * dpr; cv.height = H * dpr; }
  const ctx = cv.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = '#0b0e14'; ctx.fillRect(0, 0, W, H);
  const axisW = 62, colW = 96, footH = 30;
  const n = Math.max(1, Math.floor((W - axisW) / colW));
  let view = fp.view(n, 1);
  if (!view.length) { ctx.fillStyle = '#7d8794'; ctx.font = '12px sans-serif'; ctx.fillText('waiting for trades…', 12, 20); return; }
  let hi = -Infinity, lo = Infinity;
  for (const c of view) for (const r of c.rows) { hi = Math.max(hi, r.price); lo = Math.min(lo, r.price); }
  const rowsFit = Math.max(4, Math.floor((H - footH) / 13));
  const tick = settings[fpTickKey] || niceStep((hi - lo + MARKET.fpBase) / rowsFit);
  view = fp.view(n, tick);
  hi = -Infinity; lo = Infinity;
  for (const c of view) for (const r of c.rows) { hi = Math.max(hi, r.price); lo = Math.min(lo, r.price); }
  let nRows = Math.round((hi - lo) / tick) + 1;
  const axisDp = decimalsOf(tick);
  let top = hi;
  if (nRows > rowsFit) { // keep the ladder centred on the last price
    const center = r8(Math.floor((S.last || hi) / tick + 1e-9) * tick);
    top = Math.min(hi, r8(center + Math.floor(rowsFit / 2) * tick));
    nRows = rowsFit;
  }
  const rowH = Math.min(18, (H - footH) / nRows);
  let maxCell = 0;
  for (const c of view) for (const r of c.rows) maxCell = Math.max(maxCell, r.buy + r.sell);
  ctx.font = `${Math.max(9, Math.min(11, rowH - 3))}px ui-monospace, Menlo, monospace`;
  ctx.textBaseline = 'middle';
  for (let k = 0; k < nRows; k++) {
    const price = r8(top - k * tick), y = k * rowH;
    ctx.fillStyle = Math.abs(price - Math.floor((S.last || 0) / tick + 1e-9) * tick) < tick / 2 ? '#f7c948' : '#7d8794';
    ctx.fillText(fmtP(price, axisDp), 4, y + rowH / 2);
  }
  view.forEach((c, ci) => {
    const x = axisW + ci * colW;
    const byPrice = new Map(c.rows.map((r) => [r.price, r]));
    for (let k = 0; k < nRows; k++) {
      const price = r8(top - k * tick), r = byPrice.get(price);
      if (!r) continue;
      const y = k * rowH, d = r.buy - r.sell, a = Math.min(0.85, 0.12 + 0.8 * (r.buy + r.sell) / (maxCell || 1));
      ctx.fillStyle = d >= 0 ? `rgba(38,166,154,${a})` : `rgba(239,83,80,${a})`;
      ctx.fillRect(x + 1, y + 1, colW - 3, rowH - 1);
      if (c.poc === price) { ctx.strokeStyle = '#f7c948'; ctx.lineWidth = 1; ctx.strokeRect(x + 1.5, y + 1.5, colW - 4, rowH - 2); }
      if (rowH >= 11) {
        const below = byPrice.get(r8(price - tick)), above = byPrice.get(r8(price + tick));
        const minQ = MARKET.tapeMin; // ignore imbalances on tiny prints
        const buyImb = below && r.buy >= 3 * below.sell && r.buy > minQ, sellImb = above && r.sell >= 3 * above.buy && r.sell > minQ;
        ctx.fillStyle = sellImb ? '#ff8a80' : '#e6e6e6';
        ctx.textAlign = 'right'; ctx.fillText(fmtQ(r.sell), x + colW / 2 - 6, y + rowH / 2);
        ctx.fillStyle = '#8a8f98'; ctx.textAlign = 'center'; ctx.fillText('×', x + colW / 2, y + rowH / 2);
        ctx.fillStyle = buyImb ? '#69f0ae' : '#e6e6e6';
        ctx.textAlign = 'left'; ctx.fillText(fmtQ(r.buy), x + colW / 2 + 6, y + rowH / 2);
      }
    }
    const delta = c.buy - c.sell;
    ctx.textAlign = 'center';
    ctx.fillStyle = delta >= 0 ? '#26a69a' : '#ef5350';
    ctx.fillText(`Δ ${delta >= 0 ? '+' : ''}${delta.toFixed(1)}`, x + colW / 2, H - footH + 9);
    ctx.fillStyle = '#7d8794';
    ctx.fillText(new Date(c.time * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }), x + colW / 2, H - footH + 22);
    ctx.textAlign = 'left';
  });
}
const fmtQ = (q) => (q >= 100 ? q.toFixed(0) : q >= 10 ? q.toFixed(1) : q.toFixed(2));

// ───────── news terminal (headlines + calendar come from server.py)
const news = new News({ onChange: () => setMarkers() });
let sideTab = 'news';
news.active = () => sideTab === 'news' && !document.hidden;
function buildTabs() {
  $('sideTabs').onclick = (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    sideTab = b.dataset.tab;
    $('sideTabs').querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === b));
    document.querySelectorAll('.tabs-card .tab').forEach((t) => t.classList.toggle('hidden', t.dataset.tab !== sideTab));
    if (sideTab === 'news') news.markRead();
    if (sideTab === 'calendar') news.renderCalendar();
  };
  document.addEventListener('visibilitychange', () => { if (!document.hidden && sideTab === 'news') news.markRead(); });
}

// ───────── controls
function buildControls() {
  document.title = `${MARKET.label} · Perp Desk`;
  document.body.classList.toggle('stock', STOCK); // hides the perp-only panels (funding, OI, footprint, tape, liqs)
  $('symTabs').innerHTML = Object.entries(MARKETS).map(([s, m]) => `<button data-s="${s}" class="${s === SYMBOL ? 'on' : ''}" title="${m.name} · ${m.venue}">${m.label}</button>`).join('')
    + `<small>${MARKET.name} · ${MARKET.venue}</small>`;
  $('symTabs').onclick = (e) => {
    const s = e.target.closest('button')?.dataset.s;
    if (!s || s === SYMBOL) return;
    try { localStorage.setItem('btc-perp-desk-symbol', s); } catch { /* storage unavailable */ }
    location.search = `?s=${s}`; // a clean reload: every stream, book and cache belongs to one market
  };
  document.querySelectorAll('.unit').forEach((el) => { el.textContent = MARKET.unit; });
  $('tapeMin').value = MARKET.tapeMin;
  $('tapeMin').step = MARKET.tapeMin / 5;
  $('fpTick').innerHTML = `<option value="0">auto rows</option>` + MARKET.fpTicks.map((v) => `<option value="${v}">$${v}</option>`).join('');
  $('tfs').innerHTML = Object.keys(TIMEFRAMES).map((tf) => `<button data-tf="${tf}" class="${tf === S.tf ? 'on' : ''}">${tf}</button>`).join('');
  $('tfs').onclick = (e) => { const tf = e.target.dataset.tf; if (tf && tf !== S.tf) switchTf(tf); };
  const st = $('settings');
  st.innerHTML = LAYERS.map(([k, label]) => `<label><input type="checkbox" data-k="${k}" ${settings[k] ? 'checked' : ''}> ${label}</label>`).join('')
    + `<div class="num">Swing length <input type="number" data-n="swingLen" value="${settings.swingLen}" min="3" max="100">
       Profile bars <input type="number" data-n="profileBars" value="${settings.profileBars}" min="50" max="1500">
       Flow bars <input type="number" data-n="flowBars" value="${settings.flowBars}" min="2" max="200"></div>
       <div class="num">Gamma expiries <select data-n="gexDays"><option value="7">≤ 7 days</option><option value="30">≤ 30 days</option><option value="9999">all</option></select></div>`;
  st.querySelector('select[data-n=gexDays]').value = String(settings.gexDays);
  st.onchange = (e) => {
    const t = e.target;
    if (t.dataset.k) settings[t.dataset.k] = t.checked;
    if (t.dataset.n) settings[t.dataset.n] = +t.value;
    save();
    if (t.dataset.n === 'gexDays') refreshGex();
    if (t.dataset.k === 'gamma') drawGexLines();
    recompute();
  };
  $('settingsBtn').onclick = () => st.classList.toggle('hidden');
  $('fpTf').value = String(settings.fpTf);
  $('fpTick').value = String(settings[fpTickKey] || 0);
  $('fpTf').onchange = (e) => { settings.fpTf = +e.target.value; save(); startFootprint(); };
  $('fpTick').onchange = (e) => { settings[fpTickKey] = +e.target.value; save(); };
}

async function switchTf(tf) {
  S.tf = tf; S.tfSec = TIMEFRAMES[tf]; settings.tf = tf; save();
  document.querySelectorAll('#tfs button').forEach((b) => b.classList.toggle('on', b.dataset.tf === tf));
  const [bars] = await Promise.all([loadBars(tf), loadOiHistory(tf)]);
  S.bars = bars;
  setAllData();
  main.timeScale().setVisibleLogicalRange({ from: bars.length - 180, to: bars.length + 12 });
  openMarket();
}

// ───────── timers
setInterval(() => { // heatmap sampling
  if (!book.synced) return;
  const px = S.last || book.best().bid;
  heat.push(Date.now() / 1000, book.sample(niceStep(px * 0.00012), 0.015));
  if (settings.heatmap) heatP.set(heat.cols, S.tfSec);
}, HEATMAP_EVERY_SEC * 1000);
async function refreshOi() { // live open interest + the value one hour ago (5m history)
  if (STOCK) return;
  try {
    S.oiNow = +(await getJSON(`${REST}/fapi/v1/openInterest?symbol=${SYMBOL}`)).openInterest;
    const h = await getJSON(`${REST}/futures/data/openInterestHist?symbol=${SYMBOL}&period=5m&limit=13`);
    if (h.length >= 13) S.oi1hAgo = +h[0].sumOpenInterest;
    alignOi();
  } catch (e) { console.warn('OI', e); }
}
setInterval(refreshOi, 15000);
setInterval(async () => { // independent REST check of the streamed price
  if (STOCK) return;
  try {
    const p = +(await getJSON(`${REST}/fapi/v1/ticker/price?symbol=${SYMBOL}`)).price;
    if (S.last) S.restDiff = Math.abs(p - S.last) / p;
  } catch (e) { console.warn('ticker check', e); }
}, 30000);
setInterval(refreshGex, 5 * 60e3);
setInterval(renderScore, 3000);
setInterval(drawFootprint, 1000);
setInterval(() => { renderHeader(); renderTape(); }, 250);
window.addEventListener('resize', drawFootprint);

// ───────── start
window.desk = { S, book, heat, settings, news, footprint: () => fp, layers: { heatP, boxP, profP } }; // inspect live state from the browser console
buildControls();
buildTabs();
news.start();
(async () => {
  if (!STOCK) try {
    await refreshOi();
    const pi = await getJSON(`${REST}/fapi/v1/premiumIndex?symbol=${SYMBOL}`);
    S.mark = +pi.markPrice; S.index = +pi.indexPrice; S.funding = +pi.lastFundingRate; S.nextFunding = pi.nextFundingTime;
  } catch (e) { console.warn('startup stats', e); }
  await switchTf(S.tf);
  S.last = S.bars[S.bars.length - 1].close;
  refreshGex();
  startFootprint();
  refreshPaper();
})();
