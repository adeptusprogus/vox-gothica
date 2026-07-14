"""Cross-module resolution for gothica censura (M5)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from . import arbor as A
from .parser import parse_source

_NUM = A.TName(name="NUMERUS")
_FR = A.TName(name="FRACTIO")
_VR = A.TName(name="VERITAS")
_NH = A.TName(name="NIHIL")
_RT = A.TName(name="RITUS")
_WILD = A.TName(name="*")
_ORDO_ANY = A.TOrdo(inner=_WILD)


def _rt(params, ret) -> A.TRitus:
    return A.TRitus(params=list(params), ret=ret)


@dataclass
class ModRef:
    path: str
    line: int = 0


@dataclass
class ModuleInfo:
    path: str
    archivum: str
    schemas: set[str] = field(default_factory=set)
    rites: dict[str, A.TRitus] = field(default_factory=dict)
    exports: dict[str, Any] = field(default_factory=dict)


_STDLIB: dict[str, dict[str, Any]] = {
    "mathematica": {
        "fractio_integra": _rt([(None, _FR)], _NUM),
        "radix": _rt([(None, _NUM)], _FR),
        "minimus": _rt([(None, _NUM)], _NUM),
        "maximus": _rt([(None, _NUM)], _NUM),
    },
    "probatio": {
        "adfirma": _rt([(None, _VR), (None, _NH)], _NH),
        "adfirma_aequalia": _rt([(None, _NUM), (None, _NUM), (None, _NH)], _NH),
        "adfirma_heresim": _rt([(None, _NH), (None, _RT)], _NH),
        "praetermitte": _rt([(None, _NH)], _NH),
    },
    "ordo_opera": {
        "excerne": _rt([(None, _ORDO_ANY), (None, _RT)], _ORDO_ANY),
        "transmuta": _rt([(None, _ORDO_ANY), (None, _RT)], _ORDO_ANY),
        "redige": _rt([(None, _ORDO_ANY), (None, _RT), (None, _NUM)], _NUM),
        "ordina": _rt([(None, _ORDO_ANY)], _ORDO_ANY),
        "summa": _rt([(None, _ORDO_ANY)], _NUM),
    },
}


class ModuleResolver:
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.cache: dict[str, ModuleInfo] = {}
        self.loading: list[str] = []

    def load(self, path: str, node: A.Node | None = None) -> ModuleInfo:
        if path in self.cache:
            return self.cache[path]
        if path in self.loading:
            cycle = " -> ".join(self.loading + [path])
            raise ValueError(f"impious import cycle: {cycle}")
        if path in _STDLIB:
            info = ModuleInfo(path=path, archivum=f"<stdlib:{path}>")
            info.exports = dict(_STDLIB[path])
            info.rites = {
                k: v for k, v in info.exports.items() if isinstance(v, A.TRitus)
            }
            self.cache[path] = info
            return info
        via = self._resolve_path(path)
        if via is None:
            line = getattr(node, "line", 0) or 0
            raise FileNotFoundError(f"the invocation of '{path}' went unanswered")
        self.loading.append(path)
        try:
            with open(via, encoding="utf-8") as f:
                prog = parse_source(f.read(), via)
            if prog.mode != "LITANIA":
                raise ValueError(f"only a LITANIA may be invoked ('{path}' is {prog.mode})")
            info = ModuleInfo(path=path, archivum=via)
            for st in prog.body:
                if isinstance(st, A.SchemaDef):
                    info.schemas.add(st.name)
                    info.exports[st.name] = A.TName(line=st.line, name=st.name)
                elif isinstance(st, A.RiteDef):
                    sig = _rt(st.params, st.ret)
                    info.rites[st.name] = sig
                    info.exports[st.name] = sig
                elif isinstance(st, A.Declare) and st.sanctum:
                    info.exports[st.name] = st.type
            self.cache[path] = info
            return info
        finally:
            self.loading.pop()

    def _resolve_path(self, path: str) -> str | None:
        base = path.split("/")[-1]
        candidates = [
            os.path.join(self.root_dir, path + ".vg"),
            os.path.join(self.root_dir, "litaniae", path, "fons", base + ".vg"),
        ]
        return next((c for c in candidates if os.path.isfile(c)), None)

    def export_type(self, path: str, name: str) -> Any | None:
        info = self.load(path)
        return info.exports.get(name)

    def schemas_for(self, prog: A.Program) -> set[str]:
        out: set[str] = set()
        for st in prog.body:
            if isinstance(st, A.SchemaDef):
                out.add(st.name)
        for st in prog.body:
            if isinstance(st, A.Import):
                try:
                    out |= self.load(st.path, st).schemas
                except (FileNotFoundError, ValueError):
                    pass
        return out
