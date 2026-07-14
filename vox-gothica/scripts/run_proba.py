#!/usr/bin/env python3
"""Cross-platform sacred probations — used by Makefile and CI."""
from __future__ import annotations

import subprocess
import sys


def run(argv: list[str]) -> None:
    subprocess.run([sys.executable, *argv], check=True)


def main() -> int:
    run(["-m", "gothica", "proba", "--dir", "demo/probationes"])
    run(["-m", "gothica", "proba", "--dir", "probationes/conformitas"])
    run(["-m", "gothica", "invoco", "exempla/salutatio.vg", "--silens"])
    run(["-m", "gothica", "invoco", "exempla/litania_numerorum.vg", "--silens"])
    run(["-m", "gothica", "invoco", "exempla/census_servitorum.vg", "--silens"])
    run(["-m", "gothica", "scribe-solum", "exempla/fabrica_interretialis.vg", "--silens"])
    print("++ omnia sancta ++")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
