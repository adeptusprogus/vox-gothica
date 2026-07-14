#!/usr/bin/env python3
"""Generate docs/transectus-divider.svg — animated segment divider for README and Codex."""
from __future__ import annotations

import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "transectus-divider.svg"

W, H = 920, 34
CHAR_STEP = 13
GLYPHS = (
    "FIATINVOCOOMNISSIAH⚙01001XIIIMCLD"
    "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
    "RITUSSCHEMAFABRICACANTICUMGOTHICA"
)
HERESY = ("☠", "⨂", "†", "✠", "HER", "CHAOS", "NIHIL")


def glyph_tspan(x: int, ch: str, rng: random.Random) -> str:
    if ch in HERESY or (rng.random() < 0.04 and ch in "☠⨂†"):
        fill = "#ff3b1f"
        opacity = round(rng.uniform(0.75, 1.0), 2)
    elif rng.random() < 0.12:
        fill = "#a8ffbe"
        opacity = 1.0
    elif rng.random() < 0.28:
        fill = "#4dff7c"
        opacity = 0.9
    else:
        fill = "#2a8f4a"
        opacity = round(rng.uniform(0.3, 0.7), 2)
    esc = ch.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<tspan x="{x}" y="22" fill="{fill}" opacity="{opacity}">{esc}</tspan>'


def main() -> None:
    rng = random.Random(77)
    count = (W * 2) // CHAR_STEP + 12
    tspans = []
    for i in range(count):
        x = 4 + i * CHAR_STEP
        ch = rng.choice(HERESY) if rng.random() < 0.018 else rng.choice(GLYPHS)
        tspans.append(glyph_tspan(x, ch, rng))

    drift_to = -(count * CHAR_STEP // 2 + W // 4)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"
  aria-label="Transectus — phosphor segment divider">
  <defs>
    <style>
    @keyframes drift {{
      from {{ transform: translateX(0); }}
      to   {{ transform: translateX({drift_to}px); }}
    }}
    .stream {{ font-family:'Courier New',Courier,monospace; font-size:15px;
               animation:drift 16s linear infinite; }}
    </style>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#010502" stop-opacity="1"/>
      <stop offset="10%"  stop-color="#010502" stop-opacity="0"/>
      <stop offset="90%"  stop-color="#010502" stop-opacity="0"/>
      <stop offset="100%" stop-color="#010502" stop-opacity="1"/>
    </linearGradient>
    <clipPath id="clip"><rect width="{W}" height="{H}"/></clipPath>
  </defs>
  <rect width="{W}" height="{H}" fill="#010502"/>
  <g clip-path="url(#clip)">
    <text class="stream">{"".join(tspans)}</text>
  </g>
  <line x1="0" y1="1.5" x2="{W}" y2="1.5" stroke="#4dff7c" stroke-opacity="0.45" stroke-width="1"/>
  <line x1="0" y1="{H-1.5}" x2="{W}" y2="{H-1.5}" stroke="#4dff7c" stroke-opacity="0.45" stroke-width="1"/>
  <rect width="{W}" height="{H}" fill="url(#fade)" pointer-events="none"/>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"generated: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
