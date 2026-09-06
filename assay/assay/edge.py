"""Edge and size.

Given a market price `p` and our estimate `q`, pick the side with positive
expected value and size it by the Kelly criterion, then take a haircut.

For a binary contract that costs `p` and pays 1, buying YES has
    Kelly fraction  f* = (q - p) / (1 - p)
and buying NO is the mirror with (1 - q) and (1 - p) swapped. We only ever
bet the side with positive edge, so f* is non-negative by construction.

Full Kelly is correct in the limit and far too violent in practice: it
assumes the estimate is exactly right. We bet a fixed fraction of it
(`KELLY_FRACTION`, quarter-Kelly by default), which is the standard way to
stay solvent when your probabilities are only approximately calibrated.
"""

from __future__ import annotations

from .types import Market, Estimate, Proposal

# Quarter-Kelly. Lower is more timid and much harder to blow up.
KELLY_FRACTION = 0.25


def propose(m: Market, est: Estimate, bankroll: float) -> Proposal:
    p, q = m.price, est.q

    yes_edge = q - p
    no_edge = (1 - q) - (1 - p)   # == p - q

    if yes_edge >= no_edge:
        side, edge, price = "YES", yes_edge, p
    else:
        side, edge, price = "NO", no_edge, 1 - p

    # Kelly on the chosen side. If edge <= 0 the fraction is clamped to 0
    # and risk will PASS it anyway.
    if edge > 0 and price < 1:
        full_kelly = edge / (1 - price)
    else:
        full_kelly = 0.0

    f = max(0.0, full_kelly * KELLY_FRACTION)
    stake = round(f * bankroll, 2)

    return Proposal(
        market=m,
        estimate=est,
        side=side,
        edge=round(edge, 4),
        kelly_fraction=round(f, 4),
        stake=stake,
    )
