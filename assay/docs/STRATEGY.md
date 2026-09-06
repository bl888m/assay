# Strategy

Where every number the desk uses comes from. Nothing here is secret and
nothing here is magic. If you disagree with a rule, it is one file away.

## The edge assay bets on

The only durable edge in a prediction market is a better estimate of the
true probability than the crowd price, on markets liquid enough to bet and
slow enough to resolve. assay looks for exactly one well-documented reason
the crowd is wrong, and refuses everything else.

**Favorite-longshot bias.** Across a century of racetrack, sportsbook and
prediction-market data, longshots are overbet and favorites underbet.
Bettors pay too much for a small chance at a big payout and too little for
a near sure thing. The direction is stable and the rough size is known.

Ilsa corrects for it by stretching the crowd price in logit space by a
single slope `k`:

```
q = sigmoid( logit(price) * k )        # k = 1.18 by default
```

`k = 1` trusts the crowd exactly. Above 1 it pulls longshot prices down and
pushes favorite prices up, which is the profitable direction. Below 1 it
would fade favorites, the losing side historically. One number, and you own
it.

**Momentum.** A market that moved over the last 24h tends to keep drifting.
Ilsa nudges the estimate the way the price moved, capped at four points of
probability so it can never overrule the recalibration.

**Research (Holt, optional).** With `--research llm` and a key, a language
model reads the market and returns a probability. Its vote is capped the
same way momentum is and printed on the card with its reason. It tilts a
call, it never dictates one, and with research off the estimate is only the
two components above.

## Sizing

Kett bets the side with positive edge and sizes it by Kelly. For a binary
contract that costs `p` and pays 1, buying YES has

```
kelly f* = (q - p) / (1 - p)
```

Full Kelly assumes the estimate is exactly right and bets far too hard when
it is not. Kett bets a fixed fraction of it, quarter-Kelly by default, the
standard haircut for estimates that are only approximately calibrated.

## Why Bram refuses so much

| Rule | Default | Reason |
| ---- | ------- | ------ |
| min edge | 4% | thinner than the estimate's own noise |
| min liquidity | $5,000 | can't get filled at the quote |
| min time to resolve | 6h | too soon to be anything but a coin flip |
| max position | 5% of bankroll | one wrong estimate cannot compound |
| max exposure | 60% deployed | keep dry powder |
| max per category | 3 | crude correlation guard |

## What the numbers say

Across 500 seeded simulator runs of 120 markets each, at the default rules:
mean return +2.68%, median +3.40%, standard deviation 8.14%, 66% of runs in
profit, best +20.7%, worst -27.6%. The wide spread is the honest part: a
thin edge over a dozen bets is high variance, and a third of runs lose even
when the edge is real and known. This is a simulated measurement of whether
the strategy captures a bias baked into the simulator, not a claim about
live markets.
