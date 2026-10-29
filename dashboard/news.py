"""News terminal backend for the BTC Perp Desk.

Pulls public RSS feeds — Federal Reserve, White House, SEC, Trump's Truth Social posts (via trumpstruth.org), CNBC,
investingLive (macro wire), Google News searches (surfaces Reuters / AP / Bloomberg / WSJ headlines), BBC / Al Jazeera /
Guardian world, CoinDesk / The Block / Decrypt / Cointelegraph — plus the ForexFactory weekly economic calendar.
Every headline is tagged with a category (fed, cb, data, policy, geo, markets, crypto) and an impact score 0-3 from
keyword rules, de-duplicated across sources, kept in data/news.json, and annotated with BTC's move since it came out
(Binance perp 1m candles).

  python3 news.py                        # last 6h, impact >= 2, plus the next high-impact events
  python3 news.py --hours 24 --min-impact 1
  python3 news.py --json                 # the same payload the dashboard's /api/news serves
server.py runs the same code in a background loop for the dashboard.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import html
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

HERE = Path(__file__).parent
STORE = HERE / "data" / "news.json"
CAL_STORE = HERE / "data" / "calendar.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "quant"))
from fapi import base as fapi_base  # noqa: E402  Binance futures REST, or the local fallback where it is geo-blocked
KEEP_DAYS = 7


def gnews(q):
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"})


# id, label, url, default category, base impact, minimum impact to keep, poll seconds
FEEDS = [
    ("fed", "Federal Reserve", "https://www.federalreserve.gov/feeds/press_all.xml", "fed", 1, 1, 120),
    ("truth", "Trump (Truth Social)", "https://www.trumpstruth.org/feed", "policy", 0, 2, 90),
    ("whitehouse", "White House", "https://www.whitehouse.gov/news/feed/", "policy", 0, 1, 300),
    ("sec", "SEC", "https://www.sec.gov/news/pressreleases.rss", "policy", 0, 1, 300),
    ("investinglive", "investingLive", "https://investinglive.com/feed/news", "markets", 1, 1, 60),
    ("cnbc_top", "CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html", "markets", 0, 1, 120),
    ("cnbc_econ", "CNBC Economy", "https://www.cnbc.com/id/20910258/device/rss/rss.html", "data", 1, 1, 180),
    ("cnbc_markets", "CNBC Markets", "https://www.cnbc.com/id/15839069/device/rss/rss.html", "markets", 0, 1, 180),
    ("cnbc_world", "CNBC World", "https://www.cnbc.com/id/100727362/device/rss/rss.html", "geo", 0, 2, 180),
    ("gn_fed", "Google News", gnews('"Federal Reserve" OR FOMC OR "Fed chair" OR "rate cut" OR "interest rates" when:1d'), "fed", 0, 1, 300),
    ("gn_data", "Google News", gnews('CPI OR PCE OR "jobs report" OR payrolls OR "jobless claims" OR GDP OR inflation economy when:1d'), "data", 0, 2, 300),
    ("gn_trade", "Google News", gnews('tariffs OR "trade war" OR "trade deal" OR sanctions OR "export controls" when:1d'), "policy", 0, 2, 300),
    ("gn_geo", "Google News", gnews('(Iran OR Israel OR Russia OR Ukraine OR China OR Taiwan OR "North Korea") (missile OR strike OR attack OR war OR ceasefire OR troops) when:1d'), "geo", 0, 2, 300),
    ("gn_markets", "Google News", gnews('"Wall Street" OR "stock market" OR "Treasury yields" OR "dollar index" OR "oil prices" when:1d'), "markets", 0, 2, 300),
    ("gn_hood", "Google News", gnews('Robinhood OR "HOOD stock" OR "Vlad Tenev" when:1d'), "markets", 1, 1, 300),
    ("gn_eth", "Google News", gnews('ethereum OR "ether ETF" OR "ETH price" when:1d'), "crypto", 1, 1, 300),
    ("gn_hype", "Google News", gnews('Hyperliquid OR "HYPE token" OR "HYPE price" when:1d'), "crypto", 1, 1, 300),
    ("gn_crypto", "Google News", gnews('bitcoin OR "crypto market" OR "bitcoin ETF" OR stablecoin OR "crypto bill" when:1d'), "crypto", 1, 1, 300),
    ("bbc_world", "BBC", "https://feeds.bbci.co.uk/news/world/rss.xml", "geo", 0, 2, 180),
    ("bbc_business", "BBC", "https://feeds.bbci.co.uk/news/business/rss.xml", "markets", 0, 2, 300),
    ("aljazeera", "Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", "geo", 0, 2, 180),
    ("guardian", "Guardian", "https://www.theguardian.com/world/rss", "geo", 0, 2, 300),
    ("coindesk", "CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/", "crypto", 1, 1, 120),
    ("theblock", "The Block", "https://www.theblock.co/rss.xml", "crypto", 1, 1, 120),
    ("decrypt", "Decrypt", "https://decrypt.co/feed", "crypto", 1, 1, 180),
    ("cointelegraph", "Cointelegraph", "https://cointelegraph.com/rss", "crypto", 1, 1, 180),
]
FEED = {f[0]: f for f in FEEDS}

# ───────── tagging rules: (category, impact, tag, patterns that must ALL match, patterns that must NOT match)
# Top-impact (3) rules skip speculative / preview / opinion headlines; those fall through to the impact-2 rule below them.
SPEC = (r"\b(could|might|would|may|if|how|why|what|whether|expects?|expected to|predicts?|forecasts?|warns?|fears?|risks?|chances?|odds|"
        r"weighs?|considers?|eyes|mulls?|ahead|before|preview|explainer|analysis|opinion|mocks?|slams?|blasts?|criticiz\w+|torches)\b|\?")
FOREIGN = (r"\b(uk|u\.k\.|britain|british|japan\w*|euro ?zone|euro area|australia\w*|canad\w+|china|chinese|german\w*|india\w*|turk\w+|argentin\w+|"
           r"france|french|new zealand|mexic\w+|brazil\w*|korea\w*|swiss|ecb|boj|boe|philippin\w+|bsp|rbi|nigeria\w*|pakistan\w*|south africa\w*)\b")
US = r"\b(us|u\.s\.|united states|americans?|america|fed|federal reserve|wall street|bls|commerce department|treasury)\b|\[us\]"
ACTORS = (r"\b(iran\w*|israel\w*|russia\w*|ukrain\w*|china|chinese|taiwan\w*|north korea\w*|pyongyang|beijing|moscow|tehran|kremlin|"
          r"putin|xi jinping|nato|venezuela\w*|hezbollah|houthi\w*|hamas|gaza|saudi\w*|hormuz|red sea|pakistan\w*|india)\b")
MAJOR = r"\b(iran\w*|tehran|russia\w*|moscow|kremlin|putin|china|chinese|beijing|taiwan\w*|north korea\w*|pyongyang|nato|hormuz|pentagon)\b"
CRYPTO = r"\b(bitcoin|btc|crypto\w*|ether(eum)?|stablecoins?|tether|usdt|usdc|binance|coinbase|okx|bybit|kraken|solana|xrp|defi)\b"
UTILITY = r"\b(electricity|water|power|feed-in|energy|electric|utility|gas|rail|fares?)\b"
# domestic budget measures (e.g. a UK chancellor cutting food tariffs) are not trade-war actions
BUDGET = r"\b(chancellor|budget|fuel duty)\b"
RULES = [
    ("fed", 3, "FOMC", [r"\b(fomc|federal open market committee|dot plot)\b"], [SPEC]),
    ("fed", 3, "FED RATES", [r"\b(fed|federal reserve)\b", r"\b(cuts?|hikes?|raises?|holds?|lowers?|keeps?|leaves?|slash\w*|pause\w*)\b.{0,40}\brates?\b"], [SPEC]),
    ("fed", 3, "FED CHAIR", [r"\bfed(eral reserve)? chair\w*\b|\bchair\w* of the fed", r"\b(says|said|signals?|nominat\w+|fired?|resign\w*|ousts?|replac\w+)\b"], [SPEC]),
    ("fed", 3, "FED EMERGENCY", [r"\b(fed|federal reserve)\b", r"\bemergency\b"], [SPEC]),
    # the sitting chair by name (Kevin Warsh as of Oct 2026 — update this when the chair changes)
    ("fed", 3, "FED CHAIR", [r"\bwarsh\b", r"\b(says|said|signals?|sees|tells|told|pledges?|vows?)\b"], [SPEC]),
    ("fed", 2, "FOMC", [r"\b(fomc|federal open market committee|dot plot|fed (decision|meeting|week))\b"], []),
    ("fed", 2, "FED RATES", [r"\b(fed|federal reserve)\b", r"\brates?\b"], []),
    ("fed", 2, "FED", [r"\b(fed|federal reserve|fomc)\b", r"\b(powell|warsh|hassett|waller|bowman|jefferson|williams|goolsbee|miran|logan|daly|kashkari|"
                                                          r"musalem|hammack|barkin|bostic|collins|schmid|cook|barr|governor|minutes|balance sheet|"
                                                          r"rate cut|rate hike|interest rates?|qt|quantitative)\b"], []),
    ("fed", 2, "FED", [r"\bfederal reserve\b|\bthe fed\b|\bfed's\b|\bfed (officials?|policy|speakers?)\b"], []),
    ("cb", 3, "BOJ", [r"\b(boj|bank of japan)\b", r"\b(hikes?|hiked|raises?|raised|tighten\w*)\b"], []),
    ("cb", 2, "CENTRAL BANK", [r"\b(ecb|bank of japan|boj|bank of england|boe|pboc|people's bank of china|snb|bank of canada|lagarde|ueda)\b"], []),
    ("data", 3, "CPI", [r"\bcpi\b|consumer prices?\b|consumer price index", US], [FOREIGN, SPEC]),
    ("data", 3, "PCE", [r"\bpce\b|personal consumption expenditures", US], [FOREIGN, SPEC]),
    ("data", 3, "JOBS", [r"non-?farm|payrolls|jobs report|unemployment rate", US], [FOREIGN, SPEC]),
    ("data", 2, "CPI", [r"\bcpi\b|consumer price index", US], [FOREIGN]),
    ("data", 2, "PCE", [r"\bpce\b|personal consumption expenditures", US], [FOREIGN]),
    ("data", 2, "JOBS", [r"non-?farm|payrolls|jobs report|unemployment rate", US], [FOREIGN]),
    ("data", 2, "GDP", [r"\bgdp\b|gross domestic product", US], [FOREIGN]),
    ("data", 2, "DATA", [r"\bppi\b|producer prices?|jobless claims|unemployment claims|retail sales|\bism\b|\bpmi\b|consumer (confidence|sentiment)|"
                         r"jolts|job openings|durable goods|housing starts|core inflation", US], [FOREIGN]),
    ("data", 2, "INFLATION", [r"\binflation\b", US], [FOREIGN]),
    ("data", 1, "DATA", [r"\b(cpi|inflation|gdp|pmi|unemployment)\b"], []),
    ("policy", 3, "TARIFFS", [r"\b(impos\w*|announc\w*|rais\w*|hik\w*|slap\w*|exempt\w*|paus\w*|lift\w*|suspend\w*|sign\w*|doubl\w*|loosen\w*|"
                              r"cut\w*|retaliat\w*|threatens? (new |more |higher )?)\b.{0,40}\b(tariffs?|import duties)\b|"
                              r"\btariffs? (of|at|to) \d+ ?%|\d+ ?% tariffs?|\btariffs? (take|took|go|went) (effect|into effect)|section (232|301|338) tariffs?"],
     [SPEC, UTILITY, BUDGET]),
    ("policy", 2, "TARIFFS", [r"\btariffs?\b|trade war|import (duties|taxes)|section (232|301|338)"], [UTILITY]),
    ("policy", 3, "SHUTDOWN", [r"government shutdown|debt ceiling|debt limit|default on (us|u\.s\.|american) debt"], [SPEC]),
    ("policy", 2, "SHUTDOWN", [r"government shutdown|debt ceiling|debt limit"], []),
    ("policy", 2, "TRADE", [r"trade (deal|talks|agreement|truce|deficit)|export controls?|chip (ban|curbs|exports)|rare earths?"], []),
    ("policy", 2, "TREASURY", [r"\btreasury secretary\b|\bbessent\b|treasury (refunding|auction)|\bbond auction\b"], []),
    ("policy", 2, "TRUMP", [r"\btrump\b", r"\b(fed|rates?|powell|china|xi|tariffs?|stock market|economy|dollar|oil|crypto|bitcoin|deals?|sanctions?|iran|"
                                           r"russia|putin|ukraine|israel|venezuela|taxes|trade|markets?|inflation|energy|war|military)\b"], []),
    ("policy", 2, "EXEC ORDER", [r"executive order"], []),
    ("policy", 1, "TRUMP", [r"\btrump\b"], []),
    ("crypto", 3, "BTC RESERVE", [r"(strategic )?bitcoin reserve|crypto reserve|government (buys|sells|selling) bitcoin"], [SPEC]),
    ("crypto", 2, "BTC RESERVE", [r"(strategic )?bitcoin reserve|crypto reserve"], []),
    ("crypto", 3, "ETF DECISION", [r"\betfs?\b", r"\b(approv\w*|reject\w*|denies|denied|delays?)\b", CRYPTO], [SPEC]),
    ("crypto", 3, "ENFORCEMENT", [r"\b(sec|cftc|doj|justice department|treasury|ofac)\b", CRYPTO, r"\b(sues|sued|charges?|charged|lawsuit|indict\w*|arrest\w*|"
                                                                                             r"settle\w*|dismiss\w*|ban\w*|freez\w*|seiz\w*)\b"], []),
    ("crypto", 3, "HACK", [r"\b(hack\w*|exploit\w*|drained|breach\w*|stolen)\b", r"\b(exchange|binance|coinbase|okx|bybit|kraken|bitfinex|bridge|defi|"
                                                                                r"tether|protocol|million|billion)\b"], []),
    ("crypto", 3, "INSOLVENCY", [r"de-?peg\w*|insolven\w*|bankrupt\w*|halts? withdrawals|withdrawals? (halted|paused|suspended)", CRYPTO], []),
    ("crypto", 3, "MT GOX", [r"mt\.? ?gox"], []),
    ("crypto", 2, "ETF FLOWS", [r"\betfs?\b|\bibit\b|\bfbtc\b", r"\b(bitcoin|btc|ether|crypto)\b",
                                r"\b(inflows?|outflows?|flows?|redemptions?|net (buy\w*|sell\w*)|record|bleed\w*|pull\w*)\b"], []),
    ("crypto", 2, "REGULATION", [r"stablecoin (bill|law|rules)|market structure|clarity act|genius act|crypto (bill|rules|regulation|legislation|framework)"], []),
    ("crypto", 2, "BIG HOLDERS", [r"\b(microstrategy|strategy inc|saylor|blackrock|grayscale|metaplanet|tether|circle)\b",
                                  r"\b(buys?|bought|acquir\w+|purchas\w+|sells?|sold|selling|adds?|added|dump\w*|mint\w*|burn\w*)\b"], []),
    ("crypto", 2, "LIQUIDATIONS", [r"liquidat\w+", CRYPTO], []),
    ("crypto", 1, "BTC MOVE", [r"\b(bitcoin|btc)\b", r"\b(surg\w*|plung\w*|plummet\w*|crash\w*|tumbl\w*|soar\w*|rall(y|ies|ied)|slid\w*|slides?|sinks?|"
                                                      r"record|all-time high|drops?|dropped|falls?|fell|jumps?|jumped|\$\d{2,3},?\d{3}|\d{2,3}k)\b"], []),
    ("markets", 2, "HOOD", [r"\b(robinhood|hood)\b", r"\b(earnings|results|revenue|guidance|sec|fine[sd]?|lawsuit|outage|launch\w*|acquir\w+|"
                                                     r"stock|shares|surg\w*|plung\w*|sink\w*|tumbl\w*|jump\w*|rall\w*|record|downgrad\w*|upgrad\w*|s&p)\b"], []),
    ("crypto", 2, "ETH", [r"\b(ethereum|ether|eth)\b", r"\b(etfs?|upgrade|hard fork|staking|surg\w*|plung\w*|crash\w*|tumbl\w*|rall\w*|record|"
                                                         r"all-time high|liquidat\w+|inflows?|outflows?)\b"], []),
    ("crypto", 2, "HYPE", [r"\b(hyperliquid|hype token|hype price|hypeusdt)\b",
                           r"\b(etfs?|futures|perpetual|list\w*|launch\w*|exploit\w*|hack\w*|outage|halt\w*|unlock\w*|buyback\w*|"
                           r"ice|nyse|cme|coinbase|binance|sec|cftc|surg\w*|plung\w*|crash\w*|tumbl\w*|rall\w*|record|all-time high|"
                           r"liquidat\w+|inflows?|outflows?)\b"], []),
    ("crypto", 1, "BTC", [r"\b(bitcoin|btc)\b"], []),
    ("crypto", 1, "CRYPTO", [CRYPTO], []),
    ("markets", 3, "CRASH", [r"\b(stocks?|wall street|markets?|s&p|nasdaq|dow|equities)\b", r"\b(crash\w*|rout|meltdown|circuit breakers?|bloodbath|"
                                                                                              r"worst day|panic sell\w*)\b"], [SPEC, FOREIGN, r"\bretire\w*|sipp|401k|portfolio\b|smart money"]),
    ("markets", 3, "BANKS", [r"bank (failure|collapse|run)|banking crisis|bank fail\w*"], [SPEC]),
    ("markets", 2, "STOCKS", [r"\b(s&p 500|s&p|nasdaq|dow jones|dow|wall street|stock market|stocks|equities)\b",
                              r"\b(record|slump\w*|tumbl\w*|sell-?off|surg\w*|rall\w*|sink\w*|slid\w*|drop\w*|fall\w*|fell|jump\w*|plung\w*|soar\w*)\b"],
     [r"\bshares\b|stocks? to (buy|watch)|retire\w*|portfolio|dividend"]),
    ("markets", 2, "YIELDS", [r"treasury yields?|10-year (yield|treasury|note|bond)|30-year (yield|treasury|bond)|bond (market|yields?|selloff|rout)|"
                              r"\byields? (surge|spike|jump|soar|climb|fall|drop|tumble)"], []),
    ("markets", 2, "DOLLAR", [r"dollar index|\bdxy\b|\b(us )?dollar (surg\w*|slump\w*|jump\w*|fall\w*|tumbl\w*|rall\w*|weak\w*|strength\w*)|\byen\b"], []),
    ("markets", 2, "OIL", [r"\b(oil|crude|brent|wti|opec)\b"], []),
    ("markets", 2, "GOLD", [r"\bgold\b", r"\b(record|all-time|surg\w*|plung\w*|ounce|rall\w*)\b"], []),
    ("markets", 2, "MEGACAP", [r"\b(nvidia|apple|microsoft|alphabet|google|amazon|meta|tesla)\b", r"\b(earnings|results|guidance|revenue|forecast)\b"], []),
    ("markets", 2, "VOLATILITY", [r"\bvix\b|volatility index|fear gauge"], []),
    ("markets", 1, "MARKETS", [r"\b(stocks|s&p|nasdaq|dow|futures|treasur\w+|bonds?|yields?)\b"], []),
    ("geo", 3, "WAR", [MAJOR, r"\b(declares? war|invasion|invad\w+|nuclear (strike|test|weapons? test|attack)|missile strikes?|air ?strikes?|"
                              r"launch(es|ed)? (missiles?|strikes?|attack)|blockade|attack(s|ed)? on|escalat\w+|retaliat\w+|mobiliz\w+|strikes? (on|against)|"
                              r"bomb(s|ed|ing)|resum\w+ (war|strikes|attacks|fighting))\b"],
     [SPEC, r"\b(kharkiv|kyiv|kiev|odesa|odessa|zaporizhzhia|dnipro|lviv|donetsk|donbas|kherson|sumy)\b|ukraine's energy|war crime"]),
    ("geo", 3, "HORMUZ", [r"strait of hormuz|\bhormuz\b", r"\b(clos\w+|block\w*|mine[sd]?|seiz\w+|attack\w*|shut\w*|tanker)\b"], [SPEC]),
    ("geo", 2, "CONFLICT", [ACTORS, r"\b(war|wars|missiles?|strikes?|attack\w*|troops|military|nuclear|drones?|bomb\w*|ceasefire|truce|"
                                    r"sanctions?|shot down|killed|warships?|navy)\b"], []),
    ("geo", 2, "SANCTIONS", [r"\bsanctions?\b", ACTORS + r"|\b(us|u\.s\.|eu|european union|treasury|ofac|un|western|cuba|venezuela)\b"], []),
    ("geo", 1, "GEO", [ACTORS], []),
]
RULES = [(c, i, t, [re.compile(p, re.I) for p in a], [re.compile(p, re.I) for p in n]) for c, i, t, a, n in RULES]


# Headlines from these outlets count at full impact; anything else needs a second outlet to corroborate it (else capped at 1).
TOP_SOURCES = ("reuters", "bloomberg", "associated press", "ap news", "wsj", "wall street journal", "financial times", "cnbc", "marketwatch",
               "barron", "new york times", "washington post", "axios", "politico", "the hill", "fox business", "cnn", "bbc", "al jazeera",
               "guardian", "nikkei", "south china morning post", "coindesk", "the block", "decrypt", "cointelegraph", "bitcoin magazine",
               "dl news", "blockworks", "yahoo finance", "investing.com", "investinglive", "seeking alpha", "fortune", "business insider", "forbes",
               "npr", "abc news", "cbs news", "nbc news", "times of israel", "jerusalem post", "kyiv independent", "iran international",
               "federal reserve", "white house", "sec", "trump (truth social)", "kitco", "oilprice", "economist", "semafor", "newsweek", "usa today")
US_FEEDS = {"fed", "whitehouse", "sec", "cnbc_top", "cnbc_econ", "cnbc_markets"}


def effective_impact(raw, sources):
    trusted = any(any(t in s.lower() for t in TOP_SOURCES) for s in sources)
    return raw if trusted or len(sources) >= 2 else min(raw, 1)


def classify(text, default_cat, base):
    hits = [(i, c, t) for c, i, t, alls, nones in RULES if all(p.search(text) for p in alls) and not any(p.search(text) for p in nones)]
    if not hits:
        return default_cat, base, []
    hits.sort(key=lambda h: -h[0])  # stable: rule order breaks ties
    tags = []
    for _, _, t in hits:
        if t not in tags:
            tags.append(t)
    return hits[0][1], max(base, hits[0][0]), tags[:3]


# ───────── fetching / parsing
def fetch(url, timeout=12, deadline=30):
    """`timeout` bounds each socket op; `deadline` bounds the whole body read (a feed trickling bytes could hang for minutes)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    end = time.time() + deadline
    with urllib.request.urlopen(req, timeout=timeout) as r:
        chunks = []
        while True:
            if time.time() > end:
                raise TimeoutError(f"body not read within {deadline}s")
            b = r.read(65536)
            if not b:
                return b"".join(chunks)
            chunks.append(b)


def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()


def parse_ts(s):
    if not s:
        return None
    try:
        return parsedate_to_datetime(s).timestamp()
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(s.strip().replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


ATOM = "{http://www.w3.org/2005/Atom}"


def parse_feed(body):
    """-> list of (title, link, ts, source_name or None). Handles RSS 2.0 and Atom."""
    root = ET.fromstring(body)
    out = []
    for it in root.iter("item"):
        src = it.find("source")
        out.append((it.findtext("title") or "", (it.findtext("link") or "").strip(),
                    parse_ts(it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date")),
                    src.text.strip() if src is not None and src.text else None))
    for it in root.iter(ATOM + "entry"):
        link = it.find(ATOM + "link")
        out.append((it.findtext(ATOM + "title") or "", link.get("href", "") if link is not None else "",
                    parse_ts(it.findtext(ATOM + "published") or it.findtext(ATOM + "updated")), None))
    return out


STOP = set("a an the of to in on for and or as at by with from is are was be it its this that after over amid says said new".split())


def tokens(title):
    return {w for w in re.findall(r"[a-z0-9$%.]+", title.lower()) if w not in STOP and len(w) > 1}


class NewsStore:
    """Thread-safe store of tagged, de-duplicated headlines, persisted to data/news.json."""

    def __init__(self, path=STORE):
        self.path = Path(path)
        self.lock = threading.Lock()
        self.items = []
        self.health = {}
        if self.path.exists():
            try:
                d = json.loads(self.path.read_text())
                self.items = d.get("items", [])
                self.health = d.get("health", {})
            except (ValueError, OSError):
                pass
        for it in self.items:  # re-tag with the current rules so rule changes apply to stored headlines too
            it["_tok"] = tokens(it["title"])
            f = FEED.get(it.get("feed"))
            if f:
                it["cat"], it["raw"], it["tags"] = classify(it["title"] + (" [us]" if f[0] in US_FEEDS else ""), f[3], f[4])
                it["impact"] = effective_impact(it["raw"], it["sources"])

    def save(self):
        with self.lock:
            data = {"items": [{k: v for k, v in it.items() if k != "_tok"} for it in self.items], "health": self.health}
        self.path.parent.mkdir(exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False))
        os.replace(tmp, self.path)

    def ingest(self, feed_id, entries, now=None):
        """Merge parsed entries from one feed. Returns the number of new headlines."""
        fid, label, _, cat0, base, keep, _ = FEED[feed_id]
        now = now or time.time()
        added = 0
        with self.lock:
            recent = [x for x in self.items if x["ts"] > now - 86400]
            for title, link, ts, src in entries:
                title = clean(title)
                if fid == "truth":
                    title = "Trump: " + (title[:280] + "…" if len(title) > 280 else title)
                if src and title.endswith(" - " + src):
                    title = title[: -len(src) - 3].strip()
                if len(title) < 12:
                    continue
                ts = min(ts or now, now)
                if ts < now - KEEP_DAYS * 86400:
                    continue
                cat, imp, tags = classify(title + (" [us]" if fid in US_FEEDS else ""), cat0, base)
                if imp < keep:
                    continue
                source = src or label
                tok = tokens(title)
                dup = next((x for x in recent if x["_tok"] and len(tok & x["_tok"]) / max(1, len(tok | x["_tok"])) >= 0.6), None)
                if dup:
                    if source not in dup["sources"]:
                        dup["sources"].append(source)
                    dup["ts"] = min(dup["ts"], ts)
                    if imp > dup.get("raw", dup["impact"]):
                        dup.update(raw=imp, cat=cat, tags=tags)
                    dup["impact"] = effective_impact(dup.get("raw", dup["impact"]), dup["sources"])
                    continue
                item = {"id": hashlib.sha1(title.lower().encode()).hexdigest()[:12], "title": title, "link": link, "sources": [source],
                        "feed": fid, "cat": cat, "raw": imp, "impact": effective_impact(imp, [source]), "tags": tags, "ts": ts, "seen": now,
                        "_tok": tok}
                self.items.append(item)
                recent.append(item)
                added += 1
            self.items = [x for x in self.items if x["ts"] > now - KEEP_DAYS * 86400]
            self.items.sort(key=lambda x: -x["ts"])
            del self.items[4000:]
        return added

    def poll(self, feed_ids, workers=12):
        """Fetch the given feeds in parallel and merge them. Returns {feed_id: new_count or error string}."""
        def one(fid):
            try:
                return fid, parse_feed(fetch(FEED[fid][2])), None
            except Exception as e:  # network / parse errors are reported per feed, never fatal
                return fid, None, f"{type(e).__name__}: {str(e)[:80]}"
        res = {}
        with cf.ThreadPoolExecutor(workers) as ex:
            for fid, entries, err in ex.map(one, feed_ids):
                h = self.health.setdefault(fid, {})
                h["last_try"] = time.time()
                if err:
                    h["error"] = err
                    res[fid] = err
                else:
                    n = self.ingest(fid, entries)
                    h.update(last_ok=time.time(), error=None, entries=len(entries))
                    res[fid] = n
        return res

    def query(self, hours=24, min_impact=1):
        cut = time.time() - hours * 3600
        with self.lock:
            return [{k: v for k, v in x.items() if k != "_tok"} for x in self.items if x["ts"] >= cut and x["impact"] >= min_impact]


# ───────── BTC reaction to each headline
def btc_minutes(symbol="BTCUSDT"):
    """Last ~25h of Binance perp 1m candles for `symbol` -> {minute_ts: (open, close)}."""
    req = urllib.request.Request(f"{fapi_base()}/fapi/v1/klines?symbol={symbol}&interval=1m&limit=1500", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        k = json.load(r)
    return {int(x[0] // 1000): (float(x[1]), float(x[4])) for x in k}


def annotate(items, mins):
    if not mins:
        return items
    last_t = max(mins)
    last_px = mins[last_t][1]
    for it in items:
        m0 = int(it["ts"] // 60 * 60)
        if m0 not in mins:
            continue
        p0 = mins[m0][0]
        mv = {"now": (last_px / p0 - 1) * 100}
        for name, k in (("m15", 14), ("m60", 59)):
            if m0 + k * 60 in mins:
                mv[name] = (mins[m0 + k * 60][1] / p0 - 1) * 100
        it["btc"] = {k: round(v, 3) for k, v in mv.items()}
    return items


# ───────── economic calendar (ForexFactory weekly JSON; they ask for light polling, so cache for an hour)
CAL_URLS = ["https://nfs.faireconomy.media/ff_calendar_thisweek.json", "https://nfs.faireconomy.media/ff_calendar_nextweek.json"]
CAL_COUNTRIES_HIGH = {"USD", "EUR", "JPY", "CNY", "GBP"}


def calendar(max_age=3600):
    cache = {}
    if CAL_STORE.exists():
        try:
            cache = json.loads(CAL_STORE.read_text())
        except ValueError:
            cache = {}
    if time.time() - cache.get("fetched", 0) > max_age:
        events, ok = [], False
        for u in CAL_URLS:
            try:
                events += json.loads(fetch(u))
                ok = True
            except Exception:  # next week's file 404s until it is published
                pass
        if ok:
            cache = {"fetched": time.time(), "events": events}
            CAL_STORE.parent.mkdir(exist_ok=True)
            CAL_STORE.write_text(json.dumps(cache))
    out, seen = [], set()
    for e in cache.get("events", []):
        imp, cty = e.get("impact"), e.get("country")
        if not ((cty == "USD" and imp in ("High", "Medium")) or (cty in CAL_COUNTRIES_HIGH and imp == "High")):
            continue
        ts = parse_ts(e.get("date"))
        key = (e.get("title"), cty, ts)
        if ts is None or key in seen:
            continue
        seen.add(key)
        out.append({"title": e["title"], "country": cty, "impact": imp, "ts": ts,
                    "forecast": e.get("forecast", ""), "previous": e.get("previous", "")})
    out.sort(key=lambda x: x["ts"])
    return {"fetched": cache.get("fetched"), "events": out}


# ───────── CLI
def ago(ts):
    s = int(time.time() - ts)
    return f"{s // 3600}h{s % 3600 // 60:02d}m ago" if s >= 3600 else f"{s // 60}m ago"


def until(ts):
    s = int(ts - time.time())
    if s < 0:  # already released: say how long ago, not "in -1d 23h"
        return f"released {ago(ts)}"
    d, h, m = s // 86400, s % 86400 // 3600, s % 3600 // 60
    return f"in {d}d {h}h" if d else f"in {h}h {m:02d}m"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hours", type=float, default=6)
    ap.add_argument("--min-impact", type=int, default=2)
    ap.add_argument("--days-ahead", type=float, default=7, help="calendar look-ahead")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-fetch", action="store_true", help="read the stored headlines only")
    args = ap.parse_args()

    store = NewsStore()
    res = {} if args.no_fetch else store.poll([f[0] for f in FEEDS])
    if res:
        store.save()
    items = store.query(args.hours, args.min_impact)
    try:
        annotate(items, btc_minutes())
    except Exception as e:
        print(f"(BTC reaction unavailable: {e})")
    cal = calendar()
    if args.json:
        print(json.dumps({"items": items, "calendar": cal, "health": store.health}, ensure_ascii=False))
        return

    bad = [f"{fid} ({err})" for fid, err in res.items() if isinstance(err, str)]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"NEWS  {now}  | {len(FEEDS) - len(bad)}/{len(FEEDS)} feeds ok" + (f" | down: {', '.join(bad)}" if bad else ""))
    print(f"headlines, last {args.hours:g}h, impact >= {args.min_impact} ({len(items)}):")
    for it in items[:60]:
        b = it.get("btc", {})
        mv = "  BTC " + " ".join(f"{k} {v:+.2f}%" for k, v in b.items()) if b else ""
        src = ", ".join(it["sources"][:3]) + (f" +{len(it['sources']) - 3}" if len(it["sources"]) > 3 else "")
        print(f"  {ago(it['ts']):>11}  [{it['impact']} {'/'.join(it['tags']) or it['cat'].upper()}] {it['title'][:150]}  ({src}){mv}")
    print(f"\nupcoming events (next {args.days_ahead:g} days; USD high+medium, EUR/JPY/CNY/GBP high), times UTC:")
    nxt = [e for e in cal["events"] if time.time() - 3600 < e["ts"] < time.time() + args.days_ahead * 86400]
    for e in nxt:
        when = datetime.fromtimestamp(e["ts"], timezone.utc).strftime("%a %d %b %H:%M")
        fp = " | ".join(x for x in (f"fcst {e['forecast']}" if e["forecast"] else "", f"prev {e['previous']}" if e["previous"] else "") if x)
        star = "!!" if e["impact"] == "High" else "  "
        print(f"  {star} {when}  {until(e['ts']):>11}  {e['country']} {e['title']}" + (f"  ({fp})" if fp else ""))
    if not nxt:
        print("  none found (calendar unavailable or quiet week)")


if __name__ == "__main__":
    main()
