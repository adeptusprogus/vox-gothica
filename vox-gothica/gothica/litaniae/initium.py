"""gothica initium — project scaffold (08-litaniae §8)."""
from __future__ import annotations

from pathlib import Path

_PROJECT_MANIFEST = """\
[litania]
via = "{via}"
descriptio = "A canticle of Vox Gothica"
gothica = ">=0.2"

[canticum]
principium = "principium.vg"
"""

_LITANIA_MANIFEST = """\
[litania]
via = "{via}"
versio = "0.1.0"
descriptio = "A publishable litania of Vox Gothica"
licentia = "GPL-3.0-or-later"
gothica = ">=0.2"
"""

_PRINCIPIUM = """\
AVE OMNISSIAH.
CANTICUM "principium".

VOCIFERO "Ave, Imperium!"
"""

_FONS_MOD = """\
AVE OMNISSIAH.
LITANIA "auxilium".

RITUS salve () -> NIHIL
    VOCIFERO "Sanctus auxilium."
FINIS RITUS
"""

_PROBA = """\
AVE OMNISSIAH.
LITANIA "smoke_proba".

INVOCO adfirma EX "probatio"

RITUS proba_smoke () -> NIHIL
    adfirma(VERUM, "initium scaffold is sanctus")
FINIS RITUS
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(str(path))
    path.write_text(content, encoding="utf-8")


def scaffold(root: str | Path, via: str, *, litania: bool = False) -> list[str]:
    root = Path(root).resolve()
    if (root / "litania.toml").exists():
        raise FileExistsError(str(root / "litania.toml"))

    created: list[str] = []
    manifest = (_LITANIA_MANIFEST if litania else _PROJECT_MANIFEST).format(via=via)
    _write(root / "litania.toml", manifest)
    created.append("litania.toml")

    if litania:
        _write(root / "fons" / f"{via.split('/')[-1]}.vg", _FONS_MOD)
        created.append(f"fons/{via.split('/')[-1]}.vg")
    else:
        _write(root / "principium.vg", _PRINCIPIUM)
        created.append("principium.vg")
        _write(root / "fons" / ".gitkeep", "")
        created.append("fons/")

    _write(root / "probationes" / "smoke_proba.vg", _PROBA)
    created.append("probationes/smoke_proba.vg")

    (root / "litaniae").mkdir(exist_ok=True)
    created.append("litaniae/")

    return created
