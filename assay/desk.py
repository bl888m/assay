"""The desk. Six agents, each a real module, each with one job.

This is the "team of AI agents" the fund story is built on. The honesty
clause matters and stays: no agent hands another a paragraph of English to
re-read. Each one is a handful of lines with a single job, tested on its
own in tests.py. The names give the pipeline a face for the story; the code
underneath is deliberately dull so it can be trusted.

Only one agent, Holt, can call a model at all, and only when you turn it
on. The rest are arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Agent:
    handle: str
    role: str
    module: str
    job: str


DESK = [
    Agent("Rigo", "Scout",     "sources/*",   "pulls the universe of open markets"),
    Agent("Holt", "Research",  "research.py", "adds context to a market; the only one that can call a model"),
    Agent("Ilsa", "Analyst",   "model.py",    "estimates the true probability from the crowd price"),
    Agent("Kett", "Trader",    "edge.py",     "picks the side and sizes it by Kelly"),
    Agent("Bram", "Risk",      "risk.py",     "refuses most of it, and names the rule"),
    Agent("Tess", "Portfolio", "book.py",     "owns the paper book and settles it"),
]

BY_ROLE = {a.role: a for a in DESK}
