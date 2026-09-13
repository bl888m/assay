# FAQ

Short answers to the questions people actually ask about assay.

**Is this a buy signal or a copy-trading bot?**
No, the opposite. assay is a research desk that mostly refuses. It estimates a
probability, sizes a hypothetical bet at quarter-Kelly, and books it on paper.
There is no wallet in the repo and no `--live` flag, because the executor is
deliberately not shipped.

**Does it trade real money?**
No. Paper by default, and paper only. Every source is read-only. Going live is
code you would write yourself.

**Is the estimate an AI black box?**
No. Two lines by default: a logit recalibration of the crowd price and a capped
momentum tilt, both printed on every card with their signed contribution. The
optional research agent (Holt) is the only place a model enters, and its vote
is capped and labelled.

**Does it beat the market?**
Unknown, and the honest answer is that a dozen thin-edge bets is high variance,
so a third of simulated runs lose even when the edge is real. That is why the
scorecard shows a spread instead of one flattering number.

**Why does it refuse so many trades?**
That is the whole design. Bram, the risk agent, declines on edge, liquidity,
time, position size, exposure and correlation, and names the rule that stopped
each one. Most of what the desk does is say no.

**What is the edge, exactly?**
The favorite-longshot bias: across a century of betting and prediction markets,
longshots are overbet and favorites underbet. assay corrects for it with one
slope you can change (`k = 1.18` by default).

**Can I point it at Robinhood or Polymarket?**
Yes. `--source polymarket` reads the public Gamma API; `--source robinhood`
maps Robinhood event contracts once you set `RH_API_BASE`. Both only read.

**What is $ASSAY?**
A token, live on Pons. The software does not read, hold, or trade it and does
not need it to run. Treat anything token-related as separate from the code.

**Where do I start?**
`python examples/quickstart.py`, then read `docs/STRATEGY.md` and
`docs/SAFETY.md`. Machine-readable output: `assay scan --json`.
