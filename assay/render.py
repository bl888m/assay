"""Terminal output. One card per market, one summary block for the book.

The desk shows its work: Ilsa's estimate, Kett's size, Bram's verdict are
each tagged with the agent that produced them, so the output reads like a
team and not a monolith. Plain monospace, no color codes in the strings so
it pastes cleanly into a README.
"""

from __future__ import annotations

from .types import Decision
from .book import Book
from .desk import DESK

_W = 68

WORDMARK = (
    " █████╗ ███████╗███████╗ █████╗ ██╗   ██╗\n"
    "██╔══██╗██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝\n"
    "███████║███████╗███████╗███████║ ╚████╔╝ \n"
    "██╔══██║╚════██║╚════██║██╔══██║  ╚██╔╝  \n"
    "██║  ██║███████║███████║██║  ██║   ██║   \n"
    "╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   "
)


def rule(ch: str = "-") -> str:
    return ch * _W


def header(source: str, n: int, bankroll: float, research: str = "off") -> str:
    r = "Holt:on" if research == "llm" else "Holt:off"
    return "\n".join([
        "",
        WORDMARK,
        "  the six-agent desk for prediction markets  ·  paper by default",
        rule("="),
        f"  desk: 6 agents   source: {source:<10} {r}   "
        f"markets: {n:<3}   bankroll: ${bankroll:,.0f}",
        rule("="),
    ])


def card(d: Decision) -> str:
    p = d.proposal
    m = p.market
    est = p.estimate

    lines = [
        f"  [{m.category:<8}] {m.question[:_W - 20]}",
        f"      price {m.price:>5.1%}  Ilsa {est.q:>5.1%}   "
        f"edge {p.side} {p.edge:>+5.1%}",
        f"      liq ${m.liquidity:>8,.0f}  vol ${m.volume_24h:>8,.0f}  "
        f"{m.hours_to_resolve:>4.0f}h",
    ]

    comp = "  ".join(f"{k[:4]} {v:+.1%}" for k, v in est.components.items())
    lines.append(f"      why  {comp}")
    if est.note:
        lines.append(f"      Holt \"{est.note}\"")

    if d.verdict == "FIRE":
        lines.append(f"      Kett {p.side} ${p.stake:,.2f}  f* {p.kelly_fraction:.1%}"
                     f"      Bram FIRE")
    else:
        lines.append(f"      Kett {p.side} edge {p.edge:+.1%}"
                     f"      Bram PASS  {d.reason}")

    return "\n".join(lines)


def book_summary(book: Book) -> str:
    open_pnl = sum(pos.pnl() for pos in book.positions)
    equity = book.equity()
    ret = (equity / book.starting_cash - 1) if book.starting_cash else 0

    lines = [
        rule("="),
        "  TESS / PORTFOLIO",
        rule("-"),
        f"  equity     ${equity:>10,.2f}   ({ret:+.2%})",
        f"  cash       ${book.cash:>10,.2f}",
        f"  exposure   ${book.exposure():>10,.2f}   ({len(book.positions)} open)",
        f"  realized   ${book.realized:>+10,.2f}",
        f"  open P&L   ${open_pnl:>+10,.2f}",
    ]
    if book.positions:
        lines.append(rule("-"))
        lines.append("  OPEN POSITIONS")
        for pos in sorted(book.positions, key=lambda x: x.pnl(), reverse=True):
            lines.append(
                f"    {pos.side:3}  ${pos.stake:>7,.2f}  "
                f"{pos.pnl():>+8,.2f}  {pos.question[:34]}"
            )
    lines.append(rule("="))
    return "\n".join(lines)


def desk_roster() -> str:
    lines = [rule("="), "  THE DESK", rule("-")]
    for a in DESK:
        lines.append(f"  {a.handle:<5} {a.role:<10} {a.job}")
    lines.append(rule("-"))
    lines.append("  not chatbots. six small modules you can read and test.")
    lines.append("  only Holt can call a model, and only when you ask.")
    lines.append(rule("="))
    return "\n".join(lines)
