// Pure indicator math. No DOM, no network: everything here is unit-tested in Node (tests/test_indicators.js).
// A bar is { time (UTC seconds), open, high, low, close, volume, takerBuy } — takerBuy is Binance's taker-buy base volume.

export const DAY = 86400;
export const dayKey = (t) => Math.floor(t / DAY);
export const weekKey = (t) => Math.floor((t / DAY + 3) / 7); // weeks start Monday 00:00 UTC

export function ema(values, n) {
  const out = new Array(values.length);
  const k = 2 / (n + 1);
  for (let i = 0; i < values.length; i++) out[i] = i === 0 ? values[0] : values[i] * k + out[i - 1] * (1 - k);
  return out;
}

export function atr(bars, n = 14) {
  const out = new Array(bars.length);
  let prev = null;
  for (let i = 0; i < bars.length; i++) {
    const b = bars[i];
    const tr = i === 0 ? b.high - b.low
      : Math.max(b.high - b.low, Math.abs(b.high - bars[i - 1].close), Math.abs(b.low - bars[i - 1].close));
    prev = i < n ? (prev === null ? tr : prev + (tr - prev) / (i + 1)) : prev + (tr - prev) / n; // Wilder
    out[i] = prev;
  }
  return out;
}

// Anchored VWAP with standard-deviation bands (same variance formula as TradingView's ta.vwap).
export function vwapBands(bars, keyFn) {
  const vwap = [], up1 = [], dn1 = [], up2 = [], dn2 = [];
  let key = null, pv = 0, v = 0, p2v = 0;
  for (const b of bars) {
    const k = keyFn(b.time);
    if (k !== key) { key = k; pv = 0; v = 0; p2v = 0; }
    const p = (b.high + b.low + b.close) / 3;
    pv += p * b.volume; v += b.volume; p2v += p * p * b.volume;
    const m = v > 0 ? pv / v : p;
    const sd = v > 0 ? Math.sqrt(Math.max(0, p2v / v - m * m)) : 0;
    vwap.push(m); up1.push(m + sd); dn1.push(m - sd); up2.push(m + 2 * sd); dn2.push(m - 2 * sd);
  }
  return { vwap, up1, dn1, up2, dn2 };
}

// Exact per-bar delta from Binance taker data, and CVD (resets each UTC day when resetDaily).
export function deltaCvd(bars, resetDaily = true) {
  const delta = [], cvd = [];
  let acc = 0, key = null;
  for (const b of bars) {
    const k = dayKey(b.time);
    if (resetDaily && k !== key) { key = k; acc = 0; }
    const d = 2 * b.takerBuy - b.volume;
    acc += d;
    delta.push(d); cvd.push(acc);
  }
  return { delta, cvd };
}

// Swing structure: pivots of `len` bars each side (confirmed `len` bars later, like LuxAlgo / Pine pivots).
// A close through the last unbroken swing = break: CHoCH if against the prior trend, BOS if with it.
export function structure(bars, len = 20, maxOB = 3) {
  const events = [];
  let hi = null, lo = null, trend = 0;
  let bullOBs = [], bearOBs = [];
  for (let i = 2 * len; i < bars.length; i++) {
    const p = i - len;
    let isHi = true, isLo = true;
    for (let j = p - len; j <= i; j++) {
      if (bars[j].high > bars[p].high) isHi = false;
      if (bars[j].low < bars[p].low) isLo = false;
    }
    if (isHi) hi = { price: bars[p].high, idx: p, broken: false };
    if (isLo) lo = { price: bars[p].low, idx: p, broken: false };
    const c = bars[i].close;
    if (hi && !hi.broken && c > hi.price) {
      events.push({ idx: i, time: bars[i].time, side: 1, kind: trend === -1 ? 'CHoCH' : 'BOS', level: hi.price, fromIdx: hi.idx });
      let k = hi.idx; // order block: lowest candle between the swing and the break
      for (let j = hi.idx; j < i; j++) if (bars[j].low < bars[k].low) k = j;
      bullOBs.push({ idx: k, time: bars[k].time, top: bars[k].high, bottom: bars[k].low, side: 1 });
      hi.broken = true; trend = 1;
    }
    if (lo && !lo.broken && c < lo.price) {
      events.push({ idx: i, time: bars[i].time, side: -1, kind: trend === 1 ? 'CHoCH' : 'BOS', level: lo.price, fromIdx: lo.idx });
      let k = lo.idx;
      for (let j = lo.idx; j < i; j++) if (bars[j].high > bars[k].high) k = j;
      bearOBs.push({ idx: k, time: bars[k].time, top: bars[k].high, bottom: bars[k].low, side: -1 });
      lo.broken = true; trend = -1;
    }
    bullOBs = bullOBs.filter((ob) => c >= ob.bottom).slice(-maxOB); // mitigated when closed through
    bearOBs = bearOBs.filter((ob) => c <= ob.top).slice(-maxOB);
  }
  return { events, trend, lastBreak: events.length ? events[events.length - 1].side : 0,
    orderBlocks: [...bullOBs, ...bearOBs], swingHigh: hi, swingLow: lo };
}

// Fair value gaps still unfilled at the end (filled once price trades through the whole gap).
export function fairValueGaps(bars, atrArr, minAtr = 0.3, max = 6) {
  let gaps = [];
  for (let i = 2; i < bars.length; i++) {
    const a = bars[i - 2], m = bars[i - 1], b = bars[i];
    if (b.low > a.high && m.close > a.high && b.low - a.high >= minAtr * atrArr[i])
      gaps.push({ idx: i - 2, time: a.time, top: b.low, bottom: a.high, side: 1 });
    if (b.high < a.low && m.close < a.low && a.low - b.high >= minAtr * atrArr[i])
      gaps.push({ idx: i - 2, time: a.time, top: a.low, bottom: b.high, side: -1 });
    gaps = gaps.filter((g) => g.idx === i - 2 || !(b.low <= g.bottom && b.high >= g.top));
  }
  return gaps.slice(-max);
}

// Consolidation ranges: last `minBars` fit inside `mult` x ATR; resolved by a close outside the box.
// A breakout counts only with volume >= volMult x 20-bar average; a range expires after `lookback` bars.
export function consolidation(bars, atrArr, { lookback = 30, mult = 2.2, minBars = 8, volMult = 1.8 } = {}) {
  const ranges = [];
  let cur = null, state = 0;
  for (let i = minBars; i < bars.length; i++) {
    let hiN = -Infinity, loN = Infinity, vSum = 0;
    for (let j = i - minBars + 1; j <= i; j++) { hiN = Math.max(hiN, bars[j].high); loN = Math.min(loN, bars[j].low); }
    for (let j = Math.max(0, i - 19); j <= i; j++) vSum += bars[j].volume;
    const vAvg = vSum / Math.min(20, i + 1);
    if (!cur) {
      if (hiN - loN <= mult * atrArr[i]) { cur = { start: i - minBars + 1, end: i, top: hiN, bottom: loN, result: 0 }; state = 2; }
      continue;
    }
    const c = bars[i].close;
    if (i - cur.start > lookback) { ranges.push(cur); cur = null; state = 0; continue; }
    if (c > cur.top || c < cur.bottom) {
      const up = c > cur.top;
      cur.end = i;
      cur.result = bars[i].volume >= volMult * vAvg ? (up ? 1 : -1) : 0;
      cur.breakIdx = i;
      state = cur.result;
      ranges.push(cur); cur = null;
    } else cur.end = i;
  }
  if (cur) ranges.push({ ...cur, active: true });
  return { ranges: ranges.slice(-12), state };
}

// Volume profile over bars[from..to]: volume spread evenly across the price rows each bar covers.
export function volumeProfile(bars, from, to, rows = 40, vaPct = 0.7) {
  let hi = -Infinity, lo = Infinity;
  for (let i = from; i <= to; i++) { hi = Math.max(hi, bars[i].high); lo = Math.min(lo, bars[i].low); }
  const step = (hi - lo) / rows;
  const bins = new Array(rows).fill(0);
  if (!(step > 0)) return null;
  for (let i = from; i <= to; i++) {
    const s = Math.min(rows - 1, Math.max(0, Math.floor((bars[i].low - lo) / step)));
    const e = Math.min(rows - 1, Math.max(0, Math.floor((bars[i].high - lo) / step)));
    const share = bars[i].volume / (e - s + 1);
    for (let r = s; r <= e; r++) bins[r] += share;
  }
  return withValueArea({ lo, step, bins }, vaPct);
}

function withValueArea(p, vaPct) {
  const { bins, lo, step } = p;
  let poc = 0;
  for (let r = 1; r < bins.length; r++) if (bins[r] > bins[poc]) poc = r;
  const total = bins.reduce((a, b) => a + b, 0);
  let acc = bins[poc], up = poc, dn = poc;
  while (acc < vaPct * total && (up < bins.length - 1 || dn > 0)) {
    const vUp = up < bins.length - 1 ? bins[up + 1] : -1;
    const vDn = dn > 0 ? bins[dn - 1] : -1;
    if (vUp >= vDn) { up++; acc += vUp; } else { dn--; acc += vDn; }
  }
  return { ...p, pocRow: poc, poc: lo + (poc + 0.5) * step, vah: lo + (up + 1) * step, val: lo + dn * step };
}

// Per UTC day: the previous day's POC/VAH/VAL (auction reference) and this day's initial balance.
export function dailyAuction(bars, tfSec, ibMinutes = 60) {
  const prior = new Array(bars.length).fill(null), ib = new Array(bars.length).fill(null);
  if (tfSec >= DAY) return { prior, ib };
  let dayStart = 0, levels = null, ibHi = null, ibLo = null;
  for (let i = 0; i < bars.length; i++) {
    if (i > 0 && dayKey(bars[i].time) !== dayKey(bars[i - 1].time)) {
      if (i - dayStart >= 3) {
        const p = volumeProfile(bars, dayStart, i - 1, 30, 0.7);
        levels = p ? { poc: p.poc, vah: p.vah, val: p.val } : null;
      }
      dayStart = i; ibHi = null; ibLo = null;
    }
    if (bars[i].time - bars[dayStart].time < ibMinutes * 60) {
      ibHi = ibHi === null ? bars[i].high : Math.max(ibHi, bars[i].high);
      ibLo = ibLo === null ? bars[i].low : Math.min(ibLo, bars[i].low);
    }
    prior[i] = levels;
    ib[i] = ibHi === null ? null : { hi: ibHi, lo: ibLo };
  }
  return { prior, ib };
}

// Context scorecard: each row is +1 / -1 / 0 with a plain-language reading. Context, not a forecast.
export function scorecard(s) {
  const rows = [];
  const add = (name, score, text) => rows.push({ name, score, text });
  const c = s.close;
  add('HTF trend', s.ema200 == null ? 0 : c > s.ema200 ? 1 : -1,
    s.ema200 == null ? 'n/a' : `${c > s.ema200 ? 'above' : 'below'} EMA200`);
  if (s.vwap == null) add('VWAP', 0, 'intraday only');
  else add('VWAP', c > s.vwap ? 1 : -1, c > s.up1 ? 'above +1σ (stretched)' : c < s.dn1 ? 'below -1σ (stretched)'
    : c > s.vwap ? 'above session VWAP' : 'below session VWAP');
  add('Structure', s.lastBreak, s.lastBreak === 0 ? 'no break yet' : s.lastBreak > 0 ? `last break up (${s.lastKind})` : `last break down (${s.lastKind})`);
  if (!s.profile) add('Value area', 0, 'n/a');
  else add('Value area', c > s.profile.vah ? 1 : c < s.profile.val ? -1 : 0,
    c > s.profile.vah ? 'above value' : c < s.profile.val ? 'below value' : 'inside value: rotation more likely');
  if (!s.prior) add('Auction', 0, 'n/a');
  else {
    const p = s.prior;
    const txt = s.high > p.vah && c <= p.vah ? 'looked above prior value, failed' : s.low < p.val && c >= p.val ? 'looked below prior value, failed'
      : c > p.vah ? 'accepted above prior value' : c < p.val ? 'accepted below prior value' : 'balance: inside prior value';
    add('Auction', c > p.vah ? 1 : c < p.val ? -1 : 0, txt);
  }
  add('Delta (CVD)', Math.sign(s.cvdChange || 0), s.cvdChange == null ? 'n/a'
    : `${s.cvdChange > 0 ? 'net taker buying' : 'net taker selling'} ${fmtQty(s.cvdChange)} BTC / ${s.flowBars} bars`
      + (s.priceChange > 0 && s.cvdChange < 0 ? ' — divergence' : s.priceChange < 0 && s.cvdChange > 0 ? ' — divergence' : ''));
  if (s.oiChangePct == null) add('Open interest', 0, 'loading');
  else add('Open interest', s.oiChangePct > 0 ? Math.sign(s.priceChange) : 0,
    s.oiChangePct > 0 ? (s.priceChange > 0 ? 'rising with price: new longs' : 'rising as price falls: new shorts')
      : s.priceChange > 0 ? 'falling as price rises: short covering' : 'falling with price: longs exiting');
  if (s.funding == null) add('Funding', 0, 'loading');
  else add('Funding', 0, `${(s.funding * 100).toFixed(4)}% / 8h ${s.funding > 0.0003 ? '(longs crowded)' : s.funding < -0.0001 ? '(shorts crowded)' : '(neutral)'}`);
  if (s.bookImbalance == null) add('Order book', 0, 'syncing');
  else add('Order book', s.bookImbalance > 0.15 ? 1 : s.bookImbalance < -0.15 ? -1 : 0,
    `±0.5%: ${s.bookImbalance > 0 ? 'bids' : 'asks'} heavier by ${Math.abs(s.bookImbalance * 100).toFixed(0)}% (spoofable)`);
  if (!s.gex) add('Gamma', 0, 'loading');
  else add('Gamma', 0, isFinite(s.gex.flip) ? (c > s.gex.flip ? 'above flip: moves tend to be damped' : 'below flip: moves tend to be amplified') : 'no flip in range');
  add('Range', s.consState === 2 ? 0 : s.consState, s.consState === 2 ? 'consolidating' : s.consState === 1 ? 'volume breakout up'
    : s.consState === -1 ? 'volume breakdown' : 'no active range');
  return { rows, net: rows.reduce((a, r) => a + r.score, 0) };
}

export function fmtQty(x) {
  const a = Math.abs(x);
  return (x < 0 ? '-' : '+') + (a >= 1000 ? (a / 1000).toFixed(1) + 'k' : a.toFixed(a >= 100 ? 0 : 1));
}
