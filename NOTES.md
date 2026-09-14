# Notes

A working log for assay. Rough by design, this is where decisions and
open questions live before they make it into the docs.

## Design decisions

- The estimate stays two lines by default (recalibration + momentum). Every
  time it was tempting to add a third signal, the answer was: only if it is
  capped and printed on the card. Holt is that, behind a flag.
- Quarter-Kelly, not full. Full Kelly assumes the estimate is exact; it never
  is. The haircut is the difference between a desk and a casino.
- Risk names the single binding rule on every PASS. A log that just says "no"
  is useless; a log that says "liquidity $1,871 < $5,000" is a decision.
- Paper by default, with no --live flag at all. Not a setting, an absence.
  The executor is the one piece a reader should have to write themselves.

## Open questions

- Calibration tracking: log Ilsa's estimate against every resolution and
  report a Brier score. The desk should be graded, not trusted.
- A real historical backtest over resolved markets, so the scorecard stops
  being only a simulator result.
- Correlation beyond the crude per-category cap.

## Things I keep reminding myself

- The honest answer to "does it work" is a settle report with a wide spread,
  not a screenshot of a line going up.
- Most of what the desk does is refuse. If a change makes it fire more, it is
  probably wrong.
- $ASSAY the token is separate from the code. The code never needs it.
