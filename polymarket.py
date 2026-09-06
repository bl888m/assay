"""Live markets from Polymarket's public Gamma API.

No key needed. This is the real path: `assay scan --source polymarket`
reads open binary markets, normalises them into the same `Market` shape
the simulator produces, and the rest of the pipeline cannot tell the
difference.

It carries no `true_prob`, so paper mode against a live source marks
positions to the current price and only realises P&L when a market
actually resolves. Nothing here signs or sends anything.
"""

from __future__ import annotations

import json
from urllib.request import urlopen, Request

from ..types import Market

GAMMA = "https://gamma-api.polymarket.com/markets"


def _get(url: str) -> list:
    req = Request(url, headers={"User-Agent": "assay/0.1"})
    with urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def fetch(limit: int = 40) -> list[Market]:
    # active, unresolved, ordered by liquidity so we look at markets that
    # can actually absorb a stake
    url = (f"{GAMMA}?closed=false&active=true&limit={limit}"
           f"&order=liquidityNum&ascending=false")
    rows = _get(url)

    out: list[Market] = []
    for m in rows:
        # Gamma returns outcomePrices as a JSON-encoded string like
        # "[\"0.62\", \"0.38\"]"; the first entry is YES.
        try:
            prices = json.loads(m.get("outcomePrices") or "[]")
            price = float(prices[0])
        except (ValueError, IndexError, TypeError):
            continue
        if not (0.0 < price < 1.0):
            continue

        liquidity = float(m.get("liquidityNum") or m.get("liquidity") or 0)
        volume = float(m.get("volume24hr") or 0)

        # Gamma gives oneDayPriceChange as a signed fraction when present.
        try:
            change = float(m.get("oneDayPriceChange") or 0)
        except (ValueError, TypeError):
            change = 0.0
        price_24h_ago = min(max(price - change, 0.01), 0.99)

        hours = _hours_to(m.get("endDate"))
        if hours is None or hours <= 0:
            continue

        out.append(Market(
            id=str(m.get("id") or m.get("conditionId") or m.get("slug")),
            question=(m.get("question") or m.get("title") or "").strip(),
            category=(m.get("category") or "Other"),
            price=round(price, 4),
            liquidity=round(liquidity, 0),
            volume_24h=round(volume, 0),
            hours_to_resolve=round(hours, 1),
            price_24h_ago=round(price_24h_ago, 4),
            true_prob=None,
        ))
    return out


def _hours_to(end_date: str | None) -> float | None:
    if not end_date:
        return None
    from datetime import datetime, timezone
    try:
        end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    except ValueError:
        return None
    delta = end - datetime.now(timezone.utc)
    return delta.total_seconds() / 3600
