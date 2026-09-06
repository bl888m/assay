"""Holt, the research agent. Off unless you ask for it.

Every other agent is arithmetic you can check by hand. Holt is the one
place a language model enters the loop, and it earns its keep only if it
stays honest about three things:

1. It is optional. With no `--research llm` and no key, Holt returns
   nothing and the estimate is exactly the transparent model.
2. Its vote is bounded. Whatever the model says, its effect on the
   probability is capped (`RESEARCH_CAP`), the same way momentum is. It
   can tilt a call, never dictate one.
3. It shows its work. Holt returns a one-line reason that prints on the
   card next to its number, so a human sees what moved and why.

The model is asked for a single probability and a short reason, nothing
else. No tools, no browsing, no chain of agents talking to each other.
It reads the market text and returns a number. That is the whole agent.
"""

from __future__ import annotations

import json
import os
from urllib.request import urlopen, Request

from .types import Market

RESEARCH_CAP = 0.05          # max points of probability Holt can move an estimate
_API = "https://api.anthropic.com/v1/messages"


def enabled(mode: str) -> bool:
    return mode == "llm" and bool(os.environ.get("ANTHROPIC_API_KEY"))


def research(m: Market, mode: str = "off") -> tuple[float, str | None]:
    """Return (signed delta to apply to YES probability, one-line reason).

    (0.0, None) when Holt is off or the call fails. Failure is quiet on
    purpose: a research outage must never stop the desk, it just drops
    back to the arithmetic estimate.
    """
    if not enabled(mode):
        return 0.0, None

    key = os.environ["ANTHROPIC_API_KEY"]
    model = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

    prompt = (
        "You are a research analyst on a prediction-market desk. "
        "Given one market, estimate the probability the YES side resolves true. "
        "Reply with strict JSON only: "
        '{"p": <0..1>, "why": "<=12 words"}.\n\n'
        f"Market: {m.question}\n"
        f"Category: {m.category}\n"
        f"Current crowd price (implied YES prob): {m.price:.2f}\n"
        f"Hours to resolution: {m.hours_to_resolve:.0f}"
    )

    body = json.dumps({
        "model": model,
        "max_tokens": 128,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = Request(_API, data=body, headers={
        "content-type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
    })

    try:
        with urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode())
        text = "".join(b.get("text", "") for b in data.get("content", []))
        parsed = json.loads(text.strip().strip("`").removeprefix("json").strip())
        p = float(parsed["p"])
        why = str(parsed.get("why", ""))[:60]
    except Exception:
        return 0.0, None

    # Holt votes against the crowd price, capped. It nudges, never dictates.
    delta = max(-RESEARCH_CAP, min(RESEARCH_CAP, p - m.price))
    return delta, why
