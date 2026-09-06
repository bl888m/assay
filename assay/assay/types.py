"""Shared types. Small, boring, and readable on purpose.

Everything that flows through the pipeline is one of these. No agent
passes another a blob of free text it has to re-parse; each stage adds
typed fields and hands the same object on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Market:
    """A binary prediction market, normalised across sources."""

    id: str
    question: str
    category: str
    price: float            # market implied probability of YES, in [0, 1]
    liquidity: float        # resting depth, in USD
    volume_24h: float       # traded in the last 24h, in USD
    hours_to_resolve: float
    price_24h_ago: float    # for the momentum tilt
    # sources may not fill these; the simulator does so paper mode can resolve
    true_prob: Optional[float] = None


@dataclass
class Estimate:
    """assay's own probability for YES, with the reasons it moved off price."""

    q: float                # estimated probability of YES
    price: float            # the crowd price it started from
    components: dict = field(default_factory=dict)  # name -> signed contribution
    note: str = ""          # Holt's one-line reason, when research is on


@dataclass
class Proposal:
    """A side, a size, and the numbers behind them. Not an order yet."""

    market: Market
    estimate: Estimate
    side: str               # "YES" or "NO"
    edge: float             # estimate minus price, on the chosen side
    kelly_fraction: float   # fraction of bankroll, after the fractional-Kelly haircut
    stake: float            # USD, after caps


@dataclass
class Decision:
    """What risk did with a proposal, and why."""

    proposal: Proposal
    verdict: str            # "FIRE" or "PASS"
    reason: str             # the binding rule when PASS, or "" when FIRE
