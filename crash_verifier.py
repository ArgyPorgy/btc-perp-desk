"""Stake Crash verifier, from Stake's seeding post (bitcointalk.org topic 5162888, July 2019).

Each game hash is SHA256 of the NEXT game's hash (games are played from the end of a 10M chain backward).
So from any one game hash you can rebuild every EARLIER game, but never a later one.

Usage:
  python3 crash_verifier.py <gameHash>               # crash point for that game
  python3 crash_verifier.py <gameHash> <count>       # that game plus the <count> games before it
"""
import hashlib
import hmac
import sys

SALT = "0000000000000000001b34dc6a1e86083f95500b096231436e9b25cbdd0075c4"  # Bitcoin block 584,500
TERMINATING_HASH = "78a9757d3be42b74a3f70239078ad9317125fe9ee630d5bdada46de963e56752"


def crash_point(game_hash: str) -> float:
    h = hmac.new(game_hash.encode(), SALT.encode(), hashlib.sha256).hexdigest()
    n = int(h[:8], 16)
    raw = max(1.0, (2**32 / (n + 1)) * (1 - 0.01))
    return int(raw * 100) / 100  # displayed value, floored to 2 decimals


def previous_hash(game_hash: str) -> str:
    return hashlib.sha256(game_hash.encode()).hexdigest()


def history(game_hash: str, count: int):
    """Yield (hash, crash) for this game and `count` earlier games, newest first."""
    h = game_hash
    for _ in range(count + 1):
        yield h, crash_point(h)
        h = previous_hash(h)


if __name__ == "__main__":
    gh = sys.argv[1].strip().lower()
    cnt = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    for h, c in history(gh, cnt):
        print(f"{c:>10.2f}x  {h}")
