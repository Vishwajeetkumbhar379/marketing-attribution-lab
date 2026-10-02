"""Multi-touch attribution: five rule-based models plus a data-driven Markov chain model.

A journey is the ordered list of channels a user touched, whether they converted,
and the revenue. Each model splits the credit for every conversion across channels.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Journey:
    path: list[str]
    converted: bool
    revenue: float = 0.0


def load(path: Path) -> list[Journey]:
    """CSV columns: user_id, path (channels joined by ' > '), converted (0/1), revenue."""
    with open(path, newline="", encoding="utf-8") as f:
        return [Journey([c.strip() for c in r["path"].split(">") if c.strip()], r["converted"] in ("1", "true", "True"), float(r.get("revenue") or 0))
                for r in csv.DictReader(f)]


def _split(journeys: list[Journey], weights) -> dict[str, float]:
    credit: dict[str, float] = defaultdict(float)
    for j in journeys:
        if not j.converted or not j.path:
            continue
        w = weights(len(j.path))
        for ch, x in zip(j.path, w):
            if x:
                credit[ch] += x
    return dict(credit)


def last_touch(js):
    return _split(js, lambda n: [0] * (n - 1) + [1])


def first_touch(js):
    return _split(js, lambda n: [1] + [0] * (n - 1))


def linear(js):
    return _split(js, lambda n: [1 / n] * n)


def time_decay(js, half_life_steps: float = 2.0):
    def w(n):
        raw = [0.5 ** ((n - 1 - i) / half_life_steps) for i in range(n)]
        s = sum(raw)
        return [x / s for x in raw]
    return _split(js, w)


def position_based(js, ends: float = 0.4):
    def w(n):
        if n == 1:
            return [1.0]
        if n == 2:
            return [0.5, 0.5]
        mid = (1 - 2 * ends) / (n - 2)
        return [ends] + [mid] * (n - 2) + [ends]
    return _split(js, w)


def markov(js: list[Journey]) -> dict[str, float]:
    """Data-driven attribution via the removal effect of a first-order Markov chain.

    Build transition probabilities between states (start, channels, conversion, null).
    A channel's removal effect is how much the overall conversion probability drops when
    that channel is removed (its traffic goes to null). Credit is shared in proportion.
    """
    trans: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for j in js:
        states = ["(start)"] + j.path + ["(conversion)" if j.converted else "(null)"]
        for a, b in zip(states, states[1:]):
            trans[a][b] += 1
    probs = {a: {b: n / sum(row.values()) for b, n in row.items()} for a, row in trans.items()}
    channels = sorted({c for j in js for c in j.path})

    def p_convert(removed: str | None) -> float:
        # Solve absorption probabilities by value iteration (graphs are small).
        v = {s: 0.0 for s in list(probs) + ["(conversion)", "(null)"]}
        v["(conversion)"] = 1.0
        for _ in range(500):
            delta = 0.0
            for s, row in probs.items():
                if s == removed:
                    continue
                new = sum(p * (0.0 if b == removed else v.get(b, 0.0)) for b, p in row.items())
                delta = max(delta, abs(new - v[s]))
                v[s] = new
            if delta < 1e-12:
                break
        return v["(start)"]

    base = p_convert(None)
    if base == 0:
        return {}
    effects = {c: max(0.0, (base - p_convert(c)) / base) for c in channels}
    total_eff = sum(effects.values()) or 1.0
    conversions = sum(1 for j in js if j.converted)
    return {c: conversions * e / total_eff for c, e in effects.items()}


MODELS = {
    "Last touch": last_touch,
    "First touch": first_touch,
    "Linear": linear,
    "Time decay": time_decay,
    "Position based": position_based,
    "Markov (data-driven)": markov,
}


def compare(js: list[Journey]) -> dict[str, dict[str, float]]:
    return {name: fn(js) for name, fn in MODELS.items()}
