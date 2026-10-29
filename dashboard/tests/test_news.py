"""Offline checks for the news tagger (dashboard/news.py). Run: python3 tests/test_news.py
Each case: headline, feed id, expected impact, expected first tag (None = don't care). Add a case whenever a rule changes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import news  # noqa: E402

CASES = [
    # real catalysts -> 3
    ("Fed holds rates steady at 4.00%, signals patience on cuts", "gn_fed", 3, "FED RATES"),
    ("FOMC statement: Committee decides to maintain the target range", "fed", 3, "FOMC"),
    ("US CPI rises 0.4% in September, hotter than expected", "gn_data", 3, "CPI"),
    ("Trump slaps 100% tariffs on Chinese imports starting Nov 1", "truth", 3, "TARIFFS"),
    ("US launches strikes on Iran nuclear sites", "gn_geo", 3, "WAR"),
    ("Iran moves to close Strait of Hormuz to tankers", "gn_geo", 3, "HORMUZ"),
    ("Bybit hacked: $1.4 billion in ETH drained from cold wallet", "coindesk", 3, "HACK"),
    ("SEC approves spot bitcoin ETF options listing", "coindesk", 3, "ETF DECISION"),
    # previews / opinion / commentary -> at most 2
    ("Fed expected to hold rates at this week's meeting: what to watch", "gn_fed", 2, None),
    ("Obama mocks Trump's trade war with 'the people who gave us maple syrup'", "gn_trade", 2, "TARIFFS"),
    ("Tariffs threaten thousands of flooring jobs", "gn_trade", 2, "TARIFFS"),
    ("Here's how a stock market crash could supercharge your retirement", "cnbc_top", 0, None),
    ("Trump weighs Iran deal or military action as Netanyahu warns of attacks", "gn_geo", 2, None),
    # wrong country / wrong meaning -> not top impact
    ("UK inflation rises to 4.1% as energy prices climb", "bbc_business", 1, None),
    ("Saudi Arabia raises electricity and water tariffs for 2027", "gn_trade", 1, "GEO"),
    ("Chancellor to cut tariffs on some food and freeze fuel duty to give families 'breathing space'", "bbc_business", 2, "TARIFFS"),
    ("Brazilian Markets Crash After Lula's Surprise Election Win Stuns Investors", "gn_markets", 0, None),
    ("Russian missile strikes on Ukraine's Kharkiv kill two, injure four, mayor says", "gn_geo", 2, "CONFLICT"),
    ("Russia launches missile strikes on NATO member Poland", "gn_geo", 3, "WAR"),
    ("Cass County Judge sorry to see Swift and Sure Sanctions Probation Program end", "gn_trade", 0, None),
    ("Robinhood shares sink after earnings miss on crypto revenue", "gn_hood", 2, "HOOD"),
    ("Ether ETF inflows hit record as ETH rallies", "gn_eth", 2, "ETF FLOWS"),
    ("NYSE owner takes steps to bring Hyperliquid perpetual futures to U.S.", "coindesk", 2, "HYPE"),
    ("Bitcoin buy-and-hold underperforms trend following in 10-year backtest", "coindesk", 1, None),
]


def main():
    bad = 0
    for title, fid, want_imp, want_tag in CASES:
        f = news.FEED[fid]
        cat, imp, tags = news.classify(title + (" [us]" if fid in news.US_FEEDS else ""), f[3], f[4])
        ok = imp == want_imp and (want_tag is None or (tags and tags[0] == want_tag))
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} [{imp} {'/'.join(tags) or cat}] {title}" + ("" if ok else f"   (want {want_imp} {want_tag or ''})"))
    # corroboration: unknown single source is capped, two sources or a top outlet are not
    assert news.effective_impact(3, ["Some Blog"]) == 1
    assert news.effective_impact(3, ["Some Blog", "Other Site"]) == 3
    assert news.effective_impact(3, ["Reuters"]) == 3
    print(f"\n{len(CASES) - bad} passed, {bad} failed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
