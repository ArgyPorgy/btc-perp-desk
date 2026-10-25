// Custom drawings on the price pane using Lightweight Charts v4 series primitives.
// Coordinates come from the chart itself (priceToCoordinate / logicalToCoordinate), so drawings stay
// glued to price and time while zooming and scrolling.

class BasePrimitive {
  constructor(zOrder = 'normal') {
    this.z = zOrder;
    this.visible = true;
    const self = this;
    this.view = {
      zOrder: () => self.z,
      renderer: () => ({
        draw: (target) => {
          if (!self.visible || !self.series) return;
          target.useMediaCoordinateSpace((scope) => self.draw(scope.context, scope.mediaSize));
        },
      }),
    };
  }
  attached({ chart, series, requestUpdate }) { this.chart = chart; this.series = series; this.requestUpdate = requestUpdate; }
  detached() { this.chart = this.series = this.requestUpdate = null; }
  updateAllViews() {}
  paneViews() { return [this.view]; }
  refresh() { if (this.requestUpdate) this.requestUpdate(); }
  y(price) { return this.series.priceToCoordinate(price); }
  // logicalToCoordinate only handles whole bar indexes (fractions return 0), so interpolate between neighbours
  xLogical(lg) {
    const ts = this.chart.timeScale(), i = Math.floor(lg), f = lg - i;
    const a = ts.logicalToCoordinate(i), b = ts.logicalToCoordinate(i + 1);
    return a == null || b == null ? null : a + f * (b - a);
  }
  x(time) { return this.xLogical(this.timeToLogical(time)); }
  barWidth() { const ts = this.chart.timeScale(); return Math.abs((ts.logicalToCoordinate(1) ?? 0) - (ts.logicalToCoordinate(0) ?? 0)) || 6; }
}

// Boxes (order blocks, FVGs, ranges) and horizontal segments (broken swing levels).
export class BoxesPrimitive extends BasePrimitive {
  constructor(timeToLogical) { super('normal'); this.timeToLogical = timeToLogical; this.items = []; }
  set(items) { this.items = items; this.refresh(); }
  draw(ctx, size) {
    ctx.font = '10px -apple-system, Segoe UI, sans-serif';
    for (const it of this.items) {
      const x1 = this.x(it.t1);
      const x2 = it.t2 == null ? size.width : this.x(it.t2);
      if (x1 == null || x2 == null || x2 < 0 || x1 > size.width) continue;
      if (it.kind === 'line') {
        const y = this.y(it.price);
        if (y == null) continue;
        ctx.strokeStyle = it.color; ctx.lineWidth = 1; ctx.setLineDash(it.dash || []);
        ctx.beginPath(); ctx.moveTo(x1, y); ctx.lineTo(x2, y); ctx.stroke(); ctx.setLineDash([]);
        if (it.label) { ctx.fillStyle = it.color; ctx.fillText(it.label, (x1 + x2) / 2 - 12, it.labelBelow ? y + 11 : y - 3); }
        continue;
      }
      const yt = this.y(it.top), yb = this.y(it.bottom);
      if (yt == null || yb == null) continue;
      ctx.fillStyle = it.fill;
      ctx.fillRect(x1, yt, x2 - x1, Math.max(1, yb - yt));
      if (it.stroke) { ctx.strokeStyle = it.stroke; ctx.lineWidth = 1; ctx.strokeRect(x1, yt, x2 - x1, Math.max(1, yb - yt)); }
      if (it.label) { ctx.fillStyle = it.labelColor || it.stroke || '#aaa'; ctx.fillText(it.label, x1 + 3, yt + 10); }
    }
  }
}

// Volume profile histogram on the left edge (keeps the newest candles and the heatmap clear),
// with POC / VAH / VAL lines from the profile's first bar to the right edge.
export class ProfilePrimitive extends BasePrimitive {
  constructor(timeToLogical) { super('normal'); this.timeToLogical = timeToLogical; this.p = null; }
  set(profile, startTime) { this.p = profile; this.start = startTime; this.refresh(); }
  draw(ctx, size) {
    const p = this.p;
    if (!p) return;
    const maxW = Math.min(170, size.width * 0.18), left = 2, right = size.width - 2;
    const mx = Math.max(...p.bins);
    for (let r = 0; r < p.bins.length; r++) {
      if (!p.bins[r]) continue;
      const lo = p.lo + r * p.step, hi = lo + p.step;
      const yt = this.y(hi), yb = this.y(lo);
      if (yt == null || yb == null) continue;
      const w = (p.bins[r] / mx) * maxW;
      const inVA = lo + p.step / 2 >= p.val && lo + p.step / 2 <= p.vah;
      ctx.fillStyle = r === p.pocRow ? 'rgba(247,201,72,0.75)' : inVA ? 'rgba(66,133,244,0.40)' : 'rgba(140,148,160,0.25)';
      ctx.fillRect(left, yt + 0.5, w, Math.max(1, yb - yt - 1));
    }
    const xs = Math.max(0, this.x(this.start) ?? 0);
    const line = (price, color, dash, label) => {
      const y = this.y(price);
      if (y == null) return;
      ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.setLineDash(dash);
      ctx.beginPath(); ctx.moveTo(xs, y); ctx.lineTo(right, y); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = color; ctx.font = '10px -apple-system, Segoe UI, sans-serif';
      ctx.fillText(label, xs + 4, y - 3);
    };
    line(p.poc, 'rgba(247,201,72,0.95)', [], 'POC');
    line(p.vah, 'rgba(66,133,244,0.85)', [4, 3], 'VAH');
    line(p.val, 'rgba(66,133,244,0.85)', [4, 3], 'VAL');
  }
}

// Order-book liquidity heatmap behind the candles (columns sampled every few seconds while the page is open).
export class HeatmapPrimitive extends BasePrimitive {
  constructor(timeToLogical, everySec, tfSec) { super('bottom'); this.timeToLogical = timeToLogical; this.every = everySec; this.tf = tfSec; this.cols = []; }
  set(cols, tfSec) { this.cols = cols; this.tf = tfSec; this.refresh(); }
  draw(ctx, size) {
    if (!this.cols.length) return;
    const ts = this.chart.timeScale();
    const vr = ts.getVisibleLogicalRange();
    if (!vr) return;
    const colW = Math.max(1, this.barWidth() * (this.every / this.tf));
    const vis = [];
    for (const c of this.cols) {
      const lg = this.timeToLogical(c.t);
      if (lg < vr.from - 1 || lg > vr.to + 1) continue;
      const x = this.xLogical(lg);
      if (x != null) vis.push([c, x]);
    }
    if (!vis.length) return;
    // robust scale: 97th percentile of visible cell sizes
    const sample = [];
    for (let i = 0; i < vis.length; i += Math.max(1, Math.floor(vis.length / 300))) for (const s of vis[i][0].sizes) sample.push(s);
    sample.sort((a, b) => a - b);
    const ref = sample[Math.floor(sample.length * 0.97)] || 1;
    let lastX = -Infinity;
    for (const [c, x] of vis) {
      if (x - lastX < 1) continue; // more columns than pixels: draw one per pixel
      lastX = x;
      for (let i = 0; i < c.prices.length; i++) {
        const v = Math.min(1, c.sizes[i] / ref);
        if (v < 0.08) continue;
        const yt = this.y(c.prices[i] + c.bucket), yb = this.y(c.prices[i]);
        if (yt == null || yb == null) continue;
        ctx.fillStyle = heatColor(v);
        ctx.fillRect(x - colW / 2, yt, colW + 0.5, Math.max(1, yb - yt));
      }
    }
  }
}

function heatColor(v) { // dark blue -> cyan -> yellow -> white, alpha rising with size
  const stops = [[0.0, [20, 40, 120]], [0.35, [0, 170, 220]], [0.7, [250, 210, 50]], [1.0, [255, 255, 255]]];
  let a = stops[0], b = stops[stops.length - 1];
  for (let i = 0; i < stops.length - 1; i++) if (v >= stops[i][0] && v <= stops[i + 1][0]) { a = stops[i]; b = stops[i + 1]; break; }
  const f = (v - a[0]) / (b[0] - a[0] || 1);
  const c = a[1].map((x, i) => Math.round(x + (b[1][i] - x) * f));
  return `rgba(${c[0]},${c[1]},${c[2]},${(0.25 + 0.6 * v).toFixed(2)})`;
}
