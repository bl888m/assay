"""The estimate. This is the part everyone wants to be magic. It is not.

assay's probability for YES starts from the crowd price and moves off it
for two reasons only, both of which you can read and argue with:

1. Favorite-longshot recalibration.
   In real betting and prediction markets longshots are systematically
   overbet and favorites underbet. The signed size of this bias is one of
   the oldest documented facts in the field. We correct for it by
   stretching the price in logit space by a single slope `k > 1`: pull
   longshot prices down, push favorite prices up. One number, auditable.

2. A momentum tilt.
   A market that moved over the last 24h tends to keep drifting a little.
   We nudge the estimate in the direction of the move, capped hard so it
   can never dominate the recalibration.

That is the whole model. No hidden state, no unfalsifiable "confidence".
When you want news, order-flow or an LLM research pass, it plugs in here
as a third component with its own weight, and it shows up by name in the
`components` dict so a human can see exactly how much it moved the number.
"""

from __future__ import annotations

from math import log, exp

from .types import Market, Estimate

# The single knob behind the recalibration. k = 1.0 trusts the crowd
# exactly. Above 1.0 it corrects the favorite-longshot bias; below 1.0 it
# would fade favorites, which is the losing side historically.
LOGIT_SLOPE = 1.18

# How far a full 24h swing is allowed to move the estimate, in probability.
MOMENTUM_CAP = 0.04


def _logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return log(p / (1 - p))


def _sigmoid(x: float) -> float:
    return 1 / (1 + exp(-x))


def estimate(m: Market, research_delta: float = 0.0,
             research_note: str = "") -> Estimate:
    price = m.price

    # 1. recalibrate
    recal = _sigmoid(_logit(price) * LOGIT_SLOPE)
    recal_contrib = recal - price

    # 2. momentum, capped
    move = m.price - m.price_24h_ago
    mom_contrib = max(-MOMENTUM_CAP, min(MOMENTUM_CAP, move * 0.5))

    # 3. Holt's research vote, already capped upstream. 0.0 when off.
    q = min(max(recal + mom_contrib + research_delta, 0.01), 0.99)

    components = {
        "recalibration": round(recal_contrib, 4),
        "momentum": round(mom_contrib, 4),
    }
    if research_delta:
        components["research"] = round(research_delta, 4)

    return Estimate(
        q=round(q, 4),
        price=price,
        components=components,
        note=research_note or "",
    )
