"""Canonical source emission for gothica purga (docs 12-cli §Hygiene)."""
from __future__ import annotations

import re

from . import arbor as A
from .fabrica import ALIASES
from .lexicon import int_to_roman

_INDENT = "    "
_REVERSE_ALIASES = {v: k for k, v in ALIASES.items()}


class Emitter:
    def __init__(self, *, latinizat: bool = False):
        self.latinizat = latinizat
        self._lines: list[str] = []
        self._level = 0

    def emit_program(self, prog: A.Program) -> str:
        self._lines = ["AVE OMNISSIAH.", f'{prog.mode} "{prog.name}".', ""]
        for i, st in enumerate(prog.body):
            if i and isinstance(st, (A.RiteDef, A.SchemaDef, A.Declare)):
                if self._lines and self._lines[-1] != "":
                    self._lines.append("")
            self._stmt(st, top=True)
        while self._lines and self._lines[-1] == "":
            self._lines.pop()
        return "\n".join(self._lines) + "\n"

    def _w(self, text: str) -> None:
        self._lines.append(_INDENT * self._level + text)

    def _blank(self) -> None:
        if self._lines and self._lines[-1] != "":
            self._lines.append("")

    def _stmt(self, st, *, top: bool = False, in_loop: bool = False) -> None:
        if isinstance(st, A.Declare):
            kw = "SANCTUM" if st.sanctum else "DECLARO"
            self._w(f"{kw} {st.name} : {self._type(st.type)} = {self._expr(st.expr)}")
        elif isinstance(st, A.RiteDef):
            kw = "SANCTUM RITUS" if st.sanctum else "RITUS"
            sig = self._rite_sig(st.params, st.ret)
            self._w(f"{kw} {st.name}{sig}")
            self._level += 1
            for s in st.body:
                self._stmt(s, in_loop=in_loop)
            self._level -= 1
            self._w("FINIS RITUS")
        elif isinstance(st, A.SchemaDef):
            self._w(f"SCHEMA {st.name}")
            self._level += 1
            for name, ty, default in st.fields:
                if default is None:
                    self._w(f"{name} : {self._type(ty)}")
                else:
                    self._w(f"{name} : {self._type(ty)} = {self._expr(default)}")
            self._level -= 1
            self._w("FINIS SCHEMA")
        elif isinstance(st, A.Assign):
            self._w(f"{self._expr(st.target)} FIAT {self._expr(st.expr)}")
        elif isinstance(st, A.If):
            for i, (cond, body) in enumerate(st.arms):
                if i == 0:
                    self._w(f"SI {self._expr(cond)} TUNC")
                else:
                    self._w(f"ALITER SI {self._expr(cond)} TUNC")
                self._level += 1
                for s in body:
                    self._stmt(s, in_loop=in_loop)
                self._level -= 1
            if st.els:
                self._w("ALITER")
                self._level += 1
                for s in st.els:
                    self._stmt(s, in_loop=in_loop)
                self._level -= 1
            self._w("FINIS SI")
        elif isinstance(st, A.While):
            self._w(f"DUM {self._expr(st.cond)} AGE")
            self._level += 1
            for s in st.body:
                self._stmt(s, in_loop=True)
            self._level -= 1
            self._w("FINIS DUM")
        elif isinstance(st, A.For):
            self._w(f"PRO OMNI {st.var} IN {self._expr(st.it)} AGE")
            self._level += 1
            for s in st.body:
                self._stmt(s, in_loop=True)
            self._level -= 1
            self._w("FINIS PRO")
        elif isinstance(st, A.Try):
            self._w("TEMPTA")
            self._level += 1
            for s in st.body:
                self._stmt(s, in_loop=in_loop)
            self._level -= 1
            if st.catch_var:
                self._w(f"SI HERESIS ({st.catch_var})")
                self._level += 1
                for s in st.catch or []:
                    self._stmt(s, in_loop=in_loop)
                self._level -= 1
            if st.fin:
                self._w("DENIQUE")
                self._level += 1
                for s in st.fin:
                    self._stmt(s, in_loop=in_loop)
                self._level -= 1
            self._w("FINIS TEMPTA")
        elif isinstance(st, A.Print):
            kw = "SUSURRO" if st.err else "VOCIFERO"
            self._w(f"{kw} {self._expr(st.expr)}")
        elif isinstance(st, A.Return):
            if st.expr is None:
                self._w("REDDO")
            elif isinstance(st.expr, A.RiteExpr):
                self._emit_rite_expr(st.expr, prefix="REDDO ")
            else:
                self._w(f"REDDO {self._expr(st.expr)}")
        elif isinstance(st, A.Raise):
            if st.genus:
                self._w(f'PROCLAMO HERESIM {self._expr(st.expr)} GENERIS "{st.genus}"')
            else:
                self._w(f"PROCLAMO HERESIM {self._expr(st.expr)}")
        elif isinstance(st, A.Break):
            self._w("RUMPO")
        elif isinstance(st, A.Continue):
            self._w("PERGO")
        elif isinstance(st, A.Import):
            if st.names:
                names = ", ".join(st.names)
                self._w(f'INVOCO {names} EX "{st.path}"')
            elif st.alias:
                self._w(f'INVOCO "{st.path}" UT {st.alias}')
            else:
                self._w(f'INVOCO "{st.path}"')
        elif isinstance(st, A.Foedus):
            self._emit_infra("FOEDUS", st.name, st.attrs, finis="FOEDUS")
        elif isinstance(st, A.Sedes):
            self._emit_infra("SEDES", st.name, st.attrs, finis="SEDES")
        elif isinstance(st, A.Exstruatur):
            self._w(f"EXSTRUATUR {st.species} {self._expr(st.name_expr)}")
            self._emit_attrs(st.attrs, nested_finis=True)
            self._w("FINIS EXSTRUATUR")
        elif isinstance(st, A.Scrutor):
            self._w(f'SCRUTOR {st.label} "{st.name}"')
            self._emit_attrs(st.attrs)
            self._w("FINIS SCRUTOR")
        elif isinstance(st, A.Postulo):
            kw = "ARCANUM POSTULO" if st.arcanum else "POSTULO"
            if st.default is not None:
                self._w(f"{kw} {st.name} : {self._type(st.type)} = {self._expr(st.default)}")
            else:
                self._w(f"{kw} {st.name} : {self._type(st.type)}")
        elif isinstance(st, A.Profiteor):
            kw = "ARCANUM PROFITEOR" if st.arcanum else "PROFITEOR"
            self._w(f"{kw} {st.name} = {self._expr(st.expr)}")
        elif isinstance(st, A.ExprStmt):
            self._w(self._expr(st.expr))
        else:
            self._w(f"++ unhandled {type(st).__name__} ++")

    def _rite_sig(self, params, ret) -> str:
        ps = ", ".join(f"{n} : {self._type(t)}" for n, t in params)
        inner = f"({ps})" if ps else "()"
        if ret is not None:
            inner += f" -> {self._type(ret)}"
        return inner

    def _emit_infra(self, kw: str, name: str, attrs, *, finis: str) -> None:
        self._w(f'{kw} "{name}"')
        self._emit_attrs(attrs)
        self._w(f"FINIS {finis}")

    def _emit_attrs(self, attrs: list, *, nested_finis: bool = False) -> None:
        if not attrs:
            return
        keys = [self._attr_key(a.key) for a in attrs]
        width = max(len(self._attr_key_emit(a.key)) for a in attrs)
        self._level += 1
        for attr in attrs:
            key = self._attr_key_emit(attr.key)
            pad = " " * (width - len(key))
            if isinstance(attr.value, list):
                self._w(f"{key}{pad}:")
                self._level += 1
                for sub in attr.value:
                    sk = self._attr_key_emit(sub.key)
                    self._w(f"{sk}: {self._expr(sub.value)}")
                self._level -= 1
                if nested_finis:
                    self._w("FINIS")
            else:
                self._w(f"{key}{pad}: {self._expr(attr.value)}")
        self._level -= 1

    def _attr_key(self, key: str) -> str:
        if self.latinizat and key in _REVERSE_ALIASES:
            key = _REVERSE_ALIASES[key]
        return key

    def _attr_key_emit(self, key: str) -> str:
        key = self._attr_key(key)
        if re.match(r"^[a-z_][a-z0-9_]*$", key):
            return key
        return f'"{key}"'

    def _type(self, ty) -> str:
        if isinstance(ty, A.TName):
            return ty.name
        if isinstance(ty, A.TOrdo):
            return f"ORDO[{self._type(ty.inner)}]"
        if isinstance(ty, A.TTabula):
            return f"TABULA[{self._type(ty.k)}, {self._type(ty.v)}]"
        if isinstance(ty, A.TRitus):
            ps = ", ".join(
                f"{n}: {self._type(pt)}" if n else self._type(pt)
                for n, pt in ty.params
            )
            return f"RITUS({ps}) -> {self._type(ty.ret)}"
        return "?"

    def _expr(self, e) -> str:
        if isinstance(e, A.Num):
            try:
                return int_to_roman(e.v)
            except ValueError:
                return str(e.v)
        if isinstance(e, A.Flo):
            return repr(e.v)
        if isinstance(e, A.Bool):
            return "VERUM" if e.v else "FALSUM"
        if isinstance(e, A.Nihil):
            return "NIHIL"
        if isinstance(e, A.Ident):
            return e.name
        if isinstance(e, A.Str):
            parts = []
            for kind, val in e.parts:
                if kind == "t":
                    parts.append(val.replace("\\", "\\\\").replace('"', '\\"'))
                else:
                    parts.append("{" + self._expr(val) + "}")
            return '"' + "".join(parts) + '"'
        if isinstance(e, A.ListLit):
            items = ", ".join(self._expr(x) for x in e.items)
            return f"[{items}]"
        if isinstance(e, A.MapLit):
            pairs = ", ".join(
                f"{self._map_key_emit(k)}: {self._expr(v)}" for k, v in e.entries
            )
            return "{" + pairs + "}"
        if isinstance(e, A.SchemaLit):
            fields = ", ".join(f"{n}: {self._expr(v)}" for n, v in e.fields)
            return f"{e.name} {{ {fields} }}"
        if isinstance(e, A.RiteExpr):
            return "RITUS /* use _emit_rite_expr */"
        if isinstance(e, A.BinOp):
            return f"{self._expr(e.l)} {e.op} {self._expr(e.r)}"
        if isinstance(e, A.UnOp):
            return f"{e.op}{self._expr(e.e)}"
        if isinstance(e, A.Call):
            args = ", ".join(self._expr(a) for a in e.args)
            return f"{self._expr(e.fn)}({args})"
        if isinstance(e, A.Index):
            return f"{self._expr(e.obj)}[{self._expr(e.idx)}]"
        if isinstance(e, A.Attr):
            return f"{self._expr(e.obj)}.{e.name}"
        return "?"

    def _map_key_emit(self, k) -> str:
        if isinstance(k, A.Str):
            return self._expr(k)
        if isinstance(k, A.Ident):
            name = k.name
            if re.match(r"^[a-z_][a-z0-9_]*$", name):
                return name
            return f'"{name}"'
        return self._expr(k)

    def _emit_rite_expr(self, e: A.RiteExpr, *, prefix: str = "") -> None:
        sig = self._rite_sig(e.params, e.ret)
        self._w(f"{prefix}RITUS{sig}")
        self._level += 1
        for s in e.body:
            self._stmt(s)
        self._level -= 1
        self._w("FINIS RITUS")
