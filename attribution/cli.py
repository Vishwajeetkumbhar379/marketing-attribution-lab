"""attribution data/journeys.csv  →  comparison table, chart and budget insight."""
from __future__ import annotations

import argparse
from pathlib import Path

from .models import compare, load

COLORS = ["#B4B2C8", "#EF9F27", "#7F77DD"]


def svg_chart(table: dict[str, dict[str, float]], channels: list[str]) -> str:
    """Grouped horizontal bars: for each channel, share of conversions under each model."""
    models = [m for m in ("Last touch", "Linear", "Markov (data-driven)") if m in table]
    row_h, bar_h, left, width = 22 * len(models) + 18, 18, 170, 820
    h = row_h * len(channels) + 60
    mx = max(v for m in table.values() for v in m.values()) or 1
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" font-family="Inter,Arial,sans-serif" font-size="12">',
           f'<rect width="{width}" height="{h}" fill="#ffffff"/>']
    for i, m in enumerate(models):
        x = left + i * 150
        out.append(f'<rect x="{x}" y="10" width="10" height="10" fill="{COLORS[i]}"/><text x="{x + 14}" y="19" fill="#333">{m}</text>')
    for r, ch in enumerate(channels):
        y0 = 40 + r * row_h
        out.append(f'<text x="{left - 10}" y="{y0 + row_h / 2}" text-anchor="end" fill="#111" font-weight="600">{ch}</text>')
        for i, m in enumerate(models):
            v = table[m].get(ch, 0)
            w = (width - left - 60) * v / mx
            y = y0 + i * 22
            out.append(f'<rect x="{left}" y="{y}" width="{w:.1f}" height="{bar_h}" rx="3" fill="{COLORS[i]}"/>')
            out.append(f'<text x="{left + w + 5:.1f}" y="{y + 13}" fill="#555">{v:.0f}</text>')
    out.append("</svg>")
    return "".join(out)


def report(table: dict[str, dict[str, float]], conversions: int) -> str:
    channels = sorted({c for m in table.values() for c in m}, key=lambda c: -table["Markov (data-driven)"].get(c, 0))
    L = ["# Attribution comparison", "", f"{conversions:,} conversions credited across {len(channels)} channels by six models.", "",
         "![Attribution by model](attribution.svg)", "",
         "| Channel | " + " | ".join(table) + " |", "|---|" + "---:|" * len(table)]
    for ch in channels:
        L.append(f"| {ch} | " + " | ".join(f"{table[m].get(ch, 0):.0f}" for m in table) + " |")
    lt, mk = table["Last touch"], table["Markov (data-driven)"]
    gaps = sorted(channels, key=lambda c: mk.get(c, 0) - lt.get(c, 0))
    over = gaps[0]
    L += ["", "## What it means for budget", ""]
    for under in gaps[-2:][::-1]:
        L.append(f"- **{under}** gets {mk.get(under, 0):.0f} conversions under the data-driven model but only {lt.get(under, 0):.0f} under last touch. "
                 f"It opens and nurtures journeys that other channels close. Cutting it on last-touch numbers would hurt total sales.")
    L += [
          f"- **{over}** gets {lt.get(over, 0):.0f} under last touch but {mk.get(over, 0):.0f} under the data-driven model. "
          f"It mostly captures demand other channels created, so scaling it alone will hit diminishing returns.",
          "", "<sub>Markov model: first-order chain, credit by removal effect. Fictional data from attribution/sample.py.</sub>"]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="attribution")
    ap.add_argument("csv", type=Path)
    ap.add_argument("--out", type=Path, default=Path("reports"))
    a = ap.parse_args(argv)
    js = load(a.csv)
    table = compare(js)
    a.out.mkdir(parents=True, exist_ok=True)
    channels = sorted({c for m in table.values() for c in m}, key=lambda c: -table["Markov (data-driven)"].get(c, 0))
    (a.out / "attribution.svg").write_text(svg_chart(table, channels), encoding="utf-8")
    md = report(table, sum(j.converted for j in js))
    (a.out / "attribution.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
