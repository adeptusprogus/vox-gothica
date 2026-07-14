"""Diagnostic rendering (docs 12 §2)."""
from __future__ import annotations
import json
import sys
from .heresiae import Heresis, Profanatio, IraMachinae, HINTS
from .lexicon import int_to_roman


def _versus(n: int, profanum: bool) -> str:
    if profanum:
        return str(n)
    try:
        return int_to_roman(n) if 0 <= n <= 3999 else str(n)
    except ValueError:
        return str(n)


def render_profanatio(p: Profanatio, profanum=False) -> str:
    if profanum:
        return json.dumps({"order": "profanatio", "code": p.code,
                           "genus": p.genus, "file": p.archivum,
                           "line": p.versus, "message": p.nuntius})
    return (f"⚙ PROFANATIO DETECTA — {p.archivum}, "
            f"VERSUS {_versus(p.versus, False)}\n"
            f"  [{p.code}] genus: {p.genus}\n  {p.nuntius}")


def render_heresis(h: Heresis, profanum=False) -> str:
    if profanum:
        return json.dumps({"order": "heresis_maioris" if h.major else "heresis",
                           "genus": h.genus, "file": h.archivum,
                           "line": h.versus, "message": h.nuntius,
                           "trace": h.vestigium})
    kind = "HERESIS MAIORIS" if h.major else "HERESIS"
    out = [f"⚙ {kind} DETECTA — {h.archivum}, "
           f"VERSUS {_versus(h.versus, False)}",
           f"  genus: {h.genus}",
           f"  {h.nuntius}"]
    if h.vestigium:
        out.append("  vestigium:")
        out += [f"    {f}" for f in h.vestigium]
    hint = HINTS.get(h.genus)
    if hint:
        out.append(f"  ++ hint: {hint}")
    if h.origo is not None:
        out.append(f"  origo: [{h.origo.genus}] {h.origo.nuntius}")
    return "\n".join(out)


def render_ira(e: IraMachinae, profanum=False) -> str:
    if profanum:
        return json.dumps({"order": "ira_machinae", "message": e.nuntius,
                           "stderr": e.stderr})
    out = [f"⚙ IRA MACHINAE — the Machine Spirit rejects the rite",
           f"  {e.nuntius}"]
    if e.stderr:
        out.append("  ---- verbatim voice of the machine ----")
        out.append(e.stderr.rstrip())
    return "\n".join(out)
