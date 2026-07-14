"""Tree-walking interpreter."""
from __future__ import annotations
import os
import sys
from . import arbor as A
from .heresiae import Heresis, Profanatio
from .valores import (Cell, Env, Rite, NativeRite, SchemaType, Instance,
                      Module, HeresyValue, Relatio, RelatioRoot, scriptum,
                      genus_valoris, INT64_MIN, INT64_MAX)
from . import cultus
from .parser import parse_source, SPECIES
from . import typi as T


class BreakSig(Exception):
    pass


class ContinueSig(Exception):
    pass


class ReturnSig(Exception):
    def __init__(self, value):
        self.value = value


MAX_DEPTH_DEFAULT = 4000


class Interpres:
    def __init__(self, argv=None, mode="CANTICUM", max_depth=MAX_DEPTH_DEFAULT,
                 root_dir="."):
        self.argv = argv or []
        self.mode = mode
        self.max_depth = max_depth
        self.depth = 0
        self.stack: list[str] = []
        self.root_dir = root_dir
        self.modules: dict[str, Module] = {}
        self.loading: list[str] = []
        self.fabrica = None          # FabricaState, set by fabrica driver
        self.cur_file = "?"

    # ------------- heresy helpers -------------
    def h(self, genus, msg, node=None, gradus=0, major=False):
        e = Heresis(genus, msg, versus=getattr(node, "line", 0),
                    archivum=self.cur_file, gradus=gradus, major=major)
        e.vestigium = list(reversed(self.stack)) or ["<top>"]
        return e

    # ------------- program execution -------------
    def run_program(self, prog: A.Program):
        self.cur_file = prog.archivum
        env = Env()
        self._hoist(prog.body, env)
        for st in prog.body:
            self.exec_stmt(st, env)
        # principium entry point
        cell = env.lookup("principium")
        if prog.mode == "CANTICUM" and cell and isinstance(cell.value, Rite):
            r = self.call_value(cell.value, [])
            if isinstance(r, int) and not isinstance(r, bool):
                sys.exit(r)
        return env

    def _hoist(self, body, env):
        for st in body:
            if isinstance(st, A.RiteDef):
                env.vars[st.name] = Cell(None, sanctum=True)
            if isinstance(st, A.SchemaDef):
                env.vars[st.name] = Cell(None, sanctum=True)

    # ------------- statements -------------
    def exec_block(self, block, env):
        inner = Env(env)
        for st in block:
            self.exec_stmt(st, inner)

    def exec_stmt(self, st, env):
        m = getattr(self, "st_" + type(st).__name__, None)
        if m is None:
            raise self.h("machina_corrupta",
                         f"no executor for {type(st).__name__}", st, major=True)
        return m(st, env)

    def st_Declare(self, st: A.Declare, env):
        v = self.eval(st.expr, env)
        self.check_type(v, st.type, st, f"vessel '{st.name}'")
        if st.name in env.vars:
            raise Profanatio("P-XI", "declaratio_geminata",
                             f"'{st.name}' already declared in this scope.",
                             self.cur_file, st.line)
        env.vars[st.name] = Cell(v, st.sanctum)

    def st_Assign(self, st: A.Assign, env):
        v = self.eval(st.expr, env)
        t = st.target
        if isinstance(t, A.Ident):
            cell = env.lookup(t.name)
            if cell is None:
                raise self.h("vas_ignotum", f"unknown vessel '{t.name}'", st)
            if cell.sanctum:
                raise self.h("sanctum_violatum",
                             f"'{t.name}' is consecrated and shall not change", st)
            cell.value = v
        elif isinstance(t, A.Index):
            obj = self.eval(t.obj, env)
            idx = self.eval(t.idx, env)
            if isinstance(obj, list):
                i = self._index_int(idx, len(obj), st)
                obj[i] = v
            elif isinstance(obj, dict):
                obj[idx] = v
            else:
                raise self.h("typus_profanus",
                             f"cannot index {genus_valoris(obj)}", st)
        elif isinstance(t, A.Attr):
            obj = self.eval(t.obj, env)
            if isinstance(obj, Instance):
                if t.name not in obj.values:
                    raise self.h("campus_ignotus",
                                 f"schema {obj.schema.name} has no field "
                                 f"'{t.name}'", st)
                for fn, ft, _d in obj.schema.fields:
                    if fn == t.name:
                        self.check_type(v, ft, st, f"field '{t.name}'",
                                        allow_nihil=(_d is not None))
                obj.values[t.name] = v
            else:
                raise self.h("typus_profanus",
                             f"{genus_valoris(obj)} has no fields to set", st)

    def st_If(self, st: A.If, env):
        for cond, body in st.arms:
            c = self.eval(cond, env)
            self._need_bool(c, cond)
            if c:
                self.exec_block(body, env)
                return
        if st.els is not None:
            self.exec_block(st.els, env)

    def st_While(self, st: A.While, env):
        while True:
            c = self.eval(st.cond, env)
            self._need_bool(c, st.cond)
            if not c:
                return
            try:
                self.exec_block(st.body, env)
            except BreakSig:
                return
            except ContinueSig:
                continue

    def st_For(self, st: A.For, env):
        it = self.eval(st.it, env)
        if isinstance(it, dict):
            seq = list(it.keys())
            watched, wlen = it, len(it)
        elif isinstance(it, list):
            seq = it
            watched, wlen = it, len(it)
        elif isinstance(it, str):
            seq = list(it)
            watched, wlen = None, 0
        else:
            raise self.h("typus_profanus",
                         f"cannot iterate {genus_valoris(it)}", st)
        i = 0
        n = len(seq)
        while i < n:
            if watched is not None and len(watched) != wlen:
                raise self.h("mutatio_in_processione",
                             "the procession was disturbed by mutation", st)
            inner = Env(env)
            inner.vars[st.var] = Cell(seq[i], sanctum=True)
            try:
                self.exec_block(st.body, inner)
            except BreakSig:
                return
            except ContinueSig:
                pass
            i += 1

    def st_Try(self, st: A.Try, env):
        pending = None
        result_flow = None
        try:
            self.exec_block(st.body, env)
        except Heresis as h1:
            if h1.major:
                pending = h1
            elif st.catch is not None:
                inner = Env(env)
                inner.vars[st.catch_var] = Cell(HeresyValue(h1), sanctum=True)
                try:
                    self.exec_block(st.catch, inner)
                except Heresis as h2:
                    h2.origo = h2.origo or h1
                    pending = h2
                except (BreakSig, ContinueSig, ReturnSig) as f:
                    result_flow = f
            else:
                pending = h1
        except (BreakSig, ContinueSig, ReturnSig) as f:
            result_flow = f
        # DENIQUE always runs
        if st.fin is not None:
            try:
                self.exec_block(st.fin, env)
            except Heresis as h3:
                h3.origo = h3.origo or pending
                raise h3
        if pending is not None:
            raise pending
        if result_flow is not None:
            raise result_flow

    def st_Print(self, st: A.Print, env):
        v = self.eval(st.expr, env)
        print(scriptum(v), file=sys.stderr if st.err else sys.stdout)

    def st_Return(self, st: A.Return, env):
        v = self.eval(st.expr, env) if st.expr is not None else None
        raise ReturnSig(v)

    def st_Raise(self, st: A.Raise, env):
        v = self.eval(st.expr, env)
        if isinstance(v, HeresyValue):
            raise v.h
        genus = st.genus or "heresis_declarata"
        raise self.h(genus, scriptum(v), st)

    def st_Break(self, st, env):
        raise BreakSig()

    def st_Continue(self, st, env):
        raise ContinueSig()

    def st_ExprStmt(self, st: A.ExprStmt, env):
        self.eval(st.expr, env)

    def st_RiteDef(self, st: A.RiteDef, env):
        rite = Rite(st.name, st.params, st.ret, st.body, env, self.cur_file)
        cell = env.vars.get(st.name)
        if cell is not None and cell.value is None:
            cell.value = rite          # hoisted slot
        else:
            env.declare(st.name, rite, sanctum=True, line=st.line,
                        archivum=self.cur_file)

    def st_SchemaDef(self, st: A.SchemaDef, env):
        sch = SchemaType(st.name, st.fields, self.cur_file)
        cell = env.vars.get(st.name)
        if cell is not None and cell.value is None:
            cell.value = sch
        else:
            env.declare(st.name, sch, sanctum=True, line=st.line,
                        archivum=self.cur_file)

    def st_Import(self, st: A.Import, env):
        mod = self.load_module(st.path, st)
        if st.names:
            for n in st.names:
                if n not in mod.exports:
                    raise Profanatio("P-XVII", "nomen_non_exportatum",
                                     f"'{st.path}' does not export '{n}'.",
                                     self.cur_file, st.line)
                env.declare(n, mod.exports[n], sanctum=True, line=st.line,
                            archivum=self.cur_file)
        else:
            binding = st.alias or st.path.split("/")[-1]
            env.declare(binding, mod, sanctum=True, line=st.line,
                        archivum=self.cur_file)

    # infra statements — delegated to fabrica driver
    def st_Foedus(self, st, env):
        self._fab().foedus(self, st, env)

    def st_Sedes(self, st, env):
        self._fab().sedes(self, st, env)

    def st_Exstruatur(self, st, env):
        self._fab().exstruatur(self, st, env)

    def st_Scrutor(self, st, env):
        self._fab().scrutor(self, st, env)

    def st_Postulo(self, st, env):
        self._fab().postulo(self, st, env)

    def st_Profiteor(self, st, env):
        self._fab().profiteor(self, st, env)

    def _fab(self):
        if self.fabrica is None:
            raise self.h("fabrica_in_cantico",
                         "resources may not be raised in a CANTICUM",
                         major=True)
        return self.fabrica

    # ------------- module loading -------------
    def load_module(self, path: str, node) -> Module:
        if path in self.modules:
            return self.modules[path]
        if path in self.loading:
            cyc = " -> ".join(self.loading + [path])
            raise self.h("circulus_impius", f"impious import cycle: {cyc}",
                         node, major=True)
        std = cultus.stdlib_module(path, self)
        if std is not None:
            self.modules[path] = std
            return std
        # project / litaniae file
        candidates = [
            os.path.join(self.root_dir, path + ".vg"),
            os.path.join(self.root_dir, "litaniae", path, "fons",
                         path.split("/")[-1] + ".vg"),
        ]
        via = next((c for c in candidates if os.path.exists(c)), None)
        if via is None:
            raise Profanatio("P-XVIII", "invocatio_vana",
                             f"the invocation of '{path}' went unanswered.",
                             self.cur_file, getattr(node, "line", 0))
        self.loading.append(path)
        prev_file = self.cur_file
        try:
            with open(via, encoding="utf-8") as f:
                src = f.read()
            prog = parse_source(src, via)
            if prog.mode != "LITANIA":
                raise Profanatio("P-XVI", "modus_pravus",
                                 f"only a LITANIA may be invoked "
                                 f"('{path}' is a {prog.mode}).",
                                 self.cur_file, getattr(node, "line", 0))
            self.cur_file = via
            env = Env()
            self._hoist(prog.body, env)
            for stx in prog.body:
                self.exec_stmt(stx, env)
            exports = {k: c.value for k, c in env.vars.items()
                       if not k.startswith("_")}
            mod = Module(prog.name, exports)
            self.modules[path] = mod
            return mod
        finally:
            self.cur_file = prev_file
            self.loading.pop()

    # ------------- expressions -------------
    def eval(self, e, env):
        m = getattr(self, "ev_" + type(e).__name__, None)
        if m is None:
            raise self.h("machina_corrupta",
                         f"no evaluator for {type(e).__name__}", e, major=True)
        return m(e, env)

    def ev_Num(self, e, env):
        return e.v

    def ev_Flo(self, e, env):
        return e.v

    def ev_Bool(self, e, env):
        return e.v

    def ev_Nihil(self, e, env):
        return None

    def ev_Str(self, e: A.Str, env):
        out = []
        for kind, val in e.parts:
            if kind == "t":
                out.append(val)
            else:
                v = self.eval(val, env)
                out.append(scriptum(v))
        return "".join(out)

    def ev_Ident(self, e: A.Ident, env):
        if e.name == "__ausculto__":
            return NativeRite("AUSCULTO", self._ausculto)
        cell = env.lookup(e.name)
        if cell is not None:
            return cell.value
        if e.name in cultus.BUILTINS:
            return NativeRite(e.name, cultus.BUILTINS[e.name])
        if self.fabrica is not None:
            if e.name in SPECIES:
                return RelatioRoot("resource")
            if e.name == "scrutinium":
                return RelatioRoot("data")
        raise self.h("vas_ignotum", f"unknown vessel '{e.name}'", e)

    def _ausculto(self):
        try:
            return input()
        except EOFError:
            raise Heresis("auscultatio_vana", "the listening was in vain")

    def ev_ListLit(self, e, env):
        return [self.eval(x, env) for x in e.items]

    def ev_MapLit(self, e, env):
        out = {}
        for k, v in e.entries:
            out[self.eval(k, env)] = self.eval(v, env)
        return out

    def ev_SchemaLit(self, e: A.SchemaLit, env):
        cell = env.lookup(e.name)
        sch = cell.value if cell else None
        if not isinstance(sch, SchemaType):
            raise Profanatio("P-XV", "typus_ignotus",
                             f"unknown schema '{e.name}'.",
                             self.cur_file, e.line)
        given = {}
        for fn, fe in e.fields:
            if fn not in [f[0] for f in sch.fields]:
                raise self.h("campus_ignotus",
                             f"schema {sch.name} has no field '{fn}'", e)
            given[fn] = self.eval(fe, env)
        values = {}
        for fn, ft, fd in sch.fields:
            if fn in given:
                self.check_type(given[fn], ft, e, f"field '{fn}'",
                                allow_nihil=(fd is not None))
                values[fn] = given[fn]
            elif fd is not None:
                values[fn] = self.eval(fd, env)
            else:
                raise self.h("campus_deest",
                             f"field '{fn}' of {sch.name} is mandatory", e)
        return Instance(sch, values)

    def ev_RiteExpr(self, e: A.RiteExpr, env):
        return Rite(e.name, e.params, e.ret, e.body, env, self.cur_file)

    def ev_UnOp(self, e: A.UnOp, env):
        v = self.eval(e.e, env)
        if e.op == "-":
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise self.h("typus_profanus",
                             f"cannot negate {genus_valoris(v)}", e)
            r = -v
            if isinstance(r, int) and not (INT64_MIN <= r <= INT64_MAX):
                raise self.h("excessus_numeri", "NUMERUS overflow", e)
            return r
        if e.op == "NON":
            self._need_bool(v, e)
            return not v

    def ev_BinOp(self, e: A.BinOp, env):
        op = e.op
        if op in ("ET", "VEL"):
            l = self.eval(e.l, env)
            self._need_bool(l, e.l)
            if op == "ET" and not l:
                return False
            if op == "VEL" and l:
                return True
            r = self.eval(e.r, env)
            self._need_bool(r, e.r)
            return r
        l = self.eval(e.l, env)
        r = self.eval(e.r, env)
        if isinstance(l, (Relatio, RelatioRoot)) or isinstance(r, (Relatio, RelatioRoot)):
            raise self.h("relatio_differata_tacta",
                         "thou hast touched that which is not yet made flesh",
                         e, major=True)
        if op == "==":
            return self._eq(l, r)
        if op == "!=":
            return not self._eq(l, r)
        if op in ("<", "<=", ">", ">="):
            return self._cmp(l, r, op, e)
        return self._arith(l, r, op, e)

    def _eq(self, l, r):
        if isinstance(l, bool) != isinstance(r, bool):
            return False
        if isinstance(l, Instance) and isinstance(r, Instance):
            return (l.schema is r.schema and
                    all(self._eq(l.values[k], r.values[k]) for k in l.values))
        if isinstance(l, (Rite, NativeRite)) or isinstance(r, (Rite, NativeRite)):
            return l is r
        if type(l) is not type(r) and not (
                isinstance(l, (int, float)) and isinstance(r, (int, float))):
            return False
        try:
            return l == r
        except Exception:
            return False

    def _cmp(self, l, r, op, node):
        num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
        if (num(l) and num(r)) or (isinstance(l, str) and isinstance(r, str)):
            return {"<": l < r, "<=": l <= r, ">": l > r, ">=": l >= r}[op]
        raise self.h("typus_profanus",
                     f"cannot order {genus_valoris(l)} against "
                     f"{genus_valoris(r)}", node)

    def _arith(self, l, r, op, node):
        if l is None or r is None:
            raise self.h("nihil_tactum", "operation upon NIHIL", node)
        num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
        if op == "+":
            if isinstance(l, str) and isinstance(r, str):
                return l + r
            if isinstance(l, list) and isinstance(r, list):
                return l + r
        if not (num(l) and num(r)):
            raise self.h("typus_profanus",
                         f"'{op}' upon {genus_valoris(l)} and "
                         f"{genus_valoris(r)}", node)
        both_int = isinstance(l, int) and isinstance(r, int)
        if op == "+":
            res = l + r
        elif op == "-":
            res = l - r
        elif op == "*":
            res = l * r
        elif op == "/":
            if both_int:
                if r == 0:
                    raise self.h("divisio_nihili",
                                 "the cogitator was commanded to divide by naught",
                                 node)
                q = abs(l) // abs(r)
                res = q if (l >= 0) == (r >= 0) else -q
            else:
                try:
                    res = l / r
                except ZeroDivisionError:
                    res = float("inf") if l > 0 else (float("-inf") if l < 0
                                                      else float("nan"))
        elif op == "%":
            if both_int:
                if r == 0:
                    raise self.h("divisio_nihili", "modulo by naught", node)
                q = abs(l) // abs(r)
                q = q if (l >= 0) == (r >= 0) else -q
                res = l - q * r
            else:
                import math
                res = math.fmod(l, r)
        else:
            raise self.h("machina_corrupta", f"op {op}", node, major=True)
        if both_int and not (INT64_MIN <= res <= INT64_MAX):
            raise self.h("excessus_numeri", "NUMERUS overflow", node)
        return res

    def ev_Index(self, e: A.Index, env):
        obj = self.eval(e.obj, env)
        idx = self.eval(e.idx, env)
        if obj is None:
            raise self.h("nihil_tactum", "indexing NIHIL", e)
        if isinstance(obj, (list, str)):
            i = self._index_int(idx, len(obj), e)
            return obj[i]
        if isinstance(obj, dict):
            if idx not in obj:
                raise self.h("clavis_ignota",
                             f"no key {scriptum(idx)} in the tabula", e)
            return obj[idx]
        raise self.h("typus_profanus",
                     f"cannot index {genus_valoris(obj)}", e)

    def _index_int(self, idx, n, node):
        if isinstance(idx, bool) or not isinstance(idx, int):
            raise self.h("typus_profanus", "index must be NUMERUS", node)
        if not (0 <= idx < n):
            raise self.h("index_extra_fines",
                         f"index {idx} beyond bounds [0, {n})", node,
                         gradus=idx)
        return idx

    def ev_Attr(self, e: A.Attr, env):
        obj = self.eval(e.obj, env)
        if obj is None:
            raise self.h("nihil_tactum", "field access upon NIHIL", e)
        if isinstance(obj, Instance):
            if e.name not in obj.values:
                raise self.h("campus_ignotus",
                             f"schema {obj.schema.name} has no field "
                             f"'{e.name}'", e)
            return obj.values[e.name]
        if isinstance(obj, Module):
            if e.name not in obj.exports:
                raise self.h("vas_ignotum",
                             f"litania '{obj.name}' holds no '{e.name}'", e)
            return obj.exports[e.name]
        if isinstance(obj, HeresyValue):
            f = obj.fields
            if e.name not in f:
                raise self.h("campus_ignotus", f"HERESIS has no '{e.name}'", e)
            return f[e.name]
        if isinstance(obj, RelatioRoot):
            return Relatio(obj.kind, e.name)
        if isinstance(obj, Relatio):
            return obj.extend(e.name)
        raise self.h("typus_profanus",
                     f"{genus_valoris(obj)} has no fields", e)

    def ev_Call(self, e: A.Call, env):
        fn = self.eval(e.fn, env)
        args = [self.eval(a, env) for a in e.args]
        return self.call_value(fn, args, node=e)

    def call_value(self, fn, args, node=None):
        if isinstance(fn, NativeRite):
            try:
                return fn.fn(*args)
            except TypeError as te:
                if "positional argument" in str(te):
                    raise self.h("argumentum_pravum",
                                 f"{fn.name}: wrong offering count", node)
                raise
        if isinstance(fn, SchemaType):
            raise self.h("typus_profanus",
                         f"instantiate with {fn.name}{{...}} braces", node)
        if not isinstance(fn, Rite):
            raise self.h("typus_profanus",
                         f"{genus_valoris(fn)} is not callable", node)
        if len(args) != len(fn.params):
            raise self.h("argumentum_pravum",
                         f"rite {fn.name} demands {len(fn.params)} offerings, "
                         f"received {len(args)}", node)
        if self.depth >= self.max_depth:
            raise self.h("profunditas_excessa",
                         f"recursion beyond {self.max_depth} frames", node)
        call_env = Env(fn.env)
        for (pn, pt), av in zip(fn.params, args):
            self.check_type(av, pt, node, f"offering '{pn}' of {fn.name}")
            call_env.vars[pn] = Cell(av)
        self.depth += 1
        from .lexicon import int_to_roman
        ln = getattr(node, "line", 0) or 0
        ver = int_to_roman(ln) if 0 <= ln <= 3999 else str(ln)
        self.stack.append(f"ritus {fn.name} — VERSUS {ver}")
        try:
            for st in fn.body:
                self.exec_stmt(st, call_env)
        except ReturnSig as r:
            self.check_type(r.value, fn.ret, node, f"gift of {fn.name}",
                            allow_nihil=True if self._is_nihil_type(fn.ret)
                            else False)
            return r.value
        finally:
            self.depth -= 1
            self.stack.pop()
        if self._is_nihil_type(fn.ret):
            return None
        raise self.h("reditus_deest",
                     f"rite {fn.name} ended without REDDO", node)

    def _is_nihil_type(self, t):
        return isinstance(t, A.TName) and t.name == "NIHIL"

    # ------------- type checking -------------
    def check_type(self, v, t, node, what, allow_nihil=False):
        if t is None:
            return
        if not self._conforms(v, t, node, allow_nihil):
            raise self.h("typus_profanus",
                         f"attempted to bind {genus_valoris(v)} to {what} "
                         f"consecrated for {self._tname(t)}", node)

    def _tname(self, t):
        return T.tname(t)

    def _type_ast_eq(self, a, b) -> bool:
        return T.type_eq(a, b)

    def _rite_matches_type(self, rite: Rite, t: A.TRitus) -> bool:
        if len(rite.params) != len(t.params):
            return False
        for (_, pt), (_, tt) in zip(rite.params, t.params):
            if not self._type_ast_eq(pt, tt):
                return False
        return self._type_ast_eq(rite.ret, t.ret)

    def _conforms(self, v, t, node, allow_nihil=False):
        if isinstance(t, A.TRitus):
            if not isinstance(v, Rite):
                return False
            return self._rite_matches_type(v, t)
        if isinstance(v, (Relatio, RelatioRoot)):
            if isinstance(t, A.TName) and t.name in ("SCRIPTUM", "RELATIO"):
                return True
            return False
        if isinstance(t, A.TName):
            n = t.name
            if n == "NUMERUS":
                return isinstance(v, int) and not isinstance(v, bool)
            if n == "FRACTIO":
                return isinstance(v, float)
            if n == "SCRIPTUM":
                return isinstance(v, str)
            if n == "VERITAS":
                return isinstance(v, bool)
            if n == "NIHIL":
                return v is None
            if n == "RITUS":
                return isinstance(v, (Rite, NativeRite))
            if n == "RELATIO":
                return isinstance(v, (Relatio, RelatioRoot))
            if n == "HERESIS":
                return isinstance(v, HeresyValue)
            # schema
            if v is None and allow_nihil:
                return True
            return isinstance(v, Instance) and v.schema.name == n
        if isinstance(t, A.TOrdo):
            return isinstance(v, list) and all(
                self._conforms(x, t.inner, node) for x in v)
        if isinstance(t, A.TTabula):
            return isinstance(v, dict) and all(
                self._conforms(k, t.k, node) and self._conforms(x, t.v, node)
                for k, x in v.items())
        return False

    def _need_bool(self, v, node):
        if not isinstance(v, bool):
            raise self.h("typus_profanus",
                         "a condition must be VERITAS — there is no truthiness "
                         "in the sight of the Machine God", node)
