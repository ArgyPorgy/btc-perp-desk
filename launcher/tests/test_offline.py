"""Offline tests (no network, no money).  .venv/bin/python tests/test_offline.py"""
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from launcher import decide_exit, wanted  # noqa: E402
from ledger import Limits  # noqa: E402
from media import render_card  # noqa: E402
from naming import CoinIdea, finalize, name_with_rules  # noqa: E402
from settings import Config, load_config  # noqa: E402
from tweets import Tweet  # noqa: E402


def test_guardrails_scrub_names():
    idea = finalize(CoinIdea(True, "x", "Official Elon Token", "REAL-ELON!", "the real one", "claude"), "elonmusk")
    assert "official" not in idea.name.lower() and idea.ticker == "ELON", idea
    assert idea.description.endswith("Not affiliated with @elonmusk."), idea.description
    assert len(finalize(CoinIdea(True, "", "x" * 80, "ABCDEFGHIJKLMNOP", "", "rules"), "a").name) <= 32


def test_rules_naming():
    idea = finalize(name_with_rules("just taught my Dog to trade futures https://t.co/x"), "someone")
    assert idea.launch and idea.ticker == "DOG" and "http" not in idea.name, idea
    assert not finalize(name_with_rules("https://t.co/abc"), "x").launch


def test_card_is_png():
    data, mime = render_card("GIGA", "Gigabrain Energy")
    assert mime == "image/png" and data[:8] == b"\x89PNG\r\n\x1a\n"


def test_exit_rules():
    c = Config(accounts=["a"])
    assert decide_exit(60, 30, 1, 3, c) == "take_profit"
    assert decide_exit(17, 30, 1, 3, c) == "stop_loss"
    assert decide_exit(30, 30, 5.1, 0, c) == "no_outside_buyers"
    assert decide_exit(30, 30, 3, 0, c) is None
    assert decide_exit(31, 30, 15, 4, c) == "time_limit"
    assert decide_exit(None, None, 1, 0, c) is None


def test_limits():
    c = Config(accounts=["a"], max_launches_per_day=2, max_sol_per_day=1.0, min_seconds_between_launches=0,
               author_cooldown_minutes=30)
    with tempfile.TemporaryDirectory() as d:
        lim = Limits(c, Path(d) / "s.json")
        assert lim.check("alice", "AAA", 0.05)[0]
        lim.record("alice", "AAA", 0.05)
        assert not lim.check("alice", "BBB", 0.05)[0]          # author cooldown
        assert not lim.check("bob", "AAA", 0.05)[0]            # same ticker today
        assert not lim.check("bob", "CCC", 0.99)[0]            # SOL cap
        lim.record("bob", "CCC", 0.05)
        assert not lim.check("carol", "DDD", 0.05)[0]          # daily count
        assert len(Limits(c, Path(d) / "s.json").state["launches"]) == 2  # persisted


def test_config_rejects_big_dev_buy():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"accounts": ["a"], "dev_buy_sol": 5}, f)
    try:
        load_config(Path(f.name))
    except ValueError as e:
        assert "dev_buy_sol" in str(e)
    else:
        raise AssertionError("5 SOL dev buy should be rejected")


def test_wanted_filters():
    c = Config(accounts=["a"], keywords=["dog"])
    fresh = Tweet("1", "", "my dog", "a", time.time())
    assert wanted(fresh, c) == ""
    assert wanted(Tweet("2", "", "my cat", "a", time.time()), c) == "no keyword match"
    assert wanted(Tweet("3", "", "my dog", "a", time.time() - 999), c) == "too old"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok ", name)
