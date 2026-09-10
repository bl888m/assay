"""assay command line.

    assay desk              show the six agents and what each does
    assay scan              read markets, score them, fire nothing
    assay paper             run the pipeline into a paper book
    assay paper --settle    ... then settle every position by ground truth
    assay watch             re-scan on an interval (useful with a live source)
    assay scan --json       machine-readable rows for your own pipeline

Paper by default. Simulator by default. Reproducible by default.
Holt (the research agent) is off unless you pass --research llm.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time

from . import render
from .book import Book
from .pipeline import run
from .risk import Limits
from .sources import simulator


def _load(source: str, n: int, seed: int):
    if source == "sim":
        return simulator.generate(n=n, seed=seed)
    if source == "polymarket":
        from .sources import polymarket
        return polymarket.fetch(limit=n)
    if source == "robinhood":
        from .sources import robinhood
        return robinhood.fetch(limit=n)
    raise SystemExit(f"unknown source: {source}")


def _print_run(a, markets, book, limits):
    print(render.header(a.source, len(markets), book.bankroll(), a.research))
    decisions = run(markets, book, limits, research_mode=a.research)
    fired = 0
    for d in decisions:
        print(render.card(d))
        print()
        if d.verdict == "FIRE":
            fired += 1
    print(f"  {fired} fired, {len(decisions) - fired} passed")
    return decisions


def _settle(book: Book, markets, seed: int) -> None:
    rng = random.Random(seed + 1)
    by_id = {m.id: m for m in markets}
    for pos in list(book.positions):
        m = by_id.get(pos.market_id)
        if m is None or m.true_prob is None:
            continue
        yes_won = rng.random() < m.true_prob
        book.resolve(m.id, yes_won)


def cmd_desk(a):
    print(render.desk_roster())


def cmd_scan(a):
    markets = _load(a.source, a.n, a.seed)
    book = Book(starting_cash=a.bankroll, cash=a.bankroll)
    from . import model, edge, research
    from .risk import check
    scored = []
    for m in markets:
        delta, note = research.research(m, a.research)
        est = model.estimate(m, delta, note or "")
        scored.append((est.q - m.price, m, est))
    decisions = []
    for _, m, est in sorted(scored, key=lambda t: t[0], reverse=True):
        prop = edge.propose(m, est, book.bankroll())
        decisions.append(check(prop, book, Limits(**_limit_kwargs(a))))
    if a.json:
        print(json.dumps(render.decisions_json(decisions)))
        return
    print(render.header(a.source, len(markets), book.bankroll(), a.research))
    for d in decisions:
        print(render.card(d))
        print()


def cmd_paper(a):
    markets = _load(a.source, a.n, a.seed)
    limits = Limits(**_limit_kwargs(a))
    if a.json:
        from . import snapshot
        snap = snapshot.build(markets, limits, a.bankroll,
                              a.source, a.research == "llm", a.seed)
        print(json.dumps(snap))
        return
    book = Book(starting_cash=a.bankroll, cash=a.bankroll)
    _print_run(a, markets, book, limits)
    if a.settle:
        _settle(book, markets, a.seed)
    print()
    print(render.book_summary(book))


def cmd_board(a):
    import webbrowser
    from pathlib import Path
    from . import snapshot
    markets = _load(a.source, a.n, a.seed)
    limits = Limits(**_limit_kwargs(a))
    snap = snapshot.build(markets, limits, a.bankroll,
                          a.source, a.research == "llm", a.seed)
    board_dir = Path(__file__).resolve().parent.parent / "board"
    data = board_dir / "data.js"
    snapshot.write_data_js(snap, data)
    index = board_dir / "index.html"
    print(f"desk snapshot written. opening {index}")
    print("if it does not open, open that file in your browser.")
    try:
        webbrowser.open(index.as_uri())
    except Exception:
        pass


def cmd_watch(a):
    try:
        while True:
            markets = _load(a.source, a.n, a.seed)
            book = Book(starting_cash=a.bankroll, cash=a.bankroll)
            _print_run(a, markets, book, Limits(**_limit_kwargs(a)))
            print(f"\n  sleeping {a.interval}s ... ctrl-c to stop\n")
            time.sleep(a.interval)
    except KeyboardInterrupt:
        print("\nstopped.")


def _limit_kwargs(a) -> dict:
    out = {}
    if a.min_edge is not None:
        out["min_edge"] = a.min_edge
    if a.min_liquidity is not None:
        out["min_liquidity"] = a.min_liquidity
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="assay",
                                description="your own AI hedge-fund desk for prediction markets")
    p.add_argument("--source", default="sim",
                   choices=["sim", "polymarket", "robinhood"])
    p.add_argument("--n", type=int, default=12, help="markets to pull")
    p.add_argument("--seed", type=int, default=7, help="simulator seed")
    p.add_argument("--bankroll", type=float, default=10_000.0)
    p.add_argument("--research", default="off", choices=["off", "llm"],
                   help="turn on Holt, the LLM research agent (needs ANTHROPIC_API_KEY)")
    p.add_argument("--min-edge", type=float, default=None)
    p.add_argument("--min-liquidity", type=float, default=None)

    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("desk", help="show the six agents")
    d.set_defaults(func=cmd_desk)

    s = sub.add_parser("scan", help="score markets, fire nothing")
    s.add_argument("--json", action="store_true",
                   help="machine-readable output for your own pipeline")
    s.set_defaults(func=cmd_scan)

    pa = sub.add_parser("paper", help="run the pipeline into a paper book")
    pa.add_argument("--settle", action="store_true",
                    help="settle positions by ground truth (sim only)")
    pa.add_argument("--json", action="store_true",
                    help="machine-readable snapshot for your own pipeline")
    pa.set_defaults(func=cmd_paper)

    w = sub.add_parser("watch", help="re-scan on an interval")
    w.add_argument("--interval", type=int, default=30)
    w.set_defaults(func=cmd_watch)

    b = sub.add_parser("board", help="render the desk as a local web page")
    b.set_defaults(func=cmd_board)

    return p


def main(argv=None) -> int:
    a = build_parser().parse_args(argv)
    a.func(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
