"""Edit litania.toml dependency tables."""
from __future__ import annotations

import re
from pathlib import Path

from ..heresiae import Profanatio
from .manifestum import manifest_path

_SECTIONS = ("requirit", "requirit_probationis")


def _bad(msg: str, path: str) -> None:
    raise Profanatio("P-XIV", "manifestum_pravum", msg, path, 0)


def remove_dependency(root: str | Path, via: str) -> bool:
    path = manifest_path(root)
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf'^"{re.escape(via)}"\s*=.*\n', re.MULTILINE)
    new_text, n = pattern.subn("", text)
    if n == 0:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def set_constraint(root: str | Path, via: str, constraint: str) -> None:
    path = manifest_path(root)
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf'^("{re.escape(via)}"\s*= ).*$', re.MULTILINE)
    if not pattern.search(text):
        _bad(f"dependency '{via}' not in manifest", str(path))
    text = pattern.sub(rf'\1"{constraint}"', text)
    path.write_text(text, encoding="utf-8")
