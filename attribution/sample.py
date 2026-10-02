"""Fictional customer journeys with a realistic shape: social and creators open journeys,
search and email close them. Last-touch will over-credit search; that's the point."""
from __future__ import annotations

import csv
import random
from pathlib import Path

OPENERS = ["Instagram creators", "Meta ads", "TikTok", "SEO blog", "LinkedIn"]
MIDDLE = ["Meta retargeting", "Email", "YouTube", "SEO blog", "Instagram creators"]
CLOSERS = ["Google brand search", "Email", "Direct"]


def generate(n: int = 4000, seed: int = 11) -> list[dict]:
    rnd = random.Random(seed)
    rows = []
    for i in range(n):
        path = [rnd.choices(OPENERS, weights=[30, 25, 15, 20, 10])[0]]
        for _ in range(rnd.choice([0, 0, 1, 1, 2, 3])):
            path.append(rnd.choice(MIDDLE))
        closes = rnd.random() < 0.55
        if closes:
            path.append(rnd.choices(CLOSERS, weights=[50, 30, 20])[0])
        # creators and retargeting genuinely lift conversion in this world
        p = 0.04 + 0.06 * ("Instagram creators" in path) + 0.05 * ("Meta retargeting" in path) + 0.08 * closes
        conv = rnd.random() < p
        rows.append({"user_id": f"u{i:05d}", "path": " > ".join(path), "converted": int(conv),
                     "revenue": round(rnd.uniform(35, 95), 2) if conv else 0})
    return rows


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "journeys.csv"
    rows = generate()
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} journeys to {out}")
