# Changelog

## v0.3.0
- `--json` output for `scan` and `paper`: machine-readable rows and a full
  paper snapshot, for wiring the desk into your own pipeline.
- `$ASSAY` is live on Pons; the contract address is in the README.
- 23 offline tests in CI, still zero runtime dependencies.

## v0.2.0
- The six-agent desk: Rigo, Holt, Ilsa, Kett, Bram, Tess.
- `board`: a local HTML/CSS/JS desk view of a run.
- Sources: offline simulator, the public Polymarket Gamma API, and a
  Robinhood event-contracts adapter.
- Optional LLM research agent (Holt), off by default and capped.
- ASCII wordmark in the terminal output, CI on every push.

## v0.1.0
- Initial desk: favorite-longshot recalibration, quarter-Kelly sizing, a risk
  desk that refuses most trades, a paper book, and a settle report.
