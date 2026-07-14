"""AST nodes."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Node:
    line: int = 0


# ----- types -----
@dataclass
class TName(Node):
    name: str = ""          # NUMERUS/FRACTIO/... or schema ident


@dataclass
class TOrdo(Node):
    inner: Any = None


@dataclass
class TTabula(Node):
    k: Any = None
    v: Any = None


# ----- expressions -----
@dataclass
class Num(Node):
    v: int = 0
    arabic: bool = True   # False when lexed as canonical Roman numeral


@dataclass
class Flo(Node):
    v: float = 0.0


@dataclass
class Str(Node):
    parts: list = field(default_factory=list)   # [('t',str)|('e',Node)]


@dataclass
class Bool(Node):
    v: bool = False


@dataclass
class Nihil(Node):
    pass


@dataclass
class Ident(Node):
    name: str = ""


@dataclass
class ListLit(Node):
    items: list = field(default_factory=list)


@dataclass
class MapLit(Node):
    entries: list = field(default_factory=list)  # [(k_expr, v_expr)]


@dataclass
class SchemaLit(Node):
    name: str = ""
    fields: list = field(default_factory=list)   # [(name, expr)]


@dataclass
class RiteExpr(Node):
    params: list = field(default_factory=list)   # [(name, type)]
    ret: Any = None
    body: list = field(default_factory=list)
    name: str = "<anonymus>"


@dataclass
class BinOp(Node):
    op: str = ""
    l: Any = None
    r: Any = None


@dataclass
class UnOp(Node):
    op: str = ""
    e: Any = None


@dataclass
class Call(Node):
    fn: Any = None
    args: list = field(default_factory=list)


@dataclass
class Index(Node):
    obj: Any = None
    idx: Any = None


@dataclass
class Attr(Node):
    obj: Any = None
    name: str = ""


# ----- statements -----
@dataclass
class Declare(Node):
    name: str = ""
    type: Any = None
    expr: Any = None
    sanctum: bool = False


@dataclass
class Assign(Node):
    target: Any = None
    expr: Any = None


@dataclass
class If(Node):
    arms: list = field(default_factory=list)     # [(cond, block)]
    els: Optional[list] = None


@dataclass
class While(Node):
    cond: Any = None
    body: list = field(default_factory=list)


@dataclass
class For(Node):
    var: str = ""
    it: Any = None
    body: list = field(default_factory=list)


@dataclass
class Try(Node):
    body: list = field(default_factory=list)
    catch_var: Optional[str] = None
    catch: Optional[list] = None
    fin: Optional[list] = None


@dataclass
class Print(Node):
    err: bool = False
    expr: Any = None


@dataclass
class Return(Node):
    expr: Any = None


@dataclass
class Raise(Node):
    expr: Any = None
    genus: Optional[str] = None


@dataclass
class Break(Node):
    pass


@dataclass
class Continue(Node):
    pass


@dataclass
class ExprStmt(Node):
    expr: Any = None


@dataclass
class Import(Node):
    path: str = ""
    alias: Optional[str] = None
    names: Optional[list] = None     # EX-form


@dataclass
class SchemaDef(Node):
    name: str = ""
    fields: list = field(default_factory=list)   # [(name, type, default_expr|None)]


@dataclass
class RiteDef(Node):
    name: str = ""
    params: list = field(default_factory=list)
    ret: Any = None
    body: list = field(default_factory=list)
    sanctum: bool = False


# ----- infrastructure -----
@dataclass
class AttrKV(Node):
    key: str = ""
    value: Any = None        # expr | list[AttrKV] (nested block)


@dataclass
class Foedus(Node):
    name: str = ""
    attrs: list = field(default_factory=list)


@dataclass
class Sedes(Node):
    name: str = ""
    attrs: list = field(default_factory=list)


@dataclass
class Exstruatur(Node):
    species: str = ""
    name_expr: Any = None
    attrs: list = field(default_factory=list)


@dataclass
class Scrutor(Node):
    label: str = ""
    name: str = ""
    attrs: list = field(default_factory=list)


@dataclass
class Postulo(Node):
    name: str = ""
    type: Any = None
    default: Any = None
    arcanum: bool = False


@dataclass
class Profiteor(Node):
    name: str = ""
    expr: Any = None
    arcanum: bool = False


@dataclass
class Program(Node):
    mode: str = "CANTICUM"       # CANTICUM | FABRICA | LITANIA
    name: str = ""
    body: list = field(default_factory=list)
    archivum: str = "?"
