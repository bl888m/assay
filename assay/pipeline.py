"""The pipeline. Six agents, each a plain function, wired in order.

    Rigo   scout      pick the universe of markets       sources/*
    Holt   research   add context (optional model call)  research.py
    Ilsa   analyse    estimate the true probability       model.py
    Kett   size       choose a side and a Kelly stake     edge.py
    Bram   risk       approve or refuse, with a reason    risk.py
    Tess   allocate   record it in the paper book         book.py

The named agents map one-to-one onto these functions. They are not
chatbots and, except for Holt when you turn it on, they do not call a
model. Each is a small unit you can read in a minute and test in
isolation. The names are for the story; the code is boring so it can be
trusted.
"""

from __future__ import annotations

from collections.abc import Iterable

from .types import Market, Decision
from . import model, edge, risk, research
from .book import Book


def run(markets: Iterable[Market], book: Book, limits: risk.Limits,
        research_mode: str = "off") -> list[Decision]:
    decisions: list[Decision] = []

    # Rigo has already handed us the universe. Holt and Ilsa score each
    # market; we look at the strongest edges first so Bram's caps bind on
    # the best trades rather than whatever arrived first.
    scored = []
    for m in markets:
        delta, note = research.research(m, research_mode)   # Holt (0.0 when off)
        est = model.estimate(m, delta, note or "")          # Ilsa
        prop = edge.propose(m, est, book.bankroll())        # Kett
        scored.append((prop.edge, m, est, prop))
    scored.sort(key=lambda t: t[0], reverse=True)

    for _, m, est, prop in scored:
        decision = risk.check(prop, book, limits)           # Bram
        if decision.verdict == "FIRE":
            book.open(decision.proposal)                    # Tess
        decisions.append(decision)
    return decisions
