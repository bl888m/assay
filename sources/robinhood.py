"""Rigo, pointed at Robinhood.

Robinhood gave everyone the buy button, then event contracts, prediction
markets you can reach from a retail account. This adapter maps those
markets into the same `Market` shape the rest of the desk consumes, so
`assay scan --source robinhood` runs the identical pipeline over them.

Robinhood's event-contract endpoints move and some sit behind an
authenticated session, so the base URL and any token are read from the
environment rather than hard-coded:

    RH_API_BASE   the markets endpoint that returns open event contracts
    RH_TOKEN      optional bearer token for an authenticated session

Point those at the endpoint you have access to. Like every source, this
one only reads. It never places an order. Paper stays paper.
"""

from __future__ import annotations

import json
import os
from urllib.request import urlopen, Request

from ..types import Market


def fetch(limit: int = 40) -> list[Market]:
    base = os.environ.get("RH_API_BASE")
    if not base:
        raise SystemExit(
            "set RH_API_BASE to a Robinhood event-contracts endpoint. "
            "the public source that works out of the box is --source polymarket."
        )

    headers = {"User-Agent": "assay/0.2", "Accept": "application/json"}
    if os.environ.get("RH_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['RH_TOKEN']}"

    req = Request(f"{base}?limit={limit}", headers=headers)
    with urlopen(req, timeout=15) as r:
        payload = json.loads(r.read().decode())

    rows = payload.get("results") or payload.get("markets") or payload
    out: list[Market] = []
    for m in rows:
        price = _yes_price(m)
        if price is None or not (0.0 < price < 1.0):
            continue
        out.append(Market(
            id=str(m.get("id") or m.get("market_id") or m.get("symbol")),
            question=(m.get("title") or m.get("question") or "").strip(),
            category=(m.get("category") or "Robinhood"),
            price=round(price, 4),
            liquidity=float(m.get("liquidity") or m.get("open_interest") or 0),
            volume_24h=float(m.get("volume") or 0),
            hours_to_resolve=float(m.get("hours_to_close") or 48),
            price_24h_ago=round(price, 4),
            true_prob=None,
        ))
    return out


def _yes_price(m: dict) -> float | None:
    for key in ("yes_price", "last_price", "price", "implied_probability"):
        if key in m and m[key] is not None:
            try:
                v = float(m[key])
                return v / 100 if v > 1 else v   # accept cents or a fraction
            except (ValueError, TypeError):
                continue
    return None
