"""Intraday 24h-level trades, both directions (research_log.md 2026-10-30, lessons rule 22).
Longs: A = limit buy at the prior-24h low, stop 1 ATR under it, 1.6R; B = sweep of the 24h low with a close back above,
stop under the wick, 1.5R / 2R. Shorts: sweep of the 24h high with a close back under; close below the 24h low.
BTC 15m and BTC/ETH/HYPE 1h, fees as in scalp_tests.py, one trade per half day per pattern.
Run from quant/: python3 intraday_level_test.py
"""
import sys; sys.path.insert(0, '.')
import numpy as np
from scalp_tests import resolve, summary, TAKER, MAKER
def run_longs(sym, tf, a):
    O,H,L,C = a[:,1],a[:,2],a[:,3],a[:,4]
    per_day = 96 if tf == '15m' else 24
    tr = np.r_[0, np.maximum(H[1:],C[:-1]) - np.minimum(L[1:],C[:-1])]
    atr = np.convolve(tr, np.ones(14)/14, 'full')[:len(tr)]
    A, B15, B2 = [], [], []
    last_a = last_b = -999
    for i in range(per_day+15, len(C)-per_day):
        lo = L[i-per_day:i].min()
        # A: limit buy at the prior-24h low + 0.1%, stop 1 ATR below the low, 1.6R
        if i - last_a > per_day//2 and L[i] <= lo*1.001 and L[i-1] > lo*1.001:
            e = lo*1.001; stop = lo - atr[i-1]
            if L[i] <= stop: A.append(-1 - (MAKER+TAKER)*e/(e-stop))
            else: A.append(resolve(H,L,C,i,e,stop,e+1.6*(e-stop),1,per_day,MAKER))
            last_a = i
        # B: candle wicks under the prior-24h low and closes back above -> long at close, stop under wick
        if i - last_b > per_day//2 and L[i] < lo < C[i]:
            e = C[i]; stop = L[i] - 0.1*atr[i-1]
            if e - stop > 0.002*e:
                B15.append(resolve(H,L,C,i,e,stop,e+1.5*(e-stop),1,per_day,TAKER))
                B2.append(resolve(H,L,C,i,e,stop,e+2*(e-stop),1,per_day,TAKER))
                last_b = i
    summary(f'{sym} {tf} A floor limit, 1ATR stop, 1.6R', A)
    summary(f'{sym} {tf} B sweep-reclaim close, 1.5R', B15)
    summary(f'{sym} {tf} B sweep-reclaim close, 2R', B2)
def run_shorts(sym, tf, a):
    H,L,C = a[:,2],a[:,3],a[:,4]
    pd_ = 96 if tf=='15m' else 24
    tr = np.r_[0, np.maximum(H[1:],C[:-1]) - np.minimum(L[1:],C[:-1])]
    atr = np.convolve(tr, np.ones(14)/14, 'full')[:len(tr)]
    S, BRK, last_s, last_k = [], [], -999, -999
    for i in range(pd_+15, len(C)-pd_):
        hi, lo = H[i-pd_:i].max(), L[i-pd_:i].min()
        if i-last_s > pd_//2 and H[i] > hi > C[i]:  # sweep of the 24h high, close back under -> short
            e, stop = C[i], H[i]+0.1*atr[i-1]
            if stop-e > 0.002*e:
                S.append(resolve(H,L,C,i,e,stop,e-1.5*(stop-e),-1,pd_,TAKER)); last_s = i
        if i-last_k > pd_//2 and C[i] < lo and C[i-1] >= lo:  # close below the 24h low -> short, stop over the candle high
            e, stop = C[i], H[i]+0.1*atr[i-1]
            if stop-e > 0.002*e:
                BRK.append(resolve(H,L,C,i,e,stop,e-1.5*(stop-e),-1,pd_,TAKER)); last_k = i
    summary(f'{sym} {tf} short sweep of 24h high, 1.5R', S)
    summary(f'{sym} {tf} short 24h-low breakdown, 1.5R', BRK)
if __name__ == "__main__":
    for f in (run_longs, run_shorts):
        f('BTC', '15m', np.load('data/BTCUSDT_PERP_15m.npy'))
        for s in ('BTCUSDT', 'ETHUSDT', 'HYPEUSDT'):
            f(s[:-4], '1h', np.load(f'data/{s}_PERP_1h.npy'))
