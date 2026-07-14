"""gothica purga — canonical formatter (docs 12-cli §Hygiene)."""
from __future__ import annotations

from pathlib import Path

from .emit import Emitter
from .parser import parse_source


def _collect_vg(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".vg" else []
    return sorted(path.rglob("*.vg"))


def format_source(src: str, archivum: str, *, latinizat: bool = False) -> str:
    prog = parse_source(src, archivum)
    return Emitter(latinizat=latinizat).emit_program(prog)


def purga_path(
    path: Path,
    *,
    check_only: bool = False,
    latinizat: bool = False,
) -> bool:
    """Return True if file is already canonical (or was written)."""
    text = path.read_text(encoding="utf-8")
    formatted = format_source(text, str(path), latinizat=latinizat)
    if formatted == text:
        return True
    if not check_only:
        path.write_text(formatted, encoding="utf-8")
    return False


def purga(
    target: str | Path,
    *,
    check_only: bool = False,
    latinizat: bool = False,
) -> tuple[int, int]:
    """Format .vg files. Returns (changed, total)."""
    root = Path(target).resolve()
    files = _collect_vg(root)
    changed = 0
    for fp in files:
        if not purga_path(fp, check_only=check_only, latinizat=latinizat):
            changed += 1
    return changed, len(files)
