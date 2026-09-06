"""Risk. The part that says no.

A proposal with a fat edge is not a trade until it clears every check
below. When it fails, the decision names the single binding rule, so the
log reads like a reason and not a shrug. No agent overrides this.

The point of this file existing at all: assay is not "an AI that presses
BUY". It is a sizing-and-refusal engine with an estimate bolted on the
front. Most of what it does is decline.
"""

from __future__ import annotations

from dataclasses import dataclass

from .types import Proposal, Decision
from .book import Book


@dataclass
class Limits:
    min_edge: float = 0.04           # ignore edges thinner than the noise
    min_liquidity: float = 5_000.0   # USD of depth, or we can't get filled
    min_hours: float = 6.0           # no lottery tickets that resolve tonight
    max_position_frac: float = 0.05  # cap any single market at 5% of bankroll
    max_exposure_frac: float = 0.60  # keep this much of the book unlevered
    max_per_category: int = 3        # correlation guard, crude but honest


def check(prop: Proposal, book: Book, limits: Limits) -> Decision:
    m = prop.market

    if prop.edge < limits.min_edge:
        return _pass(prop, f"edge {prop.edge:.1%} < {limits.min_edge:.0%} floor")

    if m.liquidity < limits.min_liquidity:
        return _pass(prop, f"liquidity ${m.liquidity:,.0f} < ${limits.min_liquidity:,.0f}")

    if m.hours_to_resolve < limits.min_hours:
        return _pass(prop, f"resolves in {m.hours_to_resolve:.0f}h < {limits.min_hours:.0f}h")

    bankroll = book.bankroll()
    cap = limits.max_position_frac * bankroll
    stake = min(prop.stake, cap)
    if stake <= 0:
        return _pass(prop, "sized to zero after Kelly haircut")

    if book.exposure() + stake > limits.max_exposure_frac * bankroll:
        return _pass(prop, f"would breach {limits.max_exposure_frac:.0%} exposure ceiling")

    if book.count_in_category(m.category) >= limits.max_per_category:
        return _pass(prop, f"already {limits.max_per_category} open in {m.category}")

    # capped stake wins
    prop.stake = round(stake, 2)
    return Decision(proposal=prop, verdict="FIRE", reason="")


def _pass(prop: Proposal, reason: str) -> Decision:
    return Decision(proposal=prop, verdict="PASS", reason=reason)
