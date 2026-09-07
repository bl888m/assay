# Roadmap

Where assay is and where it goes next. Paper by default is not a phase, it
is the ground rule: every item below keeps the read-only, paper-first stance
unless a step is explicitly opt-in.

## Shipped (v0.2)

- Six-agent desk: Rigo, Holt, Ilsa, Kett, Bram, Tess, each a small module.
- Transparent estimate: favorite-longshot recalibration plus a capped
  momentum tilt, printed on every card.
- Quarter-Kelly sizing with a hard per-market cap.
- Risk desk that refuses on edge, liquidity, time, position, exposure and
  correlation, and names the binding rule.
- Paper book with a settle report against ground truth.
- board: a local HTML/CSS/JS desk view of a run.
- Sources: offline simulator and the public Polymarket Gamma API.
- Optional LLM research agent (Holt), off by default, capped and labelled.
- 22 checks, no network, running in CI.

## Next

- Live Robinhood Chain adapter: read open event contracts directly, the
  same pipeline, still read-only.
- A Kalshi source, so the desk spans the three venues a retail account can
  reach.
- Historical backtest: replay resolved markets over a date range and score
  the strategy against real outcomes, not just the simulator.
- Alerts: a webhook or Telegram ping when a fire clears a high-edge
  threshold, best-effort and off by default.

## Later

- Calibration tracking: log Ilsa's estimate against every resolution and
  report a Brier score, so the estimate is graded, not trusted.
- Correlation-aware sizing beyond the crude per-category cap.
- More research signals for Holt: news and order-flow, each capped and shown
  by name.
- An executor, behind an explicit opt-in, that reads the same proposals and
  signs orders. Paper stays the default; live is a door you open on purpose.

## Non-goals

- Auto-trading real money by default.
- A black-box model whose number you cannot trace to a line.
- Any claim of returns that is not a settle report with its spread shown.
