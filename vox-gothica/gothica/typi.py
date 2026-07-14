"""Static type compatibility (M5 Censura)."""
from __future__ import annotations

from typing import Any

from . import arbor as A

WILDCARD = "*"
TABULA_KEYS = frozenset({"NUMERUS", "SCRIPTUM"})


def is_wildcard(t: Any) -> bool:
    return isinstance(t, A.TName) and t.name == WILDCARD


def tname(t: Any) -> str:
    if isinstance(t, A.TName):
        return t.name
    if isinstance(t, A.TOrdo):
        return f"ORDO[{tname(t.inner)}]"
    if isinstance(t, A.TTabula):
        return f"TABULA[{tname(t.k)}, {tname(t.v)}]"
    if isinstance(t, A.TRitus):
        ps = ", ".join(
            f"{n}: {tname(pt)}" if n else tname(pt)
            for n, pt in t.params
        )
        return f"RITUS({ps}) -> {tname(t.ret)}"
    return "?"


def type_eq(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return a is b
    if type(a) is not type(b):
        return False
    if isinstance(a, A.TName):
        return a.name == b.name
    if isinstance(a, A.TOrdo):
        return type_eq(a.inner, b.inner)
    if isinstance(a, A.TTabula):
        return type_eq(a.k, b.k) and type_eq(a.v, b.v)
    if isinstance(a, A.TRitus):
        if len(a.params) != len(b.params):
            return False
        for (_, pa), (_, pb) in zip(a.params, b.params):
            if not type_eq(pa, pb):
                return False
        return type_eq(a.ret, b.ret)
    return False


def valid_tabula_key(t: Any) -> bool:
    return isinstance(t, A.TName) and t.name in TABULA_KEYS


def resolve_type_ref(t: Any, *, primitives: frozenset[str], schemas: set[str]) -> bool:
    """Return True if type reference is known."""
    if t is None:
        return True
    if isinstance(t, A.TName):
        return t.name in primitives or t.name in schemas
    if isinstance(t, A.TOrdo):
        return resolve_type_ref(t.inner, primitives=primitives, schemas=schemas)
    if isinstance(t, A.TTabula):
        if not valid_tabula_key(t.k):
            return False
        return (
            resolve_type_ref(t.k, primitives=primitives, schemas=schemas)
            and resolve_type_ref(t.v, primitives=primitives, schemas=schemas)
        )
    if isinstance(t, A.TRitus):
        return all(
            resolve_type_ref(pt, primitives=primitives, schemas=schemas)
            for _, pt in t.params
        ) and resolve_type_ref(t.ret, primitives=primitives, schemas=schemas)
    return True


def binds(got: Any, want: Any) -> bool:
    if type_eq(got, want):
        return True
    if is_wildcard(want):
        return True
    if isinstance(want, A.TOrdo) and isinstance(got, A.TOrdo):
        return binds(got.inner, want.inner)
    if isinstance(want, A.TTabula) and isinstance(got, A.TTabula):
        return binds(got.k, want.k) and binds(got.v, want.v)
    if isinstance(want, A.TName) and want.name == "RITUS":
        return isinstance(got, A.TRitus)
    return False
