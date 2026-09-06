# Safety

Read this before you wire assay to anything real.

## Paper by default, and there is no live switch

assay books trades on paper. There is no wallet, no exchange client, and no
order-signing code anywhere in this repository. There is no `--live` flag to
find, because the executor that would place an order is deliberately not
written here. Every source is read-only: it pulls markets and never sends.

Going live is a project you take on yourself: write an executor that reads
the same `Proposal` objects the desk produces and signs orders against your
venue. If you do that, everything below becomes your responsibility.

## What leaves your machine

With the default source (`sim`), nothing. It runs offline.

With `--source polymarket`, read-only HTTPS to Polymarket's public Gamma
API. With `--source robinhood`, read-only HTTPS to whatever endpoint you set
in `RH_API_BASE`. With `--research llm`, the market's question and price are
sent to the Anthropic API under your key. Turn research off and that path is
never touched.

## What assay is not

It is not financial advice, and it is not a claim that a script beats the
market. The reported numbers are a simulated backtest against a simulator
that has the target bias built in. Real markets may not, and a thin edge
over a handful of bets is high variance regardless. Keep it on paper, watch
it for a long time, and trust the refusals more than the fires.

## If you later add execution

Port the walls a real desk uses before the first live order: a confirmation
that prints your address and limits and waits, a per-order size cap, a total
exposure cap, and a session budget after which nothing fires whatever the
score. None of that is in this repo. Its absence is the safety feature.
