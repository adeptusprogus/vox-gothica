"""Recursive-descent parser. Grammar: docs 11-grammar.md."""
from __future__ import annotations
from . import arbor as A
from .heresiae import Profanatio
from .lexicon import Lexer, Tok, StrPart

PRIMITIVES = {"NUMERUS", "FRACTIO", "SCRIPTUM", "VERITAS", "NIHIL",
              "RITUS", "HERESIS", "RELATIO"}
SPECIES = {"machina", "retiaculum", "horreum", "custodia", "nuntius",
           "codex", "res"}


class Parser:
    def __init__(self, toks: list[Tok], archivum: str = "?"):
        self.toks = toks
        self.p = 0
        self.archivum = archivum

    # ---------- helpers ----------
    def peek(self, k=0) -> Tok:
        return self.toks[min(self.p + k, len(self.toks) - 1)]

    def next(self) -> Tok:
        t = self.toks[self.p]
        if t.kind != "EOF":
            self.p += 1
        return t

    def at_kw(self, *kws) -> bool:
        t = self.peek()
        return t.kind == "KW" and t.value in kws

    def at_op(self, op) -> bool:
        t = self.peek()
        return t.kind == "OP" and t.value == op

    def err(self, msg, line=None, code="P-XIV", genus="syntaxis_profana"):
        raise Profanatio(code, genus, msg, self.archivum,
                         line or self.peek().line)

    def expect_kw(self, kw) -> Tok:
        t = self.next()
        if t.kind != "KW" or t.value != kw:
            self.err(f"Expected {kw}; the litany is unfinished (found {t.value!r}).",
                     t.line)
        return t

    def expect_op(self, op) -> Tok:
        t = self.next()
        if t.kind != "OP" or t.value != op:
            self.err(f"Expected '{op}' (found {t.value!r}).", t.line)
        return t

    def expect_ident(self) -> str:
        t = self.next()
        if t.kind != "IDENT":
            self.err(f"Expected an identifier (found {t.value!r}).", t.line)
        return t.value

    def expect_nl(self):
        t = self.next()
        if t.kind not in ("NL", "EOF"):
            self.err(f"One line, one utterance (unexpected {t.value!r}).",
                     t.line, "P-VIII", "sermones_confusi")

    def skip_nls(self):
        while self.peek().kind == "NL":
            self.next()

    def expect_string_literal(self) -> tuple[list, int]:
        t = self.next()
        if t.kind != "STRING":
            self.err("Expected a quoted string.", t.line)
        return t.value, t.line

    def plain_string(self) -> str:
        parts, line = self.expect_string_literal()
        if any(p.kind == "e" for p in parts):
            self.err("Interpolation not allowed here.", line)
        return "".join(p.value for p in parts)

    # ---------- entry ----------
    def parse_program(self) -> A.Program:
        self.skip_nls()
        if self.at_kw("AVE"):
            self.next()
            self.expect_kw("OMNISSIAH")
            self.expect_op(".")
            self.expect_nl()
            self.skip_nls()
        if not self.at_kw("CANTICUM", "FABRICA", "LITANIA"):
            self.err("This scroll bears no seal — declare CANTICUM, FABRICA or LITANIA.",
                     self.peek().line, "P-I", "sigillum_deest")
        mode = self.next().value
        name = self.plain_string()
        self.expect_op(".")
        self.expect_nl()
        body = []
        self.skip_nls()
        while self.peek().kind != "EOF":
            body.append(self.statement(top=True))
            self.skip_nls()
        prog = A.Program(mode=mode, name=name, body=body, archivum=self.archivum)
        self._check_mode(prog)
        return prog

    def _check_mode(self, prog: A.Program):
        infra = (A.Foedus, A.Sedes, A.Exstruatur, A.Scrutor, A.Postulo, A.Profiteor)
        for st in prog.body:
            if prog.mode != "FABRICA" and isinstance(st, infra):
                self.err("Infrastructure liturgy outside a FABRICA.",
                         st.line, "P-XVI", "modus_pravus")
            if prog.mode == "LITANIA" and not isinstance(
                    st, (A.Declare, A.RiteDef, A.SchemaDef, A.Import)):
                self.err("A LITANIA holds only declarations.",
                         st.line, "P-XVI", "modus_pravus")

    # ---------- statements ----------
    def statement(self, top=False, in_loop=False, in_rite=False):
        t = self.peek()
        if t.kind == "KW":
            kw = t.value
            if kw in ("DECLARO", "SANCTUM"):
                return self.declare_or_sanctum_rite(in_rite)
            if kw == "RITUS":
                if not (top or in_rite):
                    self.err("A rite may not hide inside a block.",
                             t.line, "P-XIII", "ritus_absconditus")
                return self.rite_def()
            if kw == "SCHEMA":
                if not top:
                    self.err("SCHEMA only at top level.", t.line,
                             "P-XIII", "ritus_absconditus")
                return self.schema_def()
            if kw == "SI":
                return self.if_stmt(in_loop, in_rite)
            if kw == "DUM":
                return self.while_stmt(in_rite)
            if kw == "PRO":
                return self.for_stmt(in_rite)
            if kw == "TEMPTA":
                return self.try_stmt(in_loop, in_rite)
            if kw in ("VOCIFERO", "SUSURRO"):
                self.next()
                e = self.expr()
                self.expect_nl()
                return A.Print(line=t.line, err=(kw == "SUSURRO"), expr=e)
            if kw == "REDDO":
                self.next()
                e = None
                if self.peek().kind not in ("NL", "EOF"):
                    e = self.expr()
                self.expect_nl()
                return A.Return(line=t.line, expr=e)
            if kw == "PROCLAMO":
                self.next()
                self.expect_kw("HERESIM")
                e = self.expr()
                genus = None
                if self.at_kw("GENERIS"):
                    self.next()
                    genus = self.plain_string()
                self.expect_nl()
                return A.Raise(line=t.line, expr=e, genus=genus)
            if kw == "RUMPO":
                self.next()
                self.expect_nl()
                if not in_loop:
                    self.err("RUMPO outside a loop.", t.line,
                             "P-XII", "ruptura_vaga")
                return A.Break(line=t.line)
            if kw == "PERGO":
                self.next()
                self.expect_nl()
                if not in_loop:
                    self.err("PERGO outside a loop.", t.line,
                             "P-XII", "ruptura_vaga")
                return A.Continue(line=t.line)
            if kw == "INVOCO":
                return self.import_stmt()
            if kw == "FOEDUS":
                return self.foedus()
            if kw == "SEDES":
                return self.sedes()
            if kw == "EXSTRUATUR":
                return self.exstruatur()
            if kw == "SCRUTOR":
                return self.scrutor()
            if kw == "POSTULO":
                return self.postulo()
            if kw == "PROFITEOR":
                return self.profiteor()
            if kw == "PALAM":
                self.next()
                return self.statement(top=top, in_loop=in_loop, in_rite=in_rite)
        # expression statement or assignment
        e = self.expr()
        if self.at_kw("FIAT"):
            self.next()
            rhs = self.expr()
            self.expect_nl()
            if not isinstance(e, (A.Ident, A.Index, A.Attr)):
                self.err("Invalid vessel for assignment.", t.line,
                         "P-X", "receptaculum_pravum")
            return A.Assign(line=t.line, target=e, expr=rhs)
        self.expect_nl()
        return A.ExprStmt(line=t.line, expr=e)

    def declare_or_sanctum_rite(self, in_rite):
        t = self.next()      # DECLARO | SANCTUM
        if t.value == "SANCTUM" and self.at_kw("RITUS"):
            rd = self.rite_def()
            rd.sanctum = True
            return rd
        name = self.expect_ident()
        self.expect_op(":")
        ty = self.type_expr()
        self.expect_op("=")
        e = self.expr()
        self.expect_nl()
        return A.Declare(line=t.line, name=name, type=ty, expr=e,
                         sanctum=(t.value == "SANCTUM"))

    def block(self, enders: set[str], in_loop=False, in_rite=False) -> list:
        out = []
        self.skip_nls()
        while not (self.peek().kind == "KW" and self.peek().value in enders):
            if self.peek().kind == "EOF":
                self.err("The litany is unfinished — missing FINIS.",
                         self.peek().line)
            out.append(self.statement(in_loop=in_loop, in_rite=in_rite))
            self.skip_nls()
        return out

    def finis(self, kw):
        self.expect_kw("FINIS")
        self.expect_kw(kw)
        self.expect_nl()

    def if_stmt(self, in_loop, in_rite):
        t = self.expect_kw("SI")
        arms = []
        cond = self.expr()
        self.expect_kw("TUNC")
        self.expect_nl()
        body = self.block({"ALITER", "FINIS"}, in_loop, in_rite)
        arms.append((cond, body))
        els = None
        while self.at_kw("ALITER"):
            self.next()
            if self.at_kw("SI"):
                self.next()
                c2 = self.expr()
                self.expect_kw("TUNC")
                self.expect_nl()
                arms.append((c2, self.block({"ALITER", "FINIS"}, in_loop, in_rite)))
            else:
                self.expect_nl()
                els = self.block({"FINIS"}, in_loop, in_rite)
                break
        self.finis("SI")
        return A.If(line=t.line, arms=arms, els=els)

    def while_stmt(self, in_rite):
        t = self.expect_kw("DUM")
        cond = self.expr()
        self.expect_kw("AGE")
        self.expect_nl()
        body = self.block({"FINIS"}, in_loop=True, in_rite=in_rite)
        self.finis("DUM")
        return A.While(line=t.line, cond=cond, body=body)

    def for_stmt(self, in_rite):
        t = self.expect_kw("PRO")
        self.expect_kw("OMNI")
        var = self.expect_ident()
        self.expect_kw("IN")
        it = self.expr()
        self.expect_kw("AGE")
        self.expect_nl()
        body = self.block({"FINIS"}, in_loop=True, in_rite=in_rite)
        self.finis("PRO")
        return A.For(line=t.line, var=var, it=it, body=body)

    def try_stmt(self, in_loop, in_rite):
        t = self.expect_kw("TEMPTA")
        self.expect_nl()
        body = self.block({"SI", "DENIQUE", "FINIS"}, in_loop, in_rite)
        catch_var, catch, fin = None, None, None
        if self.at_kw("SI"):
            self.next()
            self.expect_kw("HERESIS")
            self.expect_op("(")
            catch_var = self.expect_ident()
            self.expect_op(")")
            self.expect_nl()
            catch = self.block({"DENIQUE", "FINIS"}, in_loop, in_rite)
        if self.at_kw("DENIQUE"):
            self.next()
            self.expect_nl()
            fin = self.block({"FINIS"}, in_loop, in_rite)
        if catch is None and fin is None:
            self.err("TEMPTA needs a catch or a DENIQUE.", t.line)
        self.finis("TEMPTA")
        return A.Try(line=t.line, body=body, catch_var=catch_var,
                     catch=catch, fin=fin)

    def rite_def(self) -> A.RiteDef:
        t = self.expect_kw("RITUS")
        name = self.expect_ident()
        params, ret = self.rite_signature()
        body = self.block({"FINIS"}, in_rite=True)
        self.finis("RITUS")
        return A.RiteDef(line=t.line, name=name, params=params, ret=ret,
                         body=body)

    def rite_signature(self):
        self.expect_op("(")
        params = []
        if not self.at_op(")"):
            while True:
                pn = self.expect_ident()
                self.expect_op(":")
                pt = self.type_expr()
                params.append((pn, pt))
                if self.at_op(","):
                    self.next()
                    continue
                break
        self.expect_op(")")
        self.expect_op("->")
        ret = self.type_expr()
        self.expect_nl()
        return params, ret

    def schema_def(self):
        t = self.expect_kw("SCHEMA")
        name = self.expect_ident()
        self.expect_nl()
        fields = []
        self.skip_nls()
        while not self.at_kw("FINIS"):
            fn = self.expect_ident()
            self.expect_op(":")
            ft = self.type_expr()
            default = None
            if self.at_op("="):
                self.next()
                default = self.expr()
            self.expect_nl()
            fields.append((fn, ft, default))
            self.skip_nls()
        self.finis("SCHEMA")
        return A.SchemaDef(line=t.line, name=name, fields=fields)

    def import_stmt(self):
        t = self.expect_kw("INVOCO")
        if self.peek().kind == "IDENT":
            names = [self.expect_ident()]
            while self.at_op(","):
                self.next()
                names.append(self.expect_ident())
            self.expect_kw("EX")
            path = self.plain_string()
            self.expect_nl()
            return A.Import(line=t.line, path=path, names=names)
        path = self.plain_string()
        alias = None
        if self.at_kw("UT"):
            self.next()
            alias = self.expect_ident()
        self.expect_nl()
        return A.Import(line=t.line, path=path, alias=alias)

    # ---------- infrastructure ----------
    def attr_block(self, enders: set[str]) -> list:
        out = []
        self.skip_nls()
        while not (self.peek().kind == "KW" and self.peek().value in enders):
            if self.peek().kind == "EOF":
                self.err("Unclosed attribute block.", self.peek().line)
            kt = self.peek()
            if kt.kind == "IDENT":
                key = self.expect_ident()
            elif kt.kind == "STRING":
                key = self.plain_string()
            else:
                self.err("Expected attribute name.", kt.line)
            self.expect_op(":")
            if self.peek().kind == "NL":
                self.next()
                nested = self.attr_block({"FINIS"})
                self.expect_kw("FINIS")
                self.expect_nl()
                out.append(A.AttrKV(line=kt.line, key=key, value=nested))
            else:
                e = self.expr()
                self.expect_nl()
                out.append(A.AttrKV(line=kt.line, key=key, value=e))
            self.skip_nls()
        return out

    def foedus(self):
        t = self.expect_kw("FOEDUS")
        name = self.plain_string()
        self.expect_nl()
        attrs = self.attr_block({"FINIS"})
        self.finis("FOEDUS")
        return A.Foedus(line=t.line, name=name, attrs=attrs)

    def sedes(self):
        t = self.expect_kw("SEDES")
        name = self.plain_string()
        self.expect_nl()
        attrs = self.attr_block({"FINIS"})
        self.finis("SEDES")
        return A.Sedes(line=t.line, name=name, attrs=attrs)

    def exstruatur(self):
        t = self.expect_kw("EXSTRUATUR")
        species = self.expect_ident()
        if species not in SPECIES:
            self.err(f"Unknown species '{species}'. Known: {sorted(SPECIES)}.",
                     t.line)
        parts, ln = self.expect_string_literal()
        name_expr = self._string_node(parts, ln)
        self.expect_nl()
        attrs = self.attr_block({"FINIS"})
        self.finis("EXSTRUATUR")
        return A.Exstruatur(line=t.line, species=species,
                            name_expr=name_expr, attrs=attrs)

    def scrutor(self):
        t = self.expect_kw("SCRUTOR")
        label = self.expect_ident()
        name = self.plain_string()
        self.expect_nl()
        attrs = self.attr_block({"FINIS"})
        self.finis("SCRUTOR")
        return A.Scrutor(line=t.line, label=label, name=name, attrs=attrs)

    def postulo(self):
        t = self.expect_kw("POSTULO")
        name = self.expect_ident()
        self.expect_op(":")
        ty = self.type_expr()
        default = None
        if self.at_op("="):
            self.next()
            default = self.expr()
        arcanum = False
        if self.at_kw("ARCANUM"):
            self.next()
            arcanum = True
        self.expect_nl()
        return A.Postulo(line=t.line, name=name, type=ty, default=default,
                         arcanum=arcanum)

    def profiteor(self):
        t = self.expect_kw("PROFITEOR")
        name = self.expect_ident()
        self.expect_op("=")
        e = self.expr()
        arcanum = False
        if self.at_kw("ARCANUM"):
            self.next()
            arcanum = True
        self.expect_nl()
        return A.Profiteor(line=t.line, name=name, expr=e, arcanum=arcanum)

    # ---------- types ----------
    def type_expr(self):
        t = self.peek()
        if t.kind == "KW" and t.value == "RITUS" and self.peek(1).kind == "OP" and self.peek(1).value == "(":
            self.next()
            return self._rite_type()
        t = self.next()
        if t.kind == "KW" and t.value in PRIMITIVES:
            return A.TName(line=t.line, name=t.value)
        if t.kind == "KW" and t.value == "ORDO":
            self.expect_op("[")
            inner = self.type_expr()
            self.expect_op("]")
            return A.TOrdo(line=t.line, inner=inner)
        if t.kind == "KW" and t.value == "TABULA":
            self.expect_op("[")
            k = self.type_expr()
            self.expect_op(",")
            v = self.type_expr()
            self.expect_op("]")
            return A.TTabula(line=t.line, k=k, v=v)
        if t.kind == "IDENT":
            return A.TName(line=t.line, name=t.value)
        self.err(f"Expected a type (found {t.value!r}).", t.line)

    def _rite_type(self) -> A.TRitus:
        line = self.peek().line
        self.expect_op("(")
        params = []
        if not self.at_op(")"):
            while True:
                if (self.peek().kind == "IDENT" and self.peek(1).kind == "OP"
                        and self.peek(1).value == ":"):
                    pn = self.expect_ident()
                    self.expect_op(":")
                    pt = self.type_expr()
                    params.append((pn, pt))
                else:
                    pt = self.type_expr()
                    params.append((None, pt))
                if self.at_op(","):
                    self.next()
                    continue
                break
        self.expect_op(")")
        self.expect_op("->")
        ret = self.type_expr()
        return A.TRitus(line=line, params=params, ret=ret)

    # ---------- expressions ----------
    def expr(self):
        return self.or_expr()

    def or_expr(self):
        e = self.and_expr()
        while self.at_kw("VEL"):
            t = self.next()
            e = A.BinOp(line=t.line, op="VEL", l=e, r=self.and_expr())
        return e

    def and_expr(self):
        e = self.eq_expr()
        while self.at_kw("ET"):
            t = self.next()
            e = A.BinOp(line=t.line, op="ET", l=e, r=self.eq_expr())
        return e

    def eq_expr(self):
        e = self.cmp_expr()
        if self.at_op("==") or self.at_op("!="):
            t = self.next()
            e = A.BinOp(line=t.line, op=t.value, l=e, r=self.cmp_expr())
            if self.at_op("==") or self.at_op("!="):
                self.err("Chained comparison.", t.line,
                         "P-IX", "comparatio_catenata")
        return e

    def cmp_expr(self):
        e = self.add_expr()
        for op in ("<", "<=", ">", ">="):
            if self.at_op(op):
                t = self.next()
                e = A.BinOp(line=t.line, op=op, l=e, r=self.add_expr())
                for op2 in ("<", "<=", ">", ">="):
                    if self.at_op(op2):
                        self.err("Chained comparison.", t.line,
                                 "P-IX", "comparatio_catenata")
                break
        return e

    def add_expr(self):
        e = self.mul_expr()
        while self.at_op("+") or self.at_op("-"):
            t = self.next()
            e = A.BinOp(line=t.line, op=t.value, l=e, r=self.mul_expr())
        return e

    def mul_expr(self):
        e = self.unary()
        while self.at_op("*") or self.at_op("/") or self.at_op("%"):
            t = self.next()
            e = A.BinOp(line=t.line, op=t.value, l=e, r=self.unary())
        return e

    def unary(self):
        if self.at_op("-"):
            t = self.next()
            return A.UnOp(line=t.line, op="-", e=self.unary())
        if self.at_kw("NON"):
            t = self.next()
            return A.UnOp(line=t.line, op="NON", e=self.unary())
        return self.postfix()

    def postfix(self):
        e = self.primary()
        while True:
            if self.at_op("("):
                t = self.next()
                args = []
                self.skip_nls()
                if not self.at_op(")"):
                    while True:
                        args.append(self.expr())
                        if self.at_op(","):
                            self.next()
                            self.skip_nls()
                            if self.at_op(")"):
                                break
                            continue
                        break
                self.expect_op(")")
                e = A.Call(line=t.line, fn=e, args=args)
            elif self.at_op("["):
                t = self.next()
                idx = self.expr()
                self.expect_op("]")
                e = A.Index(line=t.line, obj=e, idx=idx)
            elif self.at_op("."):
                t = self.next()
                name = self.expect_ident()
                e = A.Attr(line=t.line, obj=e, name=name)
            else:
                return e

    def primary(self):
        t = self.peek()
        if t.kind in ("INT", "ROMAN"):
            self.next()
            return A.Num(line=t.line, v=t.value, arabic=(t.kind == "INT"))
        if t.kind == "FLOAT":
            self.next()
            return A.Flo(line=t.line, v=t.value)
        if t.kind == "STRING":
            self.next()
            return self._string_node(t.value, t.line)
        if t.kind == "KW":
            if t.value == "VERUM":
                self.next()
                return A.Bool(line=t.line, v=True)
            if t.value == "FALSUM":
                self.next()
                return A.Bool(line=t.line, v=False)
            if t.value == "NIHIL":
                self.next()
                return A.Nihil(line=t.line)
            if t.value == "AUSCULTO":
                self.next()
                self.expect_op("(")
                self.expect_op(")")
                return A.Call(line=t.line, fn=A.Ident(line=t.line,
                              name="__ausculto__"), args=[])
            if t.value == "RITUS":
                self.next()
                params, ret = self.rite_signature()
                body = self.block({"FINIS"}, in_rite=True)
                self.expect_kw("FINIS")
                self.expect_kw("RITUS")
                return A.RiteExpr(line=t.line, params=params, ret=ret, body=body)
        if t.kind == "IDENT":
            # schema literal?
            if self.peek(1).kind == "OP" and self.peek(1).value == "{":
                name = self.expect_ident()
                self.expect_op("{")
                fields = []
                self.skip_nls()
                if not self.at_op("}"):
                    while True:
                        fn = self.expect_ident()
                        self.expect_op(":")
                        fields.append((fn, self.expr()))
                        if self.at_op(","):
                            self.next()
                            self.skip_nls()
                            if self.at_op("}"):
                                break
                            continue
                        break
                self.skip_nls()
                self.expect_op("}")
                return A.SchemaLit(line=t.line, name=name, fields=fields)
            self.next()
            return A.Ident(line=t.line, name=t.value)
        if t.kind == "OP" and t.value == "(":
            self.next()
            e = self.expr()
            self.expect_op(")")
            return e
        if t.kind == "OP" and t.value == "[":
            self.next()
            items = []
            self.skip_nls()
            if not self.at_op("]"):
                while True:
                    items.append(self.expr())
                    if self.at_op(","):
                        self.next()
                        self.skip_nls()
                        if self.at_op("]"):
                            break
                        continue
                    break
            self.skip_nls()
            self.expect_op("]")
            return A.ListLit(line=t.line, items=items)
        if t.kind == "OP" and t.value == "{":
            self.next()
            entries = []
            self.skip_nls()
            if not self.at_op("}"):
                while True:
                    k = self.expr()
                    self.expect_op(":")
                    entries.append((k, self.expr()))
                    if self.at_op(","):
                        self.next()
                        self.skip_nls()
                        if self.at_op("}"):
                            break
                        continue
                    break
            self.skip_nls()
            self.expect_op("}")
            return A.MapLit(line=t.line, entries=entries)
        self.err(f"Unexpected {t.value!r} where an expression was awaited.",
                 t.line)

    def _string_node(self, parts: list[StrPart], line: int) -> A.Str:
        out = []
        for p in parts:
            if p.kind == "t":
                out.append(("t", p.value))
            else:
                sub = Lexer(p.value, self.archivum)
                subtoks = sub.tokens()
                # fix line numbers
                for st in subtoks:
                    st.line = p.line or line
                sp = Parser(subtoks, self.archivum)
                sp.skip_nls()
                e = sp.expr()
                out.append(("e", e))
        return A.Str(line=line, parts=out)


def parse_source(src: str, archivum: str = "<anon>") -> A.Program:
    return Parser(Lexer(src, archivum).tokens(), archivum).parse_program()
