// News terminal: headlines + economic calendar from server.py (/api/news, /api/calendar).
// Impact 3 = can move BTC now (FOMC, CPI, tariffs, war escalation, exchange hack...), 2 = relevant, 1 = background.

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const GROUPS = { all: null, macro: ['fed', 'cb', 'data'], policy: ['policy'], geo: ['geo'], markets: ['markets'], crypto: ['crypto'] };
const GROUP_LABEL = { all: 'All', macro: 'Fed/data', policy: 'Policy', geo: 'Geo', markets: 'Mkts', crypto: 'Crypto' };
const CAT_LABEL = { fed: 'FED', cb: 'CB', data: 'DATA', policy: 'POLICY', geo: 'GEO', markets: 'MKTS', crypto: 'CRYPTO' };

const prefs = (() => { try { return { group: 'all', min: 2, ...JSON.parse(localStorage.getItem('btc-perp-desk-news') || '{}') }; } catch { return { group: 'all', min: 2 }; } })();
const savePrefs = () => { try { localStorage.setItem('btc-perp-desk-news', JSON.stringify(prefs)); } catch { /* storage unavailable */ } };

function ago(ts) {
  const s = Math.max(0, Date.now() / 1000 - ts);
  if (s < 60) return 'now';
  if (s < 3600) return `${Math.floor(s / 60)}m`;
  if (s < 86400) return `${Math.floor(s / 3600)}h${String(Math.floor(s % 3600 / 60)).padStart(2, '0')}`;
  return `${Math.floor(s / 86400)}d`;
}
function until(ts) {
  const s = ts - Date.now() / 1000;
  if (s < 0) return s > -3600 ? 'just out' : 'done';
  const d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600), m = Math.floor(s % 3600 / 60);
  return d ? `${d}d ${h}h` : h ? `${h}h ${String(m).padStart(2, '0')}m` : `${m}m ${String(Math.floor(s % 60)).padStart(2, '0')}s`;
}
const safeUrl = (u) => (/^https?:\/\//i.test(u || '') ? u : '#'); // feeds are untrusted: no javascript: links
const pct = (x) => `${x >= 0 ? '+' : ''}${x.toFixed(2)}%`;

export class News {
  constructor({ onChange } = {}) {
    this.items = [];
    this.events = [];
    this.known = new Set();
    this.firstLoad = true;
    this.unread = 0;
    this.available = null; // null = unknown, false = no server.py
    this.onChange = onChange || (() => {});
    this.active = () => true;
  }

  start() {
    this.buildFilters();
    this.poll();
    this.pollCalendar();
    setInterval(() => this.poll(), 20000);
    setInterval(() => this.pollCalendar(), 10 * 60e3);
    setInterval(() => { this.renderHeader(); this.renderCalendar(); }, 1000);
    setInterval(() => this.renderList(), 30000); // refresh the "x minutes ago" labels
  }

  async poll() {
    try {
      const r = await fetch('api/news?hours=72&min=1', { cache: 'no-store' });
      if (!r.ok) throw new Error(r.status);
      const d = await r.json();
      this.available = true;
      const fresh = [];
      for (const it of d.items) {
        if (!this.known.has(it.id)) { this.known.add(it.id); if (!this.firstLoad) { it._new = Date.now(); fresh.push(it); } }
      }
      const prev = new Map(this.items.map((x) => [x.id, x._new]));
      this.items = d.items.map((x) => (prev.get(x.id) ? { ...x, _new: prev.get(x.id) } : x));
      this.feeds = d.feeds;
      this.firstLoad = false;
      const shown = fresh.filter((x) => this.passes(x));
      if (shown.length && !this.active()) { this.unread += shown.length; }
      const hot = fresh.filter((x) => x.impact >= 3).sort((a, b) => b.ts - a.ts)[0];
      if (hot) this.toast(hot);
      this.renderList();
      this.onChange(this.items);
    } catch (e) {
      if (this.available !== true) {
        this.available = false;
        $('newsList').innerHTML = `<p class="muted">News needs the desk server (it fetches the feeds; browsers can't).<br>
          Close the old server window, then double-click <b>start.command</b> — or run <code>python3 server.py</code> in the dashboard folder.</p>`;
      }
    }
    this.renderBadge();
  }

  async pollCalendar() {
    try {
      const r = await fetch('api/calendar', { cache: 'no-store' });
      if (!r.ok) throw new Error(r.status);
      this.events = (await r.json()).events || [];
    } catch { this.events = []; }
    this.renderCalendar();
    this.renderHeader();
  }

  passes(it) {
    const g = GROUPS[prefs.group];
    return it.impact >= prefs.min && (!g || g.includes(it.cat));
  }

  buildFilters() {
    $('newsFilters').innerHTML = Object.keys(GROUPS).map((g) => `<button data-g="${g}" class="${g === prefs.group ? 'on' : ''}">${GROUP_LABEL[g]}</button>`).join('')
      + `<select id="newsMin" title="minimum impact"><option value="3">High</option><option value="2">Med+</option><option value="1">All</option></select>`;
    $('newsMin').value = String(prefs.min);
    $('newsFilters').onclick = (e) => {
      const g = e.target.dataset.g;
      if (!g) return;
      prefs.group = g; savePrefs();
      $('newsFilters').querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.dataset.g === g));
      this.renderList();
    };
    $('newsMin').onchange = (e) => { prefs.min = +e.target.value; savePrefs(); this.renderList(); };
  }

  renderList() {
    if (!this.available) return;
    const rows = this.items.filter((x) => this.passes(x)).slice(0, 150);
    const down = Object.values(this.feeds || {}).filter((f) => !f.ok).length;
    $('newsInfo').textContent = `${rows.length} shown · ${Object.keys(this.feeds || {}).length - down}/${Object.keys(this.feeds || {}).length} feeds${down ? ' ⚠' : ''}`;
    $('newsInfo').title = down ? `down: ${Object.values(this.feeds).filter((f) => !f.ok).map((f) => `${f.label} (${f.error || 'no data yet'})`).join(', ')}` : 'all feeds healthy';
    $('newsList').innerHTML = rows.length ? rows.map((it) => {
      const b = it.btc || {};
      const mv = b.m15 != null ? `<span class="${b.m15 >= 0 ? 'up' : 'down'}" title="BTC move 15 minutes after the headline">${pct(b.m15)} 15m</span>`
        : b.now != null ? `<span class="${b.now >= 0 ? 'up' : 'down'}" title="BTC move since the headline">${pct(b.now)}</span>` : '';
      const since = b.now != null && b.m15 != null ? `<span class="muted" title="BTC move since the headline">· ${pct(b.now)} since</span>` : '';
      const src = it.sources.slice(0, 2).join(' · ') + (it.sources.length > 2 ? ` +${it.sources.length - 2}` : '');
      const isNew = it._new && Date.now() - it._new < 5 * 60e3;
      return `<div class="news-item imp${it.impact}${isNew ? ' new' : ''}">
        <div class="meta"><i class="dot"></i><b>${esc(it.tags[0] || CAT_LABEL[it.cat] || it.cat)}</b><span class="muted">${ago(it.ts)}</span>${mv}${since}</div>
        <a href="${esc(safeUrl(it.link))}" target="_blank" rel="noopener noreferrer">${esc(it.title)}</a>
        <div class="src muted">${esc(src)}</div></div>`;
    }).join('') : '<p class="muted">Nothing at this filter. Try Med+ or All.</p>';
  }

  renderBadge() {
    $('newsBadge').textContent = this.unread ? String(this.unread) : '';
  }
  markRead() { this.unread = 0; this.renderBadge(); }

  nextEvents(n = 4) {
    const now = Date.now() / 1000;
    return this.events.filter((e) => e.ts > now - 1800 && (e.country === 'USD' ? e.impact === 'High' : false)).slice(0, n);
  }

  renderHeader() {
    const el = $('nextEvent');
    if (!el) return;
    const nx = this.nextEvents(6);
    if (!nx.length) { el.textContent = this.available === false ? 'needs server.py' : '—'; return; }
    const e = nx[0], s = e.ts - Date.now() / 1000;
    el.textContent = `${e.title} · ${until(e.ts)}`;
    el.className = s < 2 * 3600 ? 'down' : s < 24 * 3600 ? 'gold' : '';
    el.parentElement.title = nx.map((x) => `${new Date(x.ts * 1000).toLocaleString([], { weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false })}  ${x.title}${x.forecast ? ` (fcst ${x.forecast})` : ''}`).join('\n');
  }

  renderCalendar() {
    const box = $('calList');
    if (!box || box.closest('.hidden')) return;
    if (!this.events.length) { box.innerHTML = `<p class="muted">${this.available === false ? 'Calendar needs server.py.' : 'Loading calendar…'}</p>`; return; }
    const now = Date.now() / 1000;
    let lastDay = '';
    box.innerHTML = this.events.filter((e) => e.ts > now - 12 * 3600).map((e) => {
      const d = new Date(e.ts * 1000);
      const day = d.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short' });
      const head = day !== lastDay ? `<div class="cal-day">${day}</div>` : '';
      lastDay = day;
      const past = e.ts < now;
      return `${head}<div class="cal-row${past ? ' past' : ''}${e.impact === 'High' ? ' high' : ''}">
        <span>${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}</span>
        <span class="cty">${esc(e.country)}</span><span class="ttl">${esc(e.title)}${e.forecast || e.previous
          ? ` <small class="muted">${e.forecast ? esc(e.forecast) : '–'} / ${e.previous ? esc(e.previous) : '–'}</small>` : ''}</span>
        <span class="cd">${past ? '' : until(e.ts)}</span></div>`;
    }).join('') + '<p class="muted tiny">Local time · forecast / previous · ForexFactory calendar. USD high + medium; EUR/JPY/CNY/GBP high.</p>';
  }

  toast(it) {
    const t = $('toast');
    t.innerHTML = `<b>${esc(it.tags[0] || 'NEWS')}</b> ${esc(it.title)} <span class="muted">— ${esc(it.sources[0])}</span>`;
    t.classList.remove('hidden');
    t.onclick = () => { window.open(safeUrl(it.link), '_blank', 'noopener'); t.classList.add('hidden'); };
    clearTimeout(this.toastTimer);
    this.toastTimer = setTimeout(() => t.classList.add('hidden'), 30000);
  }

  // impact-3 headlines as chart markers
  markers(bars, tfSec) {
    if (!bars.length) return [];
    const first = bars[0].time, last = bars[bars.length - 1].time;
    const seen = new Set();
    return this.items.filter((x) => x.impact >= 3).slice(0, 12).map((x) => ({ t: Math.floor(x.ts / tfSec) * tfSec, x }))
      .filter(({ t }) => t >= first && t <= last && !seen.has(t) && seen.add(t))
      .map(({ t, x }) => ({ time: t, position: 'aboveBar', color: '#b388ff', shape: 'square', size: 0.6, text: (x.tags[0] || 'news').slice(0, 10) }));
  }
}
