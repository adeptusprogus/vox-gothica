"""litania.claustrum lockfile (08-litaniae §5)."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LockEntry:
    via: str
    versio: str
    fons: str
    signum: str


def _bad(msg: str, path: str) -> None:
    raise Profanatio("P-XV", "claustrum_pravum", msg, path, 0)


def load_claustrum(path: str | Path) -> list[LockEntry]:
    path = Path(path)
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    entries: list[LockEntry] = []
    cur: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[[claustrum]]":
            if cur:
                entries.append(_entry_from(cur, str(path)))
            cur = {}
            continue
        for key in ("via", "versio", "fons", "signum"):
            m = re.match(rf'^{key}\s*=\s*"(.*)"\s*$', line)
            if m:
                cur[key] = m.group(1)
                break
        else:
            _bad(f"unexpected lockfile line: {line}", str(path))
    if cur:
        entries.append(_entry_from(cur, str(path)))
    return entries


def _entry_from(cur: dict[str, str], path: str) -> LockEntry:
    missing = [k for k in ("via", "versio", "fons", "signum") if k not in cur]
    if missing:
        _bad(f"lock entry missing fields: {', '.join(missing)}", path)
    return LockEntry(**cur)  # type: ignore[arg-type]


def write_claustrum(path: str | Path, entries: list[LockEntry]) -> None:
    lines = ["# litania.claustrum — machine-written; commit to version control", ""]
    for e in sorted(entries, key=lambda x: x.via):
        lines.extend([
            "[[claustrum]]",
            f'via     = "{e.via}"',
            f'versio  = "{e.versio}"',
            f'fons    = "{e.fons}"',
            f'signum  = "{e.signum}"',
            "",
        ])
    Path(path).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def tree_signum(root: Path) -> str:
    h = hashlib.sha256()
    for fp in sorted(root.rglob("*")):
        if not fp.is_file():
            continue
        rel = fp.relative_to(root).as_posix().encode()
        h.update(rel)
        h.update(fp.read_bytes())
    return f"sha256:{h.hexdigest()}"


def claustrum_path(root: str | Path) -> Path:
    return Path(root) / "litania.claustrum"
