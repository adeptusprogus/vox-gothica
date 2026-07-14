"""JSON diagnostic records for CI and LSP (docs 12-cli §2)."""
from __future__ import annotations

from .heresiae import HINTS
from .lustro import Lint
from .censura import Finding


def lint(hit: Lint) -> dict:
    return {
        "order": "lustro",
        "code": hit.code,
        "genus": hit.code,
        "file": hit.archivum,
        "line": hit.line,
        "col": 0,
        "message": hit.message,
        "hint": "",
        "trace": [],
    }


def censura(hit: Finding) -> dict:
    return {
        "order": "censura",
        "code": hit.code,
        "genus": hit.genus,
        "file": hit.archivum,
        "line": hit.line,
        "col": 0,
        "message": hit.message,
        "hint": HINTS.get(hit.genus, ""),
        "trace": [],
    }
