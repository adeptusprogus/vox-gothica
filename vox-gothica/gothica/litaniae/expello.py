"""gothica expello — remove a dependency (08-litaniae §8)."""
from __future__ import annotations

import shutil
from pathlib import Path

from ..heresiae import Profanatio
from . import adfero as lit_adfero
from .manifest_edit import remove_dependency
from .manifestum import load_manifest, manifest_path


def _transitively_required(root: Path, via: str) -> str | None:
    lit_root = root / "litaniae"
    if not lit_root.is_dir():
        return None
    for child in lit_root.iterdir():
        mpath = child / "litania.toml"
        if not mpath.is_file():
            continue
        manifest = load_manifest(mpath)
        if via in manifest.requirit or via in manifest.requirit_probationis:
            return manifest.via
    return None


def expello(root: str | Path, via: str) -> None:
    root = Path(root).resolve()
    manifest = load_manifest(manifest_path(root))
    if via not in manifest.requirit and via not in manifest.requirit_probationis:
        raise Profanatio(
            "P-XIV", "via_absens",
            f"'{via}' is not a direct dependency of this project",
            str(manifest_path(root)), 0,
        )
    req = _transitively_required(root, via)
    if req:
        raise Profanatio(
            "P-XIV", "requiritur_adhuc",
            f"cannot expello '{via}' — still required by '{req}'",
            str(manifest_path(root)), 0,
        )
    if not remove_dependency(root, via):
        raise Profanatio(
            "P-XIV", "via_absens",
            f"failed to remove '{via}' from manifest",
            str(manifest_path(root)), 0,
        )
    vendored = root / "litaniae" / via
    if vendored.exists():
        shutil.rmtree(vendored)
    lit_adfero.sync(root)
