"""Runtime values and environments."""
from __future__ import annotations
from .heresiae import Heresis
from .lexicon import int_to_roman

INT64_MIN = -(2 ** 63)
INT64_MAX = 2 ** 63 - 1


class Cell:
    __slots__ = ("value", "sanctum")

    def __init__(self, value, sanctum=False):
        self.value = value
        self.sanctum = sanctum


class Env:
    def __init__(self, parent: "Env | None" = None):
        self.parent = parent
        self.vars: dict[str, Cell] = {}

    def lookup(self, name: str) -> Cell | None:
        e = self
        while e is not None:
            c = e.vars.get(name)
            if c is not None:
                return c
            e = e.parent
        return None

    def declare(self, name: str, value, sanctum=False, line=0, archivum="?"):
        if name in self.vars:
            from .heresiae import Profanatio
            raise Profanatio("P-XI", "declaratio_geminata",
                             f"'{name}' is already declared in this scope.",
                             archivum, line)
        self.vars[name] = Cell(value, sanctum)


class Rite:
    def __init__(self, name, params, ret, body, env, archivum):
        self.name = name
        self.params = params      # [(name, type_ast)]
        self.ret = ret
        self.body = body
        self.env = env
        self.archivum = archivum

    def __repr__(self):
        return f"RITUS {self.name}"


class NativeRite:
    def __init__(self, name, fn, arity=None):
        self.name = name
        self.fn = fn
        self.arity = arity

    def __repr__(self):
        return f"RITUS {self.name}"


class SchemaType:
    def __init__(self, name, fields, archivum):
        self.name = name
        self.fields = fields      # [(name, type_ast, default_expr|None)]
        self.archivum = archivum

    def __repr__(self):
        return f"SCHEMA {self.name}"


class Instance:
    def __init__(self, schema: SchemaType, values: dict):
        self.schema = schema
        self.values = values


class Module:
    def __init__(self, name, exports: dict):
        self.name = name
        self.exports = exports

    def __repr__(self):
        return f"LITANIA {self.name}"


class HeresyValue:
    """A caught heresy, visible to the program."""

    def __init__(self, h: Heresis):
        self.h = h

    @property
    def fields(self):
        origo = HeresyValue(self.h.origo) if self.h.origo else None
        return {
            "genus": self.h.genus, "nuntius": self.h.nuntius,
            "versus": self.h.versus, "archivum": self.h.archivum,
            "gradus": self.h.gradus, "vestigium": list(self.h.vestigium),
            "origo": origo,
        }


class Relatio:
    """Deferred Terraform reference (docs 10-fabrica §7)."""

    def __init__(self, kind: str, res_name: str, path: tuple = ()):
        self.kind = kind          # 'resource' | 'data'
        self.res_name = res_name
        self.path = path

    def extend(self, name: str) -> "Relatio":
        return Relatio(self.kind, self.res_name, self.path + (name,))

    def __repr__(self):
        return f"<relatio {self.kind}:{self.res_name}.{'.'.join(self.path)}>"


class RelatioRoot:
    def __init__(self, kind: str):
        self.kind = kind          # 'resource' | 'data'


# marker used when a Relatio is interpolated into a string
REL_L, REL_R = "\x01REL\x02", "\x03LER\x04"


def relatio_marker(r: Relatio) -> str:
    return f"{REL_L}{r.kind}:{r.res_name}:{'.'.join(r.path)}{REL_R}"


def scriptum(v, depth=0) -> str:
    """Canonical text form (docs 02-types §8)."""
    if depth > 32:
        return "..."
    if v is None:
        return "NIHIL"
    if isinstance(v, bool):
        return "VERUM" if v else "FALSUM"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        s = repr(v)
        return s
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return "[" + ", ".join(scriptum(x, depth + 1) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{scriptum(k, depth+1)}: {scriptum(x, depth+1)}"
                               for k, x in v.items()) + "}"
    if isinstance(v, Instance):
        inner = ", ".join(f"{k}: {scriptum(x, depth+1)}"
                          for k, x in v.values.items())
        return f"{v.schema.name}{{{inner}}}"
    if isinstance(v, (Rite, NativeRite, Module, SchemaType)):
        return repr(v)
    if isinstance(v, HeresyValue):
        return f"HERESIS({v.h.genus}: {v.h.nuntius})"
    if isinstance(v, Relatio):
        return relatio_marker(v)
    return str(v)


def genus_valoris(v) -> str:
    if v is None:
        return "NIHIL"
    if isinstance(v, bool):
        return "VERITAS"
    if isinstance(v, int):
        return "NUMERUS"
    if isinstance(v, float):
        return "FRACTIO"
    if isinstance(v, str):
        return "SCRIPTUM"
    if isinstance(v, list):
        return "ORDO"
    if isinstance(v, dict):
        return "TABULA"
    if isinstance(v, Instance):
        return v.schema.name
    if isinstance(v, (Rite, NativeRite)):
        return "RITUS"
    if isinstance(v, HeresyValue):
        return "HERESIS"
    if isinstance(v, Relatio):
        return "RELATIO"
    return type(v).__name__
