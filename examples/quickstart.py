"""quickstart: run the desk in five lines and print the strongest edges.

    python examples/quickstart.py

No flags, no network. It generates a batch of markets with the simulator,
runs the six-agent pipeline, and prints the trades Bram let through, sorted
by edge. This is the smallest possible example of using assay as a library
rather than from the command line.
"""

from assay.sources import simulator
from assay.book import Book
from assay.risk import Limits
from assay.pipeline import run

markets = simulator.generate(n=14, seed=2)
book = Book()
decisions = run(markets, book, Limits())

fired = [d for d in decisions if d.verdict == "FIRE"]
fired.sort(key=lambda d: d.proposal.edge, reverse=True)

print(f"{len(fired)} fired of {len(decisions)} scored\n")
for d in fired:
    p = d.proposal
    print(f"  {p.edge:>+5.1%}  {p.side:<3}  ${p.stake:>6,.0f}  {p.market.question[:44]}")
