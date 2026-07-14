#!/usr/bin/env python3
"""Generate docs/readme-crypta.svg — animated phosphor banner for README."""
from __future__ import annotations

import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "readme-crypta.svg"

W, H = 920, 168

SACRED_STREAMS = [
    "FIAT INVOCO RITUS SCHEMA NIHIL FINIS AVE",
    "CANTICUM FABRICA LITANIA PURGA LUSTRO",
    "OMNISSIAH MACHINA SPIRITUS COGITATOR",
    "DECLARO SANCTUM VOCIFERO EXSTRUATUR",
    "XIII XLII MCMXIV DCCCLXXXVIII",
    "01001111 01001101 01001110 01001001",
    "⚙ ⚙ ⚙ ⚙ ⚙ ⚙ ⚙ ⚙ ⚙ ⚙ ⚙ ⚙",
    "ADFERRO EXPOLLO RENOVUM OFFERO PROBA",
    "SEDES FOEDUS SCRUTOR POSTULO ARCANUM",
    "NUMQUAM FINIS LITANIA CANTICLE VOX",
    "GOTHICA ADEPTUS MECHANICUS CULTUS",
    "PHOSPHOR CATHODE NOOSPHERE LIBRARIUM",
    "INVOCO UT EX MODULUS VERSIO MANDATA",
    "TYPUS VALOR SENTENTIA EXPRESSIO RITE",
]

HERESY_FLASHES = [
    ("☠", 120, 48, 22),
    ("HERETICUS", 380, 72, 16),
    ("CHAOS", 640, 55, 18),
    ("divisio_nihili", 220, 95, 11),
    ("circulus_impius", 520, 88, 11),
    ("⨂", 760, 42, 26),
    ("PROFANUM", 480, 118, 14),
    ("NIHILUM", 300, 130, 13),
    ("H̸E̸R̸E̸S̸Y̸", 680, 125, 15),
]


def column(x: int, text: str, dur: float, delay: float, opacity: float, size: int) -> str:
    # Repeat text for seamless loop
    stream = (text + " · ") * 4
    y_end = H + 80
    return f"""  <text x="{x}" y="0" fill="#4dff7c" fill-opacity="{opacity:.2f}"
        font-family="'Courier New',Courier,monospace" font-size="{size}" letter-spacing="1">
    <tspan>{stream}</tspan>
    <animateTransform attributeName="transform" type="translate"
      values="0 -{y_end}; 0 {y_end}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>
  </text>"""


def heresy_flash(text: str, x: int, y: int, size: int, begin: float) -> str:
    return f"""  <text x="{x}" y="{y}" text-anchor="middle" fill="#ff3b1f"
        font-family="'Courier New',Courier,monospace" font-size="{size}" font-weight="700"
        filter="url(#heresy-glow)" opacity="0">
    {text}
    <animate attributeName="opacity" values="0;0;0.95;0.95;0;0" keyTimes="0;0.82;0.86;0.9;0.94;1"
      dur="9s" begin="{begin}s" repeatCount="indefinite"/>
    <animate attributeName="fill" values="#ff3b1f;#ffb000;#ff3b1f;#ff3b1f"
      keyTimes="0;0.5;0.7;1" dur="9s" begin="{begin}s" repeatCount="indefinite"/>
  </text>"""


def main() -> None:
    random.seed(42)
    cols = []
    for i in range(18):
        x = 12 + i * 50
        text = SACRED_STREAMS[i % len(SACRED_STREAMS)]
        dur = round(random.uniform(6.5, 11.5), 2)
        delay = round(random.uniform(0, 5), 2)
        opacity = round(random.uniform(0.18, 0.55), 2)
        size = random.choice([9, 10, 11, 12])
        cols.append(column(x, text, dur, delay, opacity, size))

    flashes = [
        heresy_flash(t, x, y, sz, round(random.uniform(0, 7), 1))
        for t, x, y, sz in HERESY_FLASHES
    ]

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img"
  aria-label="Vox Gothica — phosphor crypt feed with heretical glitches">
  <defs>
    <linearGradient id="void" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#020805"/>
      <stop offset="100%" stop-color="#010502"/>
    </linearGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="#4dff7c" fill-opacity="0.03"/>
    </pattern>
    <filter id="phos-glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="heresy-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <radialGradient id="center-glow" cx="50%" cy="50%" r="45%">
      <stop offset="0%" stop-color="#0a1a0f" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#010502" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="6"/></clipPath>
  </defs>

  <rect width="{W}" height="{H}" rx="6" fill="url(#void)"/>
  <rect width="{W}" height="{H}" rx="6" fill="url(#scan)"/>
  <rect width="{W}" height="{H}" rx="6" fill="none" stroke="#14512a" stroke-width="1.5"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="5" fill="none" stroke="#2a8f4a" stroke-width="0.5" stroke-opacity="0.4"/>

  <g clip-path="url(#frame)" opacity="0.92">
{chr(10).join(cols)}
  </g>

  <rect x="0" y="0" width="{W}" height="{H}" fill="url(#center-glow)" pointer-events="none"/>

  <g filter="url(#phos-glow)">
    <text x="{W//2}" y="62" text-anchor="middle"
      font-family="Georgia,'Times New Roman',serif" font-size="34" font-weight="700"
      fill="#a8ffbe" letter-spacing="6">VOX GOTHICA</text>
    <text x="{W//2}" y="88" text-anchor="middle"
      font-family="'Courier New',Courier,monospace" font-size="11"
      fill="#ffb000" letter-spacing="4">HIGH GOTHIC PROGRAMMING LANGUAGE</text>
    <text x="{W//2}" y="108" text-anchor="middle"
      font-family="'Courier New',Courier,monospace" font-size="9"
      fill="#2a8f4a" letter-spacing="2">CANTICLES · FABRICAE · TERRAFORM · ADEPTUS MECHANICUS</text>
  </g>

  <g>
    <circle cx="72" cy="{H//2}" r="22" fill="none" stroke="#c9a227" stroke-width="1.5" opacity="0.7"/>
    <circle cx="72" cy="{H//2}" r="8" fill="none" stroke="#4dff7c" stroke-width="1.2" opacity="0.8"/>
    <path d="M72 {H//2-14}v-5M72 {H//2+14}v5M50 {H//2}h-5M94 {H//2}h5"
      stroke="#c9a227" stroke-width="1.2" stroke-linecap="round" opacity="0.6"/>
    <path d="M72 {H//2-6}l-2.5 5h5l-2.5 5" fill="none" stroke="#4dff7c" stroke-width="1.4" stroke-linejoin="round"/>
    <circle cx="{W-72}" cy="{H//2}" r="22" fill="none" stroke="#c9a227" stroke-width="1.5" opacity="0.7"/>
    <circle cx="{W-72}" cy="{H//2}" r="8" fill="none" stroke="#4dff7c" stroke-width="1.2" opacity="0.8"/>
    <path d="M{W-72} {H//2-14}v-5M{W-72} {H//2+14}v5M{W-94} {H//2}h-5M{W-50} {H//2}h5"
      stroke="#c9a227" stroke-width="1.2" stroke-linecap="round" opacity="0.6"/>
    <path d="M{W-72} {H//2-6}l-2.5 5h5l-2.5 5" fill="none" stroke="#4dff7c" stroke-width="1.4" stroke-linejoin="round"/>
  </g>

  <g>
{chr(10).join(flashes)}
  </g>

  <text x="{W//2}" y="{H-14}" text-anchor="middle"
    font-family="'Courier New',Courier,monospace" font-size="8" fill="#14512a" letter-spacing="3">
    FROM THE WEAKNESS OF THE FLESH — THE MACHINE DELIVERS US
  </text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"generated: {OUT.relative_to(ROOT)}")
    divider = ROOT / ".github" / "scripts" / "gen-transectus-divider.py"
    subprocess.run([sys.executable, str(divider)], check=True)


if __name__ == "__main__":
    main()
