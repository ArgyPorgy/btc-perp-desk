"""Rebuild Stake's entire real Crash history from one recent game hash.

Walks the hash chain backward (each earlier game = SHA256 of the later game's hash) until it reaches
the terminating hash Stake published on BitcoinTalk in July 2019. Saves crash points (oldest first).
Run: python3 crash_history.py <recentGameHash>
"""
import hashlib
import hmac
import sys

import numpy as np

from crash_verifier import SALT, TERMINATING_HASH

LIMIT = 10_000_001
salt = SALT.encode()
h = sys.argv[1].strip().lower()
cents = np.empty(LIMIT, dtype=np.uint32)
n = 0
found = False
while n < LIMIT:
    if h == TERMINATING_HASH:
        found = True
        break
    d = hmac.new(h.encode(), salt, hashlib.sha256).digest()
    x = int.from_bytes(d[:4], "big")
    raw = max(1.0, (2**32 / (x + 1)) * 0.99)
    cents[n] = int(raw * 100)
    n += 1
    h = hashlib.sha256(h.encode()).hexdigest()

print(f"games walked back: {n:,}   reached Stake's 2019 terminating hash: {found}")
hist = cents[:n][::-1].copy()  # oldest first
np.save("crash_history.npy", hist)
print("saved crash_history.npy  (crash point x100, oldest game first)")
