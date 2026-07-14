"""gothica lustro — linter (docs 12-cli §3)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import arbor as A
from .parser import parse_source


@dataclass
class Lint:
    code: str
    message: str
    line: int
    archivum: str


def _collect_vg(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".vg" else []
    return sorted(path.rglob("*.vg"))


def _const_num(e) -> int | None:
    if isinstance(e, A.Num):
        return e.v
    if isinstance(e, A.Bool):
        return 1 if e.v else 0
    return None


class _LintWalker:
    def __init__(self, prog: A.Program, *, serius: bool = False):
        self.prog = prog
        self.serius = serius
        self.hits: list[Lint] = []

    def run(self) -> list[Lint]:
        if self.prog.mode == "LITANIA":
            for st in self.prog.body:
                if isinstance(st, A.Declare) and not st.sanctum:
                    self._warn(
                        "L-III",
                        f"mutable DECLARO '{st.name}' at LITANIA top level",
                        st.line,
                    )
        self._walk_block(self.prog.body, env={}, shadow=set())
        if self.prog.mode == "FABRICA":
            self._fabrica_rules()
        return self.hits

    def _warn(self, code: str, message: str, line: int) -> None:
        self.hits.append(Lint(code, message, line, self.prog.archivum))

    def _fabrica_rules(self) -> None:
        resources = 0
        for st in self.prog.body:
            if isinstance(st, A.Foedus):
                keys = {a.key for a in st.attrs}
                if "versio_foederis" not in keys:
                    self._warn(
                        "L-IV",
                        f"FOEDUS '{st.name}' has no versio_foederis",
                        st.line,
                    )
            if isinstance(st, A.Exstruatur):
                resources += 1
                if st.species == "custodia":
                    self._check_custodia(st)
            if isinstance(st, A.Sedes):
                pass
        sedes = any(isinstance(st, A.Sedes) for st in self.prog.body)
        if resources > 5 and not sedes:
            self._warn(
                "L-IX",
                f"FABRICA declares {resources} resources but no SEDES",
                self.prog.body[0].line if self.prog.body else 1,
            )

    def _check_custodia(self, st: A.Exstruatur) -> None:
        for attr in st.attrs:
            if attr.key in ("ingress", "ingressus") and isinstance(attr.value, A.Str):
                text = "".join(p[1] for p in attr.value.parts if p[0] == "t")
                if "0.0.0.0/0" in text:
                    self._warn("L-V", "custodia with 0.0.0.0/0 ingress", st.line)

    def _walk_block(self, stmts: list, *, env: dict[str, int], shadow: set[str]) -> None:
        for i, st in enumerate(stmts):
            self._walk_stmt(st, env=env, shadow=shadow, later=stmts[i + 1 :])

    def _walk_stmt(
        self,
        st,
        *,
        env: dict[str, int],
        shadow: set[str],
        later: list | None = None,
    ) -> None:
        later = later or []
        if isinstance(st, A.Declare):
            if st.name in env:
                self._warn("L-II", f"shadowing '{st.name}'", st.line)
            elif st.name in shadow:
                self._warn("L-II", f"shadowing outer '{st.name}'", st.line)
            env[st.name] = st.line
            self._walk_expr(st.expr, env)
        elif isinstance(st, A.RiteDef):
            local = dict(env)
            for n, _ in st.params:
                local[n] = st.line
            self._walk_block(st.body, env=local, shadow=set(env) | shadow)
        elif isinstance(st, A.Assign):
            self._walk_expr(st.target, env)
            self._walk_expr(st.expr, env)
        elif isinstance(st, A.If):
            for cond, body in st.arms:
                self._walk_expr(cond, env)
                self._walk_block(body, env=dict(env), shadow=shadow | set(env))
            if st.els:
                self._walk_block(st.els, env=dict(env), shadow=shadow | set(env))
        elif isinstance(st, A.While):
            self._walk_expr(st.cond, env)
            self._walk_block(st.body, env=dict(env), shadow=shadow)
        elif isinstance(st, A.For):
            child = dict(env)
            child[st.var] = st.line
            self._walk_expr(st.it, env)
            self._walk_block(st.body, env=child, shadow=shadow)
        elif isinstance(st, A.Try):
            self._walk_block(st.body, env=dict(env), shadow=shadow)
            if st.catch:
                child = dict(env)
                if st.catch_var:
                    child[st.catch_var] = st.line
                self._walk_block(st.catch, env=child, shadow=shadow)
            if st.fin:
                self._walk_block(st.fin, env=dict(env), shadow=shadow)
        elif isinstance(st, A.Print):
            self._walk_expr(st.expr, env)
            self._check_io(st)
        elif isinstance(st, A.ExprStmt):
            self._walk_expr(st.expr, env)
        elif isinstance(st, A.Return):
            if st.expr:
                self._walk_expr(st.expr, env)
        elif isinstance(st, A.Raise):
            self._walk_expr(st.expr, env)
        elif isinstance(st, (A.Foedus, A.Sedes, A.Exstruatur, A.Scrutor,
                           A.Postulo, A.Profiteor, A.Import, A.SchemaDef,
                           A.Break, A.Continue)):
            if isinstance(st, A.ExprStmt):
                return
            if hasattr(st, "expr") and st.expr:
                self._walk_expr(st.expr, env)
            for attr in getattr(st, "attrs", []) or []:
                if isinstance(attr.value, list):
                    for sub in attr.value:
                        self._walk_expr(sub.value, env)
                else:
                    self._walk_expr(attr.value, env)
            if isinstance(st, A.Exstruatur):
                self._walk_expr(st.name_expr, env)

        self._check_unused_decl(st, env, later)

    def _name_used_in_stmts(self, name: str, stmts: list) -> bool:
        for s in stmts:
            if self._stmt_refs(s, name):
                return True
        return False

    def _stmt_refs(self, st, name: str) -> bool:
        if isinstance(st, A.Declare):
            return self._expr_uses(st.expr, name)
        if isinstance(st, A.Assign):
            return self._expr_uses(st.target, name) or self._expr_uses(st.expr, name)
        if isinstance(st, A.Print):
            return self._expr_uses(st.expr, name)
        if isinstance(st, A.ExprStmt):
            return self._expr_uses(st.expr, name)
        if isinstance(st, A.Return) and st.expr:
            return self._expr_uses(st.expr, name)
        if isinstance(st, A.If):
            return any(
                self._expr_uses(c, name) or self._name_used_in_stmts(name, b)
                for c, b in st.arms
            ) or (st.els and self._name_used_in_stmts(name, st.els))
        if isinstance(st, A.For):
            return self._expr_uses(st.it, name) or self._name_used_in_stmts(name, st.body)
        if isinstance(st, A.While):
            return self._expr_uses(st.cond, name) or self._name_used_in_stmts(name, st.body)
        return False

    def _check_unused_decl(self, st, env: dict[str, int], later: list) -> None:
        if not isinstance(st, A.Declare):
            return
        if st.name.startswith("_"):
            return
        used = self._expr_uses(st.expr, st.name)
        if not used:
            used = self._name_used_in_stmts(st.name, later)
        if not used and not st.sanctum:
            self._warn("L-I", f"unused binding '{st.name}'", st.line)

    def _expr_uses(self, e, name: str) -> bool:
        if e is None:
            return False
        if isinstance(e, A.Ident):
            return e.name == name
        if isinstance(e, A.BinOp):
            return self._expr_uses(e.l, name) or self._expr_uses(e.r, name)
        if isinstance(e, A.UnOp):
            return self._expr_uses(e.e, name)
        if isinstance(e, A.Call):
            return self._expr_uses(e.fn, name) or any(
                self._expr_uses(a, name) for a in e.args
            )
        if isinstance(e, A.Index):
            return self._expr_uses(e.obj, name) or self._expr_uses(e.idx, name)
        if isinstance(e, A.Attr):
            return self._expr_uses(e.obj, name)
        if isinstance(e, A.ListLit):
            return any(self._expr_uses(x, name) for x in e.items)
        if isinstance(e, A.MapLit):
            return any(
                self._expr_uses(k, name) or self._expr_uses(v, name)
                for k, v in e.entries
            )
        if isinstance(e, A.Str):
            return any(
                p[0] == "e" and self._expr_uses(p[1], name) for p in e.parts
            )
        return False

    def _walk_expr(self, e, env: dict[str, int]) -> None:
        if e is None:
            return
        if isinstance(e, A.BinOp):
            if e.op == "/":
                denom = _const_num(e.r)
                if denom == 0:
                    self._warn(
                        "L-VIII",
                        "constant division by N — guaranteed divisio_nihili",
                        e.line,
                    )
            self._walk_expr(e.l, env)
            self._walk_expr(e.r, env)
        elif isinstance(e, A.UnOp):
            self._walk_expr(e.e, env)
        elif isinstance(e, A.Call):
            self._walk_expr(e.fn, env)
            for a in e.args:
                self._walk_expr(a, env)
            self._check_call(e)
        elif isinstance(e, A.Index):
            self._walk_expr(e.obj, env)
            self._walk_expr(e.idx, env)
        elif isinstance(e, A.Attr):
            self._walk_expr(e.obj, env)
        elif isinstance(e, A.ListLit):
            for x in e.items:
                self._walk_expr(x, env)
        elif isinstance(e, A.MapLit):
            for k, v in e.entries:
                self._walk_expr(k, env)
                self._walk_expr(v, env)
        elif isinstance(e, A.Str):
            for p in e.parts:
                if p[0] == "e":
                    self._walk_expr(p[1], env)
        elif isinstance(e, A.RiteExpr):
            for s in e.body:
                self._walk_stmt(s, env=dict(env), shadow=set(), later=[])

    def _check_io(self, st: A.Print) -> None:
        if self.prog.mode != "FABRICA":
            return
        if isinstance(st.expr, A.Call) and isinstance(st.expr.fn, A.Attr):
            if st.expr.fn.name in ("pete", "pete_plene", "mitte"):
                self._warn(
                    "L-VI",
                    "network read in FABRICA (machina_cogitans)",
                    st.line,
                )

    def _check_call(self, call: A.Call) -> None:
        if not self.serius:
            return
        if isinstance(call.fn, A.Ident) and call.fn.name == "elige":
            if len(call.args) == 3:
                self._warn(
                    "L-X",
                    "elige evaluates both branches — avoid effectful arguments",
                    call.line,
                )


def lint_source(src: str, archivum: str, *, serius: bool = False) -> list[Lint]:
    prog = parse_source(src, archivum)
    return _LintWalker(prog, serius=serius).run()


def lustro(
    target: str | Path,
    *,
    serius: bool = False,
) -> list[Lint]:
    root = Path(target).resolve()
    all_hits: list[Lint] = []
    for fp in _collect_vg(root):
        text = fp.read_text(encoding="utf-8")
        all_hits.extend(lint_source(text, str(fp), serius=serius))
    return all_hits
