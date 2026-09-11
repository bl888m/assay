# Security

assay is read-only research software. This document is about what it can and
cannot touch, and how to report a problem.

## What assay can do

- Read public market data (the offline simulator, the Polymarket Gamma API,
  or a Robinhood event-contracts endpoint you configure).
- Read the Robinhood Chain public RPC for chain height, gas and chain id.
- Score markets, size hypothetical bets, and record them in a paper book.

## What assay cannot do

- It holds no private key and imports no wallet library.
- It signs nothing and broadcasts nothing.
- It has no `--live` flag and no order executor. Going live is code you would
  write yourself; it is deliberately not in this repository.

Paper is the default and the only mode shipped here. If a number is not from
a public read or the local simulator, it does not exist in assay.

## What leaves your machine

- With the default `sim` source: nothing, it runs offline.
- With `--source polymarket` or `--source robinhood`: read-only HTTPS to that
  public endpoint.
- With `--research llm`: the market question and price are sent to the
  Anthropic API under your own key. Research is off by default.

No telemetry, no analytics, no phone-home.

## Keys and secrets

- The only secret assay ever reads is `ANTHROPIC_API_KEY`, and only when you
  pass `--research llm`.
- Keep keys in `.env` (gitignored) or your shell, never in code.
- `.env` is ignored by git in this repo; do not commit real keys.

## The $ASSAY token

The token contract is `0x96d2b15b35f43e0113a362b6d522a27a6a9d2138`. assay the
software does not read, hold, or trade it, and does not need it to run. Treat
anything token-related as separate from this codebase, and verify the address
from the repository or the site before interacting with it.

## Reporting

Found a problem, a wrong number, or a claim the code does not back up? Open an
issue on GitHub, or reach out on X: @bl888m_eth. There is no bug bounty; this
is a research toy, and honesty reports are as welcome as security ones.
