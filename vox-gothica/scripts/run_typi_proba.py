#!/usr/bin/env python3
"""Unit probations for typi.binds and speculum stdio."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gothica import arbor as A
from gothica import typi as T


def test_strict_ordo() -> None:
    num = A.TOrdo(inner=A.TName(name="NUMERUS"))
    srv = A.TOrdo(inner=A.TName(name="servitor"))
    assert T.binds(num, num)
    assert not T.binds(srv, num)
    assert T.binds(srv, A.TOrdo(inner=A.TName(name="*")))


def test_speculum_stdio() -> None:
    salutatio = ROOT / "exempla" / "salutatio.vg"
    req = json.dumps({
        "id": 1,
        "method": "analyze",
        "params": {"file": str(salutatio)},
    })
    proc = subprocess.run(
        [sys.executable, "-m", "gothica", "speculum", "--stdio", "--silens"],
        input=req + "\n",
        text=True,
        capture_output=True,
        cwd=str(ROOT),
        check=True,
    )
    resp = json.loads(proc.stdout.strip().splitlines()[-1])
    assert resp["id"] == 1
    assert resp["result"] == []


def main() -> int:
    test_strict_ordo()
    test_speculum_stdio()
    print("++ typi/speculum sancta ++")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
