"""Build the board's data snapshot from a run.

`assay board` runs the desk once, serialises the result into a plain object,
writes it as board/data.js (so the page loads with no server and no fetch),
and opens the page. Nothing here is live: it is a snapshot of one paper run,
the same numbers the terminal prints, drawn as a desk.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

from .book import Book
from .desk import DESK
from .pipeline import run
from .risk import Limits, check
from . import model, edge, research


def _score(edge_val: float) -> int:
    return max(0, min(100, round(min(edge_val, 0.10) / 0.10 * 100)))


def build(markets, limits: Limits, bankroll: float,
          source: str, holt: bool, seed: int) -> dict:
    book = Book(starting_cash=bankroll, cash=bankroll)
    decisions = run(markets, book, limits,
                    research_mode="llm" if holt else "off")

    rows = []
    fired = 0
    for d in decisions:
        p = d.proposal
        m = p.market
        if d.verdict == "FIRE":
            fired += 1
        rows.append({
            "question": m.question,
            "category": m.category,
            "price": round(m.price, 4),
            "estimate": round(p.estimate.q, 4),
            "edge": round(p.edge, 4),
            "side": p.side,
            "score": _score(p.edge),
            "verdict": d.verdict,
            "reason": d.reason,
            "stake": round(p.stake, 2),
        })
    # strongest first
    rows.sort(key=lambda r: (r["verdict"] != "FIRE", -r["edge"]))

    desk = []
    for a in DESK:
        if a.role == "Scout":
            status = f"pulled {len(decisions)}"
        elif a.role == "Research":
            status = "on" if holt else "idle · off"
        elif a.role == "Analyst":
            status = f"scored {len(decisions)}"
        elif a.role == "Trader":
            status = f"sized {len(decisions)}"
        elif a.role == "Risk":
            status = f"fired {fired}, passed {len(decisions) - fired}"
        else:
            status = f"{len(book.positions)} open"
        desk.append({"handle": a.handle, "role": a.role, "status": status})

    booklist = [{
        "side": pos.side,
        "question": pos.question[:30],
        "stake": round(pos.stake, 2),
        "pnl": round(pos.pnl(), 2),
    } for pos in book.positions]

    return {
        "generated": _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": source,
        "holt": holt,
        "seed": seed,
        "stats": {
            "scanned": len(decisions),
            "fired": fired,
            "open": len(book.positions),
            "equity": round(book.equity(), 2),
            "cash": round(book.cash, 2),
            "exposure": round(book.exposure(), 2),
            "ret": round(book.equity() / book.starting_cash - 1, 4),
        },
        "desk": desk,
        "markets": rows,
        "book": booklist,
        "limits": {
            "min_edge": limits.min_edge,
            "min_liquidity": int(limits.min_liquidity),
            "min_hours": int(limits.min_hours),
            "max_position_frac": limits.max_position_frac,
            "max_exposure_frac": limits.max_exposure_frac,
            "max_per_category": limits.max_per_category,
        },
    }


def write_data_js(snapshot: dict, path: Path) -> None:
    path.write_text("window.ASSAY_SNAPSHOT = "
                    + json.dumps(snapshot, ensure_ascii=False) + ";\n",
                    encoding="utf-8")
