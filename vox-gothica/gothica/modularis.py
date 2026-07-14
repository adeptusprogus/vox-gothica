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
_STR = A.TName(name="SCRIPTUM")
_WILD = A.TName(name="*")
_ORDO_ANY = A.TOrdo(inner=_WILD)
_ORDO_STR = A.TOrdo(inner=_STR)


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
        "potentia": _rt([(None, _NUM), (None, _NUM)], _NUM),
        "minimus": _rt([(None, _NUM)], _NUM),
        "maximus": _rt([(None, _NUM)], _NUM),
    },
    "probatio": {
        "adfirma": _rt([(None, _VR), (None, _STR)], _NH),
        "adfirma_aequalia": _rt([(None, _NUM), (None, _NUM), (None, _STR)], _NH),
        "adfirma_heresim": _rt([(None, _STR), (None, _RT)], _NH),
        "praetermitte": _rt([(None, _NH)], _NH),
    },
    "ordo_opera": {
        "excerne": _rt([(None, _ORDO_ANY), (None, _RT)], _ORDO_ANY),
        "transmuta": _rt([(None, _ORDO_ANY), (None, _RT)], _ORDO_ANY),
        "redige": _rt([(None, _ORDO_ANY), (None, _RT), (None, _NUM)], _NUM),
        "ordina": _rt([(None, _ORDO_ANY)], _ORDO_ANY),
        "ordina_per": _rt([(None, _ORDO_ANY), (None, _RT)], _ORDO_ANY),
        "inverte": _rt([(None, _ORDO_ANY)], _ORDO_ANY),
        "summa": _rt([(None, _ORDO_ANY)], _NUM),
        "quisque": _rt([(None, _ORDO_ANY), (None, _RT)], _VR),
        "ullus": _rt([(None, _ORDO_ANY), (None, _RT)], _VR),
        "compone": _rt([(None, _ORDO_ANY), (None, _ORDO_ANY)], _ORDO_ANY),
    },
    "scriptura": {
        "maiuscula": _rt([(None, _STR)], _STR),
        "minuscula": _rt([(None, _STR)], _STR),
        "divide": _rt([(None, _STR), (None, _STR)], _ORDO_STR),
        "coniunge": _rt([(None, _ORDO_ANY), (None, _STR)], _STR),
        "substitue": _rt([(None, _STR), (None, _STR), (None, _STR)], _STR),
        "incipit": _rt([(None, _STR), (None, _STR)], _VR),
        "desinit": _rt([(None, _STR), (None, _STR)], _VR),
        "continet": _rt([(None, _STR), (None, _STR)], _VR),
        "purga": _rt([(None, _STR)], _STR),
        "imple_sinistra": _rt([(None, _STR), (None, _NUM), (None, _STR)], _STR),
        "inveni": _rt([(None, _STR), (None, _STR)], _NUM),
        "mensura_octetorum": _rt([(None, _STR)], _NUM),
        "ad_octetos": _rt([(None, _STR)], A.TOrdo(inner=_NUM)),
        "ex_octetis": _rt([(None, A.TOrdo(inner=_NUM))], _STR),
    },
    "tempus": {
        "nunc": _rt([], _NUM),
        "nunc_monotonicum": _rt([], _NUM),
        "data_scriptum": _rt([(None, _NUM), (None, _STR)], _STR),
    },
    "archivum": {
        "lege": _rt([(None, _STR)], _STR),
        "scribe": _rt([(None, _STR), (None, _STR)], _NH),
        "attinge": _rt([(None, _STR), (None, _STR)], _NH),
        "existit": _rt([(None, _STR)], _VR),
        "dele": _rt([(None, _STR)], _NH),
        "enumera": _rt([(None, _STR)], _ORDO_STR),
        "crea_directorium": _rt([(None, _STR)], _NH),
    },
    "imperium": {
        "argumenta": _rt([], _ORDO_STR),
        "ambitus": _rt([(None, _STR)], _STR),
        "ambitus_aut": _rt([(None, _STR), (None, _STR)], _STR),
        "exi": _rt([(None, _NUM)], _NH),
        "impera": _rt([(None, _ORDO_ANY)], _ORDO_ANY),
    },
    "machina_cogitans": {
        "pete": _rt([(None, _STR)], _STR),
        "mitte": _rt([(None, _STR), (None, _STR)], _STR),
    },
    "codex_json": {
        "lege": _rt([(None, _STR)], _ORDO_ANY),
        "scribe": _rt([(None, _ORDO_ANY)], _STR),
        "scribe_ornatum": _rt([(None, _ORDO_ANY)], _STR),
    },
    "fortuna": {
        "inter": _rt([(None, _NUM), (None, _NUM)], _NUM),
        "fractio_fortunae": _rt([], _FR),
        "elige_sortem": _rt([(None, _ORDO_ANY)], _ORDO_ANY),
        "misce": _rt([(None, _ORDO_ANY)], _NH),
        "semen": _rt([(None, _NUM)], _NH),
    },
    "notarius": {
        "nota": _rt([(None, _STR), (None, _ORDO_ANY)], _NH),
        "debug": _rt([(None, _ORDO_ANY)], _NH),
        "info": _rt([(None, _ORDO_ANY)], _NH),
        "monitum": _rt([(None, _ORDO_ANY)], _NH),
        "error": _rt([(None, _ORDO_ANY)], _NH),
        "gradus_pone": _rt([(None, _STR)], _NH),
    },
    "fenestra": {
        "crea": _rt([(None, _STR)], _STR),
        "crea_cogitator": _rt([(None, _STR)], _STR),
        "rotula": _rt([(None, _STR), (None, _STR), (None, _ORDO_ANY)], _NH),
        "campus": _rt([(None, _STR), (None, _STR), (None, _STR)], _NH),
        "nuntius": _rt([(None, _STR), (None, _STR)], _NH),
        "lege_campo": _rt([(None, _STR), (None, _STR)], _STR),
        "lege_rotula": _rt([(None, _STR), (None, _STR)], _STR),
        "pulsor": _rt([(None, _STR), (None, _STR), (None, _RT)], _NH),
        "circulo": _rt([(None, _STR)], _NH),
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
