"""gothica speculum — LSP-oriented diagnostics (M5 stub, docs 12-cli §2)."""
from __future__ import annotations

from pathlib import Path

from . import lustro as lit_lustro
from . import censura as lit_censura
from .modularis import ModuleResolver
from .diagnostic_records import lint as lint_record, censura as censura_record


def _find_root(start: Path) -> str:
    probe = start.resolve()
    while True:
        if (probe / "litania.toml").is_file():
            return str(probe)
        parent = probe.parent
        if parent == probe:
            return str(start.resolve())
        probe = parent


def analyze(path: str | Path, *, root_dir: str | None = None) -> list[dict]:
    fp = Path(path).resolve()
    if not fp.is_file():
        return []
    root = root_dir or _find_root(fp.parent)
    records: list[dict] = []
    text = fp.read_text(encoding="utf-8")
    archivum = str(fp)
    for lint in lit_lustro.lint_source(text, archivum):
        records.append(lint_record(lint))
    resolver = ModuleResolver(root)
    for finding in lit_censura.check_source(text, archivum, resolver=resolver):
        records.append(censura_record(finding))
    return records
