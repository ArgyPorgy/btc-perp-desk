"""Coin image: the tweet's own photo when it has one, otherwise a generated ticker card."""
import hashlib
import io
import textwrap

import requests
from PIL import Image, ImageDraw, ImageFont

MAX_BYTES = 4_000_000


def fetch_image(url: str):
    """Returns (bytes, mime) or None. Re-encodes to PNG so pump.fun always gets a clean image."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        if not r.headers.get("content-type", "").startswith("image/") or len(r.content) > MAX_BYTES:
            return None
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        img.thumbnail((1000, 1000))
        buf = io.BytesIO()
        img.save(buf, "PNG")
        return buf.getvalue(), "image/png"
    except Exception:
        return None


def render_card(ticker: str, name: str):
    h = hashlib.sha256(ticker.encode()).digest()
    bg = (40 + h[0] % 150, 40 + h[1] % 150, 40 + h[2] % 150)
    img = Image.new("RGB", (600, 600), bg)
    d = ImageDraw.Draw(img)
    big = ImageFont.load_default(size=110 if len(ticker) <= 6 else 70)
    small = ImageFont.load_default(size=40)
    d.text((300, 250), f"${ticker}", font=big, fill="white", anchor="mm")
    d.multiline_text((300, 420), "\n".join(textwrap.wrap(name, 22)[:3]), font=small, fill="white",
                     anchor="mm", align="center")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue(), "image/png"
