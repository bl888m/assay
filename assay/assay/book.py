"""The paper book. Cash, open positions, marks, and resolved P&L.

Paper by default, always. There is no method here that touches a wallet
or an exchange. Going live means writing an executor that reads these same
proposals and signs orders, and that is deliberately not in this repo.

Marks are honest: a YES position bought at price `p0` and now trading at
`p` is marked at `stake * (p / p0)` before fees, i.e. the size of the
position if you closed it at the current quote. Resolution pays out 1 per
share on the winning side and 0 on the other.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .types import Proposal


@dataclass
class Position:
    market_id: str
    question: str
    category: str
    side: str          # YES or NO
    entry: float       # price paid on the chosen side, in [0,1]
    stake: float       # USD committed
    price_now: float   # latest mark price on the chosen side

    def mark(self) -> float:
        # value of the position if closed at the current quote
        if self.entry <= 0:
            return self.stake
        return self.stake * (self.price_now / self.entry)

    def pnl(self) -> float:
        return self.mark() - self.stake


@dataclass
class Book:
    starting_cash: float = 10_000.0
    cash: float = 10_000.0
    positions: list[Position] = field(default_factory=list)
    realized: float = 0.0
    log: list[str] = field(default_factory=list)

    def bankroll(self) -> float:
        return self.starting_cash

    def exposure(self) -> float:
        return sum(p.stake for p in self.positions)

    def count_in_category(self, cat: str) -> int:
        return sum(1 for p in self.positions if p.category == cat)

    def open(self, prop: Proposal) -> None:
        m = prop.market
        entry = m.price if prop.side == "YES" else 1 - m.price
        self.cash -= prop.stake
        self.positions.append(Position(
            market_id=m.id, question=m.question, category=m.category,
            side=prop.side, entry=entry, stake=prop.stake, price_now=entry,
        ))
        self.log.append(
            f"FIRE  {prop.side:3}  ${prop.stake:>7,.2f}  {m.question[:48]}"
        )

    def resolve(self, market_id: str, yes_won: bool) -> float:
        """Settle a position: winning side pays 1/entry per dollar staked."""
        for pos in list(self.positions):
            if pos.market_id != market_id:
                continue
            won = (pos.side == "YES") == yes_won
            payout = (pos.stake / pos.entry) if (won and pos.entry > 0) else 0.0
            self.cash += payout
            self.realized += payout - pos.stake
            self.positions.remove(pos)
            return payout - pos.stake
        return 0.0

    def equity(self) -> float:
        return self.cash + sum(p.mark() for p in self.positions)
