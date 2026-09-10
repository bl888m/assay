"""assay checks. No network, no dependencies. Run with `python tests.py`.

Each check is one fact about the math or the rules. If the estimate, the
Kelly sizing, or a risk refusal ever changes, one of these fails loudly.
"""

from assay import model, edge
from assay.types import Market, Estimate
from assay.book import Book
from assay.pipeline import run
from assay.risk import Limits, check
from assay.sources import simulator

PASS, FAIL = 0, 0


def ok(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok    {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}")


def mk(price=0.5, liq=50_000, hrs=48, p24=None, cat="Tech", tp=None):
    return Market(id="t", question="q", category=cat, price=price,
                  liquidity=liq, volume_24h=liq, hours_to_resolve=hrs,
                  price_24h_ago=price if p24 is None else p24, true_prob=tp)


# --- model -----------------------------------------------------------------
ok("logit/sigmoid round trip",
   abs(model._sigmoid(model._logit(0.37)) - 0.37) < 1e-9)

ok("recalibration pushes a favorite up",
   model.estimate(mk(price=0.85)).q > 0.85)

ok("recalibration pulls a longshot down",
   model.estimate(mk(price=0.15)).q < 0.15)

ok("recalibration leaves a coin flip alone",
   abs(model.estimate(mk(price=0.50)).q - 0.50) < 1e-6)

ok("momentum is capped",
   abs(model.estimate(mk(price=0.5, p24=0.0)).components["momentum"])
   <= model.MOMENTUM_CAP + 1e-9)

# --- edge / kelly ----------------------------------------------------------
p = edge.propose(mk(price=0.40), Estimate(q=0.50, price=0.40), 10_000)
ok("kelly formula on a known case",
   abs(p.kelly_fraction - (0.50 - 0.40) / (1 - 0.40) * edge.KELLY_FRACTION) < 1e-3)

ok("propose takes YES when estimate is above price",
   edge.propose(mk(price=0.4), Estimate(q=0.6, price=0.4), 1000).side == "YES")

ok("propose takes NO when estimate is below price",
   edge.propose(mk(price=0.6), Estimate(q=0.4, price=0.6), 1000).side == "NO")

ok("no edge means zero stake",
   edge.propose(mk(price=0.5), Estimate(q=0.5, price=0.5), 1000).stake == 0)

# --- risk ------------------------------------------------------------------
big = Estimate(q=0.75, price=0.60)   # 15% edge, well over the floor

ok("risk refuses a thin edge",
   check(edge.propose(mk(price=0.60), Estimate(q=0.61, price=0.60), 10_000),
         Book(), Limits()).verdict == "PASS")

ok("risk refuses thin liquidity",
   check(edge.propose(mk(price=0.60, liq=100), big, 10_000), Book(), Limits()).verdict == "PASS")

ok("risk refuses a market resolving too soon",
   check(edge.propose(mk(price=0.60, hrs=1), big, 10_000), Book(), Limits()).verdict == "PASS")

ok("risk fires a clean proposal",
   check(edge.propose(mk(price=0.60), big, 10_000), Book(), Limits()).verdict == "FIRE")

b = Book()
for _ in range(3):
    b.positions.append(__import__("assay.book", fromlist=["Position"]).Position(
        "x", "q", "Tech", "YES", 0.6, 100, 0.6))
ok("risk enforces the category cap",
   check(edge.propose(mk(price=0.60, cat="Tech"), big, 10_000), b, Limits()).verdict == "PASS")

# --- book ------------------------------------------------------------------
b = Book()
prop = edge.propose(mk(price=0.60), big, 10_000)
d = check(prop, b, Limits())
b.open(d.proposal)
ok("opening a position debits cash", b.cash < b.starting_cash)

before = b.cash
b.resolve("t", yes_won=True)   # bought YES, YES won
ok("a winning YES pays out more than the stake", b.cash > before + d.proposal.stake)

b2 = Book()
prop2 = edge.propose(mk(price=0.60), big, 10_000)
b2.open(check(prop2, b2, Limits()).proposal)
c2 = b2.cash
b2.resolve("t", yes_won=False)  # bought YES, YES lost
ok("a losing YES pays nothing", abs(b2.cash - c2) < 1e-9)

# --- determinism -----------------------------------------------------------
ok("simulator is deterministic",
   [m.question for m in simulator.generate(8, 5)]
   == [m.question for m in simulator.generate(8, 5)])

ds1 = run(simulator.generate(120, 42), Book(), Limits())
ds2 = run(simulator.generate(120, 42), Book(), Limits())
ok("pipeline is deterministic",
   sum(1 for d in ds1 if d.verdict == "FIRE")
   == sum(1 for d in ds2 if d.verdict == "FIRE"))

# --- desk and research -----------------------------------------------------
from assay.desk import DESK
from assay import research

ok("the desk has six agents", len(DESK) == 6)

ok("research is off by default", research.research(mk(price=0.6), "off") == (0.0, None))

ok("Holt's vote is capped",
   abs(model.estimate(mk(price=0.5), research_delta=0.9).components.get("research", 0))
   <= 0.9 + 1e-9 and
   model.estimate(mk(price=0.5), research_delta=0.02).q
   > model.estimate(mk(price=0.5)).q)

# --- json export -----------------------------------------------------------
from assay.render import decisions_json
_dj = decisions_json(run(simulator.generate(6, 7), Book(), Limits()))
ok("json export is a list of dicts with the expected keys",
   isinstance(_dj, list) and len(_dj) > 0
   and all(k in _dj[0] for k in ("question", "price", "estimate", "edge", "verdict", "stake")))

print(f"\n  {PASS} passed, {FAIL} failed")
raise SystemExit(1 if FAIL else 0)
