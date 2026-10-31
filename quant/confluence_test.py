"""Does following the indicators work? A 9-point trend/flow score, tested on the 1h perp history (2026-10-31).

Each 1h close scores +1 (bullish) or -1 (bearish) on: EMA50 vs EMA200 on 1h, 4h and 1d; close vs EMA50 on 1h and 4h;
1d close vs EMA200; 24h return; 12h taker delta; position in the 48h range. 4h/1d values come from the last CLOSED
candle (no look-ahead). Score S in [-9, 9]; |S| >= k trades WITH the score (long if S >= k, short if S <= -k), and
"against" takes the opposite side (what buying support in a downtrend looks like). Entry at the 1h close, stop 1.5 ATR(14),
target 2R, exit after 48h, one trade at a time per market, taker fees both ways.
Run from quant/: python3 confluence_test.py
"""
import numpy as np

from scalp_tests import resolve, summary, TAKER

H1 = 3_600_000


def ema(x, n):
    out, k = np.empty(len(x)), 2 / (n + 1)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = x[i] * k + out[i - 1] * (1 - k)
    return out


def htf(t, C, hours):
    """Close, EMA50, EMA200 of the last CLOSED higher-timeframe candle, aligned to each 1h bar."""
    step = hours * H1
    key = t // step
    uk, first = np.unique(key, return_index=True)
    last = np.r_[first[1:] - 1, len(t) - 1]
    c = C[last]
    e50, e200 = ema(c, 50), ema(c, 200)
    idx = np.searchsorted(uk, (t + H1) // step - 1)  # the htf candle that has closed by this 1h close
    ok = (idx < len(uk)) & (uk[np.minimum(idx, len(uk) - 1)] == (t + H1) // step - 1)
    idx = np.minimum(idx, len(uk) - 1)
    return np.where(ok, c[idx], np.nan), np.where(ok, e50[idx], np.nan), np.where(ok, e200[idx], np.nan)


def score(a):
    t, H, L, C, V, TB = a[:, 0], a[:, 2], a[:, 3], a[:, 4], a[:, 5], a[:, 6]
    sgn = lambda x: np.where(x, 1, -1)
    e50, e200 = ema(C, 50), ema(C, 200)
    c4, f4, s4 = htf(t, C, 4)
    cd, fd, sd = htf(t, C, 24)
    delta = np.convolve(2 * TB - V, np.ones(12), "full")[:len(C)]
    hi48 = np.array([H[max(0, i - 47):i + 1].max() for i in range(len(C))])
    lo48 = np.array([L[max(0, i - 47):i + 1].min() for i in range(len(C))])
    ret24 = C - np.r_[np.full(24, np.nan), C[:-24]]
    S = (sgn(e50 > e200) + sgn(f4 > s4) + sgn(fd > sd) + sgn(C > e50) + sgn(c4 > f4) + sgn(cd > sd)
         + sgn(ret24 > 0) + sgn(delta > 0) + sgn(C > (hi48 + lo48) / 2))
    S = S.astype(float)
    S[:24 * 210] = np.nan  # warm-up: 200 daily candles for the 1d EMA200
    S[np.isnan(sd) | np.isnan(s4) | np.isnan(ret24)] = np.nan
    return S


def run(sym):
    a = np.load(f"data/{sym}_PERP_1h.npy")
    H, L, C = a[:, 2], a[:, 3], a[:, 4]
    tr = np.r_[0, np.maximum(H[1:], C[:-1]) - np.minimum(L[1:], C[:-1])]
    atr = np.convolve(tr, np.ones(14) / 14, "full")[:len(tr)]
    S = score(a)
    for k in (5, 7, 9):
        for mode in ("with", "against"):
            res, i = [], 0
            while i < len(C) - 49:
                if np.isnan(S[i]) or abs(S[i]) < k:
                    i += 1
                    continue
                side = (1 if S[i] > 0 else -1) * (1 if mode == "with" else -1)
                e, risk = C[i], 1.5 * atr[i]
                res.append(resolve(H, L, C, i, e, e - side * risk, e + side * 2 * risk, side, 48, TAKER))
                i += 48  # one trade at a time (max hold)
            summary(f"{sym[:-4]} |S|>={k} {mode:7}", res)


if __name__ == "__main__":
    for s in ("BTCUSDT", "ETHUSDT", "HYPEUSDT"):
        run(s)
