#!/usr/bin/env python3
"""Cross-platform sacred probations — used by Makefile and CI."""
from __future__ import annotations

import subprocess
import sys


def run(argv: list[str]) -> None:
    subprocess.run([sys.executable, *argv], check=True)


def main() -> int:
    run(["-m", "gothica", "proba", "--dir", "demo/probationes"])
    run(["-m", "gothica", "proba", "--dir", "applicata/cogitator_arithmetica/probationes"])
    run(["-m", "gothica", "proba", "--dir", "applicata/auspex_impietatis/probationes"])
    run(["-m", "gothica", "proba", "--dir", "applicata/census_mortis/probationes"])
    run(["-m", "gothica", "proba", "--dir", "probationes/conformitas"])
    run(["-m", "gothica", "invoco", "exempla/salutatio.vg", "--silens"])
    run(["-m", "gothica", "invoco", "exempla/litania_numerorum.vg", "--silens"])
    run(["-m", "gothica", "invoco", "exempla/census_servitorum.vg", "--silens"])
    run(["-m", "gothica", "invoco", "exempla/auspex_lectio.vg", "--silens"])
    run(["-m", "gothica", "invoco",
         "applicata/cogitator_arithmetica/principium.vg",
         "additio", "VII", "III", "--silens"])
    run(["-m", "gothica", "invoco",
         "applicata/auspex_impietatis/principium.vg", "OMNISSIAH", "--silens"])
    run(["-m", "gothica", "invoco",
         "applicata/census_mortis/principium.vg",
         "census", "D", "X", "V", "III", "--silens"])
    run(["-m", "gothica", "censura", "applicata/cogitator_arithmetica", "--silens"])
    run(["-m", "gothica", "censura", "applicata/auspex_impietatis", "--silens"])
    run(["-m", "gothica", "censura", "applicata/census_mortis", "--silens"])
    run(["-m", "gothica", "librarium", "quaere", "gothica", "--silens"])
    run(["-m", "gothica", "librarium", "inspice",
         "github.com/adeptusprogus/vox-gothica", "--silens"])
    run(["-m", "gothica", "purga", "exempla", "--silens"])
    run(["-m", "gothica", "purga", "exempla", "--proba", "--silens"])
    run(["-m", "gothica", "lustro", "exempla", "--silens"])
    run(["-m", "gothica", "censura", "exempla", "--silens"])
    run(["-m", "gothica", "censura", "demo/fons/tributum.vg", "--silens"])
    run(["-m", "gothica", "speculum", "exempla/census_servitorum.vg", "--silens"])
    run(["-m", "gothica", "codex", "lustro", "--silens"])
    run(["-m", "gothica", "codex", "--silens"])
    for bad in ("typus_pravus", "reditus_pravus", "typus_ignotus", "ritus_pravus",
                "ordo_pravus", "modulus_pravus", "ordo_inner_pravus", "ordo_cov_assign",
                "schema_pravus", "condicio_pravus", "binop_pravus", "import_pravus",
                "tabula_key_pravus"):
        r = subprocess.run(
            [sys.executable, "-m", "gothica", "censura",
             f"probationes/censura/{bad}.vg", "--silens"],
            check=False,
        )
        if r.returncode != 1:
            raise SystemExit(f"censura should reject {bad}.vg")
    run(["scripts/run_typi_proba.py"])
    run(["-m", "gothica", "scribe-solum", "exempla/fabrica_interretialis.vg", "--silens"])
    print("++ omnia sancta ++")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
