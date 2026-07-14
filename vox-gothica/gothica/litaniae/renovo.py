"""gothica renovo — raise dependency constraints (08-litaniae §4, §8)."""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..heresiae import Profanatio
from . import adfero as lit_adfero
from .manifest_edit import set_constraint
from .manifestum import load_manifest, manifest_path
from .adfero import _git_url, _parse_min_version


def _parse_version(ver: str) -> tuple[int, ...]:
    core = ver.lstrip("v").split("-")[0]
    parts = []
    for p in core.split("."):
        parts.append(int(p) if p.isdigit() else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def _satisfies(ver: str, constraint: str) -> bool:
    v = _parse_version(ver)
    c = constraint.strip()
    if c.startswith("^"):
        lo = _parse_version(_parse_min_version(c))
        return v >= lo and v[0] == lo[0]
    if c.startswith("~"):
        lo = _parse_version(_parse_min_version(c))
        return v >= lo and v[0] == lo[0] and v[1] == lo[1]
    if c.startswith("="):
        return v == _parse_version(_parse_min_version(c))
    if c.startswith(">="):
        return v >= _parse_version(_parse_min_version(c))
    return v == _parse_version(c)


def _list_tags(via: str) -> list[str]:
    url = _git_url(via)
    proc = subprocess.run(
        ["git", "ls-remote", "--tags", url],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        raise Profanatio(
            "P-XIV", "fons_inaccessibilis",
            f"cannot list tags for '{via}'",
            via, 0,
        )
    tags = []
    for line in proc.stdout.splitlines():
        if "refs/tags/" not in line:
            continue
        tag = line.split("refs/tags/")[-1]
        if tag.endswith("^{}"):
            continue
        tags.append(tag.lstrip("v"))
    return tags


def _newest_compatible(via: str, constraint: str) -> str:
    tags = _list_tags(via)
    matching = [t for t in tags if _satisfies(t, constraint)]
    if not matching:
        raise Profanatio(
            "P-XIV", "versio_innota",
            f"no tag satisfies '{constraint}' for '{via}'",
            via, 0,
        )
    return max(matching, key=_parse_version)


def renovo(root: str | Path, via: str | None = None) -> list[tuple[str, str, str]]:
    root = Path(root).resolve()
    manifest = load_manifest(manifest_path(root))
    deps = dict(manifest.requirit)
    if via:
        if via not in deps:
            raise Profanatio(
                "P-XIV", "via_absens",
                f"'{via}' is not in [requirit]",
                str(manifest_path(root)), 0,
            )
        deps = {via: deps[via]}

    bumps: list[tuple[str, str, str]] = []
    for dep, constraint in sorted(deps.items()):
        newest = _newest_compatible(dep, constraint)
        new_constraint = f"^{newest}"
        if new_constraint == constraint:
            continue
        set_constraint(root, dep, new_constraint)
        bumps.append((dep, constraint, new_constraint))

    lit_adfero.sync(root)
    return bumps
