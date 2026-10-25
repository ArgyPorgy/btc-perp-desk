"""Load .env and config.json, validate them, and hold the guardrails that config cannot change."""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Hard guardrails: deliberately not configurable.
HARD_MAX_DEV_BUY_SOL = 1.0
EST_FEES_PER_LAUNCH_SOL = 0.03  # mint rent + priority fees + PumpPortal's 0.5% on the dev buy, rounded up
BANNED_WORDS = ("official", "verified", "real", "team", "airdrop", "presale")


def load_env(path: Path = ROOT / ".env") -> None:
    """Minimal KEY=VALUE loader so secrets live in .env, never in code or config.json."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        if value:  # blank placeholders must not count as credentials
            os.environ.setdefault(key.strip(), value)


@dataclass
class Config:
    dry_run: bool = True
    accounts: list = field(default_factory=list)
    keywords: list = field(default_factory=list)
    ignore_replies: bool = True
    ignore_retweets: bool = True
    poll_seconds: float = 10
    max_tweet_age_seconds: float = 120
    dev_buy_sol: float = 0.05
    slippage_pct: float = 15
    priority_fee_sol: float = 0.0005
    take_profit_multiple: float = 2.0
    stop_loss_multiple: float = 0.6
    max_hold_minutes: float = 15
    sell_if_no_outside_buyer_minutes: float = 5
    max_launches_per_day: int = 10
    max_sol_per_day: float = 1.0
    min_seconds_between_launches: float = 60
    author_cooldown_minutes: float = 30
    claim_creator_fees_every_hours: float = 6
    use_claude: bool = True
    claude_model: str = "claude-opus-5-5"
    rules_fallback_live: bool = False  # rule-based names can't tell a meme from an ad, so live mode skips them


def load_config(path: Path) -> Config:
    raw = json.loads(Path(path).read_text())
    known = Config.__dataclass_fields__
    unknown = [k for k in raw if k not in known and not k.startswith("_")]
    if unknown:
        raise ValueError(f"Unknown config keys: {unknown}")
    cfg = Config(**{k: v for k, v in raw.items() if k in known})
    cfg.accounts = [a.lstrip("@").strip() for a in cfg.accounts if a.strip()]
    if not cfg.accounts:
        raise ValueError("config.accounts is empty - list the X accounts to watch")
    if not 0 <= cfg.dev_buy_sol <= HARD_MAX_DEV_BUY_SOL:
        raise ValueError(f"dev_buy_sol must be between 0 and {HARD_MAX_DEV_BUY_SOL} SOL")
    if not 1 <= cfg.slippage_pct <= 50:
        raise ValueError("slippage_pct must be between 1 and 50")
    if not 0 < cfg.stop_loss_multiple < 1 < cfg.take_profit_multiple:
        raise ValueError("need 0 < stop_loss_multiple < 1 < take_profit_multiple")
    if cfg.max_sol_per_day <= 0 or cfg.max_launches_per_day <= 0:
        raise ValueError("daily limits must be positive")
    if cfg.poll_seconds < 3:
        raise ValueError("poll_seconds below 3 burns API credit for little gain")
    return cfg
