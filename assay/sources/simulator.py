"""A deterministic prediction-market generator.

The default source. It exists so a demo run is reproducible and works
with no network, the same way bodkin defaults to a dry run. Every market
carries a hidden `true_prob` so paper mode can resolve positions and show
real P&L instead of a made-up number.

The generator is seeded. Same seed, same markets, same run, forever.
"""

from __future__ import annotations

import random
from math import log, exp

from ..types import Market

CATEGORIES = ["Politics", "Crypto", "Sports", "Econ", "Tech", "Weather", "Culture"]

_TEMPLATES = {
    "Politics": [
        "Will {p} win the {y} nomination?",
        "Will {p} be confirmed before {m}?",
        "Government shutdown before {m}?",
    ],
    "Crypto": [
        "Will BTC close above ${k}k in {m}?",
        "Will ETH flip ${k}00 by {m}?",
        "Will a spot {p} ETF be approved in {y}?",
    ],
    "Sports": [
        "Will {p} reach the final?",
        "Will {p} win on Sunday?",
        "Over {k}.5 goals in {p} vs {q}?",
    ],
    "Econ": [
        "Will the Fed cut in {m}?",
        "CPI above {k}% for {m}?",
        "Will unemployment tick up in {m}?",
    ],
    "Tech": [
        "Will {p} ship {q} before {m}?",
        "Will {p} IPO in {y}?",
        "Will {p} pass {k}M users by {m}?",
    ],
    "Weather": [
        "Will a named storm hit {p} in {m}?",
        "Warmest {m} on record for {p}?",
    ],
    "Culture": [
        "Will {p} win Best Picture?",
        "Will {p} debut at number one?",
    ],
}

_NAMES = ["Atlas", "Corvi", "Delphi", "Ember", "Frost", "Gale", "Halcyon",
          "Ives", "Juno", "Koda", "Lumen", "Mira", "Nox", "Orion", "Perla",
          "Quill", "Rune", "Sable", "Tycho", "Umbra", "Vesper", "Wren"]
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
           "Oct", "Nov", "Dec"]


def _logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return log(p / (1 - p))


def _sigmoid(x: float) -> float:
    return 1 / (1 + exp(-x))


def generate(n: int = 12, seed: int = 7) -> list[Market]:
    rng = random.Random(seed)
    out: list[Market] = []
    for i in range(n):
        cat = rng.choice(CATEGORIES)
        tmpl = rng.choice(_TEMPLATES[cat])
        q = tmpl.format(
            p=rng.choice(_NAMES), q=rng.choice(_NAMES),
            m=rng.choice(_MONTHS), y=rng.choice([2026, 2027]),
            k=rng.choice([2, 3, 4, 90, 100, 120]),
        )

        # A crowd price drawn to over-represent the extremes, the way real
        # books do. This is what makes the favorite-longshot inefficiency
        # show up at all.
        price = round(min(max(rng.betavariate(0.7, 0.7), 0.03), 0.97), 3)

        # The hidden truth: the crowd is biased at the extremes. Longshots
        # are a touch too dear, favorites a touch too cheap. We bake exactly
        # that into the ground truth, then add idiosyncratic noise so no
        # single rule is a free lunch.
        base = _sigmoid(_logit(price) * 1.18)
        true_prob = min(max(base + rng.gauss(0, 0.06), 0.01), 0.99)

        drift = rng.gauss(0, 0.05)
        price_24h_ago = round(min(max(price - drift, 0.02), 0.98), 3)

        liquidity = round(rng.lognormvariate(9.5, 1.1), 0)       # ~USD 13k median
        volume_24h = round(liquidity * rng.uniform(0.2, 3.0), 0)
        hours = round(rng.choice([6, 18, 48, 120, 360, 720]) * rng.uniform(0.6, 1.4), 1)

        out.append(Market(
            id=f"sim-{i:03d}",
            question=q,
            category=cat,
            price=price,
            liquidity=liquidity,
            volume_24h=volume_24h,
            hours_to_resolve=hours,
            price_24h_ago=price_24h_ago,
            true_prob=true_prob,
        ))
    return out
