# Contributing

assay is small on purpose. The whole point is that a person can read the desk
end to end, so contributions that keep it readable are worth more than
contributions that add features.

## Ground rules

- Paper by default stays. No pull request adds a wallet, a private key, or a
  --live flag. The executor is deliberately not in this repo.
- Every signal that moves the estimate must be capped and printed on the card.
  No hidden state, no unfalsifiable confidence score.
- New behaviour comes with a test in tests.py. The suite runs with no network
  and no dependencies; keep it that way.

## How to propose a change

1. Fork the repo and branch from main.
2. Keep the change small and focused. One idea per pull request.
3. Run python tests.py locally; make sure it is green.
4. Open a pull request that says what changed and why, in plain words.

## Good first changes

- A new source adapter under assay/sources/, matching the Market shape.
- A --top N flag on scan to trim the output.
- Better docs: a clearer explanation is a real contribution.

## Not looking for

- Anything that makes the desk fire more trades by default.
- Heavy dependencies. Zero runtime deps is a feature, not an accident.
- Returns claims. The honest answer is a settle report with a spread.

Questions or a wrong number you spotted? Open an issue, or reach out on X:
@bl888m_eth.
