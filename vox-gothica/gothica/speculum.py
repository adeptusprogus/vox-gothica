"""gothica speculum — LSP-oriented diagnostics (M5, docs 12-cli §2)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

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


def _to_lsp(records: list[dict], uri: str) -> dict:
    severity = {"lustro": 2, "censura": 1}
    diags = []
    for rec in records:
        diags.append({
            "range": {
                "start": {"line": max(0, rec["line"] - 1), "character": rec.get("col", 0)},
                "end": {"line": max(0, rec["line"] - 1), "character": rec.get("col", 0)},
            },
            "severity": severity.get(rec["order"], 2),
            "code": rec["code"],
            "source": "gothica",
            "message": rec["message"],
        })
    return {"uri": uri, "diagnostics": diags}


def _handle_request(req: dict, *, default_root: str | None) -> dict:
    rid = req.get("id")
    method = req.get("method")
    params = req.get("params") or {}
    try:
        if method == "analyze":
            path = params["file"]
            root = params.get("root") or default_root or _find_root(Path(path).parent)
            records = analyze(path, root_dir=root)
            if params.get("lsp"):
                uri = params.get("uri") or Path(path).resolve().as_uri()
                result = _to_lsp(records, uri)
            else:
                result = records
            return {"id": rid, "result": result}
        if method == "shutdown":
            return {"id": rid, "result": None, "_shutdown": True}
        return {
            "id": rid,
            "error": {"code": -32601, "message": f"unknown method: {method}"},
        }
    except Exception as exc:
        return {"id": rid, "error": {"code": -32600, "message": str(exc)}}


def serve_stdio(*, root_dir: str | None = None) -> int:
    """NDJSON RPC transport for editor plugins (M5 LSP stub)."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        req = json.loads(line)
        resp = _handle_request(req, default_root=root_dir)
        print(json.dumps(resp), flush=True)
        if resp.get("_shutdown"):
            return 0
    return 0
