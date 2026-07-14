"""Parse and validate litania.toml (08-litaniae §3)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

from ..heresiae import Profanatio

_VIA_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]*$")
_CONSTRAINT_RE = re.compile(
    r"^(?P<op>\^|~|=|>=)?(?P<ver>\d+(?:\.\d+)*(?:-[a-zA-Z0-9.]+)?)$"
)


@dataclass
class Manifest:
    via: str
    versio: str | None = None
    descriptio: str | None = None
    auctores: list[str] = field(default_factory=list)
    licentia: str | None = None
    gothica: str | None = None
    requirit: dict[str, str] = field(default_factory=dict)
    requirit_probationis: dict[str, str] = field(default_factory=dict)
    principium: str | None = None
    publishable: bool = False


def _bad(msg: str, path: str) -> None:
    raise Profanatio("P-XIV", "manifestum_pravum", msg, path, 0)


def _section_table(data: dict[str, Any], key: str, path: str) -> dict[str, str]:
    block = data.get(key)
    if block is None:
        return {}
    if not isinstance(block, dict):
        _bad(f"[{key}] must be a table", path)
    out: dict[str, str] = {}
    for dep, constraint in block.items():
        if not isinstance(dep, str) or not isinstance(constraint, str):
            _bad(f"[{key}] keys and values must be strings", path)
        out[dep] = constraint
    return out


def _validate_via(via: str, path: str) -> None:
    if not via or not _VIA_RE.match(via):
        _bad(f"invalid litania.via '{via}'", path)


def _validate_constraint(constraint: str, path: str, ctx: str) -> None:
    if not _CONSTRAINT_RE.match(constraint.strip()):
        _bad(f"malformed version constraint '{constraint}' in {ctx}", path)


def load_manifest(path: str | Path) -> Manifest:
    path = Path(path)
    if not path.is_file():
        _bad("litania.toml not found", str(path))
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except Exception as exc:  # tomllib uses TOMLDecodeError
        _bad(f"cannot parse manifest: {exc}", str(path))
    if not isinstance(data, dict):
        _bad("manifest root must be a table", str(path))

    lit = data.get("litania")
    if not isinstance(lit, dict):
        _bad("[litania] table is required", str(path))
    via = lit.get("via")
    if not isinstance(via, str):
        _bad("litania.via is required", str(path))
    _validate_via(via, str(path))

    versio = lit.get("versio")
    if versio is not None and not isinstance(versio, str):
        _bad("litania.versio must be a string", str(path))

    requirit = _section_table(data, "requirit", str(path))
    requirit_prob = _section_table(data, "requirit_probationis", str(path))
    for dep, c in {**requirit, **requirit_prob}.items():
        _validate_via(dep, str(path))
        _validate_constraint(c, str(path), dep)

    cant = data.get("canticum")
    principium = None
    if cant is not None:
        if not isinstance(cant, dict):
            _bad("[canticum] must be a table", str(path))
        p = cant.get("principium")
        if p is not None:
            if not isinstance(p, str):
                _bad("canticum.principium must be a string", str(path))
            principium = p

    publishable = versio is not None and principium is None
    if publishable and not versio:
        _bad("published litaniae require litania.versio", str(path))

    auctores = lit.get("auctores") or []
    if not isinstance(auctores, list) or not all(isinstance(a, str) for a in auctores):
        _bad("litania.auctores must be a string array", str(path))

    return Manifest(
        via=via,
        versio=versio if isinstance(versio, str) else None,
        descriptio=lit.get("descriptio") if isinstance(lit.get("descriptio"), str) else None,
        auctores=list(auctores),
        licentia=lit.get("licentia") if isinstance(lit.get("licentia"), str) else None,
        gothica=lit.get("gothica") if isinstance(lit.get("gothica"), str) else None,
        requirit=requirit,
        requirit_probationis=requirit_prob,
        principium=principium,
        publishable=publishable,
    )


def manifest_path(root: str | Path) -> Path:
    return Path(root) / "litania.toml"
