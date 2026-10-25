"""Stake Mines provably-fair verifier, written from Stake's published spec
(stake.com/provably-fair/implementation, /conversions, /game-events).

Usage: python3 verifier.py <serverSeed> <clientSeed> <nonce> <mines> [serverSeedHash]
"""
import hashlib
import hmac
import sys


def byte_generator(server_seed, client_seed, nonce, cursor=0):
    rnd = cursor // 32
    pos = cursor - rnd * 32
    while True:
        msg = f"{client_seed}:{nonce}:{rnd}".encode()
        buf = hmac.new(server_seed.encode(), msg, hashlib.sha256).digest()
        while pos < 32:
            yield buf[pos]
            pos += 1
        pos = 0
        rnd += 1


def generate_floats(server_seed, client_seed, nonce, count, cursor=0):
    rng = byte_generator(server_seed, client_seed, nonce, cursor)
    out = []
    for _ in range(count):
        out.append(sum(next(rng) / 256 ** (i + 1) for i in range(4)))
    return out


def mine_positions(server_seed, client_seed, nonce, mines):
    """Fisher-Yates over tiles 0..24 (left->right, top->bottom); first `mines` picks are bombs."""
    floats = generate_floats(server_seed, client_seed, nonce, 24)
    tiles = list(range(25))
    picks = []
    for f in floats:
        picks.append(tiles.pop(int(f * len(tiles))))
    return picks[:mines]


def board(positions):
    s = set(positions)
    return "\n".join(" ".join("X" if r * 5 + c in s else "." for c in range(5)) for r in range(5))


if __name__ == "__main__":
    ss, cs, nonce, m = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    if len(sys.argv) > 5:
        ok = hashlib.sha256(ss.encode()).hexdigest() == sys.argv[5].lower()
        print("server seed hash matches:", ok)
    pos = mine_positions(ss, cs, nonce, m)
    print("mine tiles (0-24):", sorted(pos))
    print(board(pos))
