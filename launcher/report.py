"""Is it working? Summarise ledger.csv.  python report.py [ledger.csv]"""
import csv
import statistics
import sys
from collections import Counter
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "ledger.csv")
rows = list(csv.DictReader(path.open())) if path.exists() else []
closed = [r for r in rows if r["status"] == "closed"]
failed = [r for r in rows if r["status"].startswith(("failed", "create_not"))]
print(f"{path.name}: {len(rows)} rows, {len(closed)} closed launches, {len(failed)} failed")
if closed:
    buyers = [int(r["outside_buyers"] or 0) for r in closed]
    pnl = [float(r["pnl_sol_est"]) for r in closed if r["pnl_sol_est"] not in ("", None)]
    print(f"  got at least one outside buyer: {sum(b > 0 for b in buyers)}/{len(closed)}"
          f"  (median buyers {statistics.median(buyers):.0f}, max {max(buyers)})")
    print(f"  exits: {dict(Counter(r['exit_reason'] for r in closed))}")
    if pnl:
        print(f"  estimated PnL: total {sum(pnl):+.4f} SOL over {len(pnl)} sells, "
              f"profitable {sum(p > 0 for p in pnl)}/{len(pnl)}, best {max(pnl):+.4f}, worst {min(pnl):+.4f}")
    print("  ground truth is your wallet balance: estimates exclude creator fees claimed and use a fee estimate")
