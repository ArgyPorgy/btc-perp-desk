"""Tweet sources: twitterapi.io polling (live) and a JSON replay file (testing)."""
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import requests


@dataclass
class Tweet:
    id: str
    url: str
    text: str
    author: str
    created_ts: float
    media_urls: list = field(default_factory=list)


def _parse(t: dict) -> Tweet:
    created = t.get("createdAt") or ""
    try:
        ts = datetime.strptime(created, "%a %b %d %H:%M:%S %z %Y").timestamp()
    except ValueError:
        ts = time.time()
    media = []
    for holder in (t.get("extendedEntities") or {}, t.get("entities") or {}):
        for m in holder.get("media") or []:
            url = m.get("media_url_https") or m.get("url")
            if m.get("type", "photo") == "photo" and url and url not in media:
                media.append(url)
    author = (t.get("author") or {}).get("userName", "")
    return Tweet(id=str(t.get("id")), url=t.get("url") or f"https://x.com/{author}/status/{t.get('id')}",
                 text=t.get("text") or "", author=author, created_ts=ts, media_urls=media)


class TwitterApiIo:
    """Polls twitterapi.io advanced search for new tweets from the watched accounts."""

    URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    GROUP = 8  # accounts per query, keeps the search string short

    def __init__(self, api_key: str, accounts: list, ignore_replies: bool, ignore_retweets: bool):
        self.session = requests.Session()
        self.session.headers["X-API-Key"] = api_key
        self.groups = [accounts[i:i + self.GROUP] for i in range(0, len(accounts), self.GROUP)]
        self.suffix = (" -filter:replies" if ignore_replies else "") + (" -filter:retweets" if ignore_retweets else "")

    def fetch_new(self, since_ts: float) -> list:
        out = []
        for group in self.groups:
            query = "(" + " OR ".join(f"from:{a}" for a in group) + f") since_time:{int(since_ts)}" + self.suffix
            r = self.session.get(self.URL, params={"query": query, "queryType": "Latest"}, timeout=15)
            r.raise_for_status()
            out += [_parse(t) for t in r.json().get("tweets") or []]
        return out

    exhausted = False


class ReplaySource:
    """Feeds tweets from a JSON file (same shape as twitterapi.io) once, for dry-run testing."""

    def __init__(self, path: Path):
        self.tweets = [_parse(t) for t in json.loads(Path(path).read_text())]
        self.exhausted = False

    def fetch_new(self, since_ts: float) -> list:
        if self.exhausted:
            return []
        self.exhausted = True
        now = time.time()
        for t in self.tweets:  # pretend they were just posted
            t.created_ts = now
        return self.tweets
