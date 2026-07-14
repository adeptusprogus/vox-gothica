"""gothica censura — static checker (M5 Censura, docs 14-implementation §4)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import arbor as A
from .parser import parse_source

PRIMITIVES = frozenset(
    {"NUMERUS", "FRACTIO", "SCRIPTUM", "VERITAS", "NIHIL", "RITUS", "HERESIS",
     "RELATIO"}
)


def _rite_type(params, ret, line: int) -> A.TRitus:
    return A.TRitus(line=line, params=list(params), ret=ret)


@dataclass
class Finding:
    code: str
    genus: str
    message: str
    line: int
    archivum: str


def _collect_vg(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".vg" else []
    return sorted(path.rglob("*.vg"))


def _tname(t: Any) -> str:
    if isinstance(t, A.TName):
        return t.name
    if isinstance(t, A.TOrdo):
        return f"ORDO[{_tname(t.inner)}]"
    if isinstance(t, A.TTabula):
        return f"TABULA[{_tname(t.k)}, {_tname(t.v)}]"
    if isinstance(t, A.TRitus):
        ps = ", ".join(
            f"{n}: {_tname(pt)}" if n else _tname(pt)
            for n, pt in t.params
        )
        return f"RITUS({ps}) -> {_tname(t.ret)}"
    return "?"


def _type_eq(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return a is b
    if type(a) is not type(b):
        return False
    if isinstance(a, A.TName):
        return a.name == b.name
    if isinstance(a, A.TOrdo):
        return _type_eq(a.inner, b.inner)
    if isinstance(a, A.TTabula):
        return _type_eq(a.k, b.k) and _type_eq(a.v, b.v)
    if isinstance(a, A.TRitus):
        if len(a.params) != len(b.params):
            return False
        for (_, pa), (_, pb) in zip(a.params, b.params):
            if not _type_eq(pa, pb):
                return False
        return _type_eq(a.ret, b.ret)
    return False


def _binds(got: Any, want: Any) -> bool:
    if _type_eq(got, want):
        return True
    if isinstance(want, A.TName) and want.name == "RITUS":
        return isinstance(got, A.TRitus)
    return False


def _is_nihil_type(t: Any) -> bool:
    return isinstance(t, A.TName) and t.name == "NIHIL"


class _Checker:
    def __init__(self, prog: A.Program):
        self.prog = prog
        self.schemas: set[str] = set()
        self.rites: dict[str, A.TRitus] = {}
        self.hits: list[Finding] = []

    def run(self) -> list[Finding]:
        for st in self.prog.body:
            if isinstance(st, A.SchemaDef):
                self.schemas.add(st.name)
            if isinstance(st, A.RiteDef):
                self.rites[st.name] = _rite_type(st.params, st.ret, st.line)
        for st in self.prog.body:
            self._check_type_ref(st)
        self._walk_block(self.prog.body, env=self._hoist_env())
        return self.hits

    def _hoist_env(self) -> dict[str, Any]:
        return dict(self.rites)

    def _warn(self, code: str, genus: str, message: str, line: int) -> None:
        self.hits.append(Finding(code, genus, message, line, self.prog.archivum))

    def _resolve_type(self, t: Any, line: int) -> bool:
        if t is None:
            return True
        if isinstance(t, A.TName):
            if t.name in PRIMITIVES or t.name in self.schemas:
                return True
            self._warn(
                "P-XV",
                "typus_ignotus",
                f"type '{t.name}' is not declared in this scroll",
                line,
            )
            return False
        if isinstance(t, A.TOrdo):
            return self._resolve_type(t.inner, line)
        if isinstance(t, A.TTabula):
            return self._resolve_type(t.k, line) and self._resolve_type(t.v, line)
        if isinstance(t, A.TRitus):
            ok = True
            for _, pt in t.params:
                ok = self._resolve_type(pt, line) and ok
            return self._resolve_type(t.ret, line) and ok
        return True

    def _check_type_ref(self, st) -> None:
        if isinstance(st, A.Declare):
            self._resolve_type(st.type, st.line)
        elif isinstance(st, A.RiteDef):
            for _, pt in st.params:
                self._resolve_type(pt, st.line)
            self._resolve_type(st.ret, st.line)
            if not _is_nihil_type(st.ret) and not self._all_paths_return(st.body):
                self._warn(
                    "C-II",
                    "reditus_deest",
                    f"rite '{st.name}' may end without REDDO",
                    st.line,
                )
        elif isinstance(st, A.SchemaDef):
            for _, ft, default in st.fields:
                self._resolve_type(ft, st.line)
                if default is not None:
                    self._infer(default, {})
        elif isinstance(st, A.Postulo):
            self._resolve_type(st.type, st.line)

    def _all_paths_return(self, stmts: list) -> bool:
        return self._block_must_return(stmts)

    def _block_must_return(self, stmts: list) -> bool:
        if not stmts:
            return False
        for i, st in enumerate(stmts):
            if isinstance(st, (A.Return, A.Raise)):
                return True
            if isinstance(st, A.If):
                for _, body in st.arms:
                    if not self._block_must_return(body):
                        return False
                if st.els is not None:
                    if not self._block_must_return(st.els):
                        return False
                elif not self._block_must_return(stmts[i + 1 :]):
                    return False
                return True
            if isinstance(st, (A.While, A.For)):
                return False
            if isinstance(st, A.Try):
                if st.fin is not None:
                    return False
                body_ok = self._block_must_return(st.body)
                catch_ok = st.catch is None or self._block_must_return(st.catch)
                return body_ok and catch_ok
        return False

    def _walk_block(
        self,
        stmts: list,
        *,
        env: dict[str, Any],
        ret_type: Any | None = None,
    ) -> None:
        for st in stmts:
            self._walk_stmt(st, env=env, ret_type=ret_type)

    def _walk_stmt(
        self,
        st,
        *,
        env: dict[str, Any],
        ret_type: Any | None = None,
    ) -> None:
        if isinstance(st, A.Declare):
            got = self._infer(st.expr, env)
            if got is not None:
                self._check_bind(got, st.type, st.line, f"binding '{st.name}'")
            env[st.name] = st.type
        elif isinstance(st, A.RiteDef):
            local = dict(env)
            for n, pt in st.params:
                local[n] = pt
            self._walk_block(st.body, env=local, ret_type=st.ret)
        elif isinstance(st, A.Assign):
            self._infer(st.expr, env)
            self._infer(st.target, env)
        elif isinstance(st, A.If):
            for cond, body in st.arms:
                self._infer(cond, env)
                self._walk_block(body, env=dict(env), ret_type=ret_type)
            if st.els:
                self._walk_block(st.els, env=dict(env), ret_type=ret_type)
        elif isinstance(st, A.While):
            self._infer(st.cond, env)
            self._walk_block(st.body, env=dict(env), ret_type=ret_type)
        elif isinstance(st, A.For):
            self._infer(st.it, env)
            child = dict(env)
            child[st.var] = A.TName(line=st.line, name="NUMERUS")
            self._walk_block(st.body, env=child, ret_type=ret_type)
        elif isinstance(st, A.Try):
            self._walk_block(st.body, env=dict(env), ret_type=ret_type)
            if st.catch:
                child = dict(env)
                if st.catch_var:
                    child[st.catch_var] = A.TName(line=st.line, name="HERESIS")
                self._walk_block(st.catch, env=child, ret_type=ret_type)
            if st.fin:
                self._walk_block(st.fin, env=dict(env), ret_type=ret_type)
        elif isinstance(st, A.Print):
            self._infer(st.expr, env)
        elif isinstance(st, A.Return):
            if st.expr:
                got = self._infer(st.expr, env)
                if got is not None and ret_type is not None:
                    self._check_bind(got, ret_type, st.line, "REDDO")
        elif isinstance(st, A.Raise):
            self._infer(st.expr, env)
        elif isinstance(st, A.ExprStmt):
            self._infer(st.expr, env)
        elif isinstance(st, (A.Foedus, A.Sedes, A.Exstruatur, A.Scrutor,
                             A.Profiteor, A.Import, A.SchemaDef)):
            for attr in getattr(st, "attrs", []) or []:
                if isinstance(attr.value, list):
                    for sub in attr.value:
                        self._infer(sub.value, env)
                else:
                    self._infer(attr.value, env)
            if isinstance(st, A.Exstruatur):
                self._infer(st.name_expr, env)
        elif isinstance(st, A.Postulo):
            self._resolve_type(st.type, st.line)

    def _check_bind(self, got: Any, want: Any, line: int, what: str) -> None:
        if not _binds(got, want):
            self._warn(
                "C-I",
                "typus_profanus",
                f"{what}: {_tname(got)} bound where {_tname(want)} was consecrated",
                line,
            )

    def _infer(self, e, env: dict[str, Any]) -> Any | None:
        if e is None:
            return None
        if isinstance(e, A.Num):
            return A.TName(line=e.line, name="NUMERUS")
        if isinstance(e, A.Flo):
            return A.TName(line=e.line, name="FRACTIO")
        if isinstance(e, A.Bool):
            return A.TName(line=e.line, name="VERITAS")
        if isinstance(e, A.Nihil):
            return A.TName(line=e.line, name="NIHIL")
        if isinstance(e, A.Ident):
            return self.rites.get(e.name) or env.get(e.name)
        if isinstance(e, A.ListLit):
            if not e.items:
                return None
            inner = self._infer(e.items[0], env)
            if inner is None:
                return None
            return A.TOrdo(line=e.line, inner=inner)
        if isinstance(e, A.MapLit):
            if not e.entries:
                return None
            k = self._infer(e.entries[0][0], env)
            v = self._infer(e.entries[0][1], env)
            if k is None or v is None:
                return None
            return A.TTabula(line=e.line, k=k, v=v)
        if isinstance(e, A.UnOp):
            if e.op == "-":
                inner = self._infer(e.e, env)
                if isinstance(inner, A.TName) and inner.name == "NUMERUS":
                    return inner
                if isinstance(inner, A.TName) and inner.name == "FRACTIO":
                    return inner
            if e.op == "NON":
                return A.TName(line=e.line, name="VERITAS")
            return None
        if isinstance(e, A.BinOp):
            lt = self._infer(e.l, env)
            rt = self._infer(e.r, env)
            if e.op in ("+", "-", "*", "/", "%"):
                if isinstance(lt, A.TName) and isinstance(rt, A.TName):
                    if lt.name == "SCRIPTUM" and rt.name == "SCRIPTUM" and e.op == "+":
                        return lt
                    if lt.name == "NUMERUS" and rt.name == "NUMERUS":
                        return lt
                    if lt.name == "FRACTIO" or rt.name == "FRACTIO":
                        if lt.name in ("NUMERUS", "FRACTIO") and rt.name in (
                            "NUMERUS",
                            "FRACTIO",
                        ):
                            return A.TName(line=e.line, name="FRACTIO")
            if e.op in ("==", "!=", "<", "<=", ">", ">="):
                return A.TName(line=e.line, name="VERITAS")
            if e.op in ("ET", "VEL"):
                return A.TName(line=e.line, name="VERITAS")
            return None
        if isinstance(e, A.Call):
            ft = None
            if isinstance(e.fn, A.Ident):
                ft = self.rites.get(e.fn.name) or env.get(e.fn.name)
            if ft is None:
                ft = self._infer(e.fn, env)
            if isinstance(ft, A.TRitus):
                if len(e.args) != len(ft.params):
                    self._warn(
                        "C-III",
                        "argumentum_pravum",
                        f"rite expects {len(ft.params)} offerings, got {len(e.args)}",
                        e.line,
                    )
                else:
                    for arg, (_, pt) in zip(e.args, ft.params):
                        got = self._infer(arg, env)
                        if got is not None:
                            self._check_bind(got, pt, e.line, "offering")
                return ft.ret
            for a in e.args:
                self._infer(a, env)
            self._infer(e.fn, env)
            return None
        if isinstance(e, A.Index):
            self._infer(e.obj, env)
            self._infer(e.idx, env)
            if isinstance(e.obj, A.Ident):
                ot = env.get(e.obj.name)
                if isinstance(ot, A.TOrdo):
                    return ot.inner
                if isinstance(ot, A.TTabula):
                    return ot.v
            return None
        if isinstance(e, A.Attr):
            self._infer(e.obj, env)
            return None
        if isinstance(e, A.Str):
            for p in e.parts:
                if p[0] == "e":
                    self._infer(p[1], env)
            return A.TName(line=e.line, name="SCRIPTUM")
        if isinstance(e, A.RiteExpr):
            local = dict(env)
            for n, pt in e.params:
                local[n] = pt
            if e.ret and not _is_nihil_type(e.ret) and not self._all_paths_return(e.body):
                self._warn(
                    "C-II",
                    "reditus_deest",
                    f"anonymous rite may end without REDDO",
                    e.line,
                )
            self._walk_block(e.body, env=local, ret_type=e.ret)
            return _rite_type(e.params, e.ret, e.line)
        if isinstance(e, A.SchemaLit):
            if e.name in self.schemas:
                return A.TName(line=e.line, name=e.name)
            return None
        return None


def check_source(src: str, archivum: str) -> list[Finding]:
    prog = parse_source(src, archivum)
    return _Checker(prog).run()


def censura(target: str | Path) -> list[Finding]:
    root = Path(target).resolve()
    all_hits: list[Finding] = []
    for fp in _collect_vg(root):
        text = fp.read_text(encoding="utf-8")
        all_hits.extend(check_source(text, str(fp)))
    return all_hits
