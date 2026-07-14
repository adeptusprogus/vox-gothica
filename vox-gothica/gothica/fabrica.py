"""FABRICA: consecration-time evaluation → Terraform JSON (docs 10)."""
from __future__ import annotations
import json
import os
import re
import shutil
import subprocess
import sys
from . import arbor as A
from .heresiae import Heresis, IraMachinae
from .valores import (Relatio, RelatioRoot, Instance, scriptum,
                      REL_L, REL_R, relatio_marker)
from .lexicon import roman_to_int

NAME_RE = re.compile(r"^[a-z_][a-z0-9_]*$")

ALIASES = {
    "regio": "region",
    "numerus_machinarum": "count",
    "genus_machinae": "instance_type",
    "nomen_datum": "name",
    "postulat": "depends_on",
    "cognomen": "alias",
    "vita": "lifecycle",
}
# imago is genus-aware
_IMAGO_AMI = ("aws_instance", "aws_launch_template")

_MARKER_RE = re.compile(re.escape(REL_L) + r"(resource|data):([a-z0-9_]+):([a-zA-Z0-9_.]*)"
                        + re.escape(REL_R))


class FabricaState:
    def __init__(self, name: str):
        self.name = name
        self.providers: list[tuple[str, dict]] = []
        self.backend: tuple[str, dict] | None = None
        self.resources: dict[str, dict] = {}     # nomen -> {genus, species, attrs}
        self.datas: dict[str, dict] = {}
        self.variables: dict[str, dict] = {}
        self.outputs: dict[str, dict] = {}
        self.postulata: dict[str, object] = {}   # resolved demand values

    # ---------- statement handlers (called by interpreter) ----------
    def _attrs(self, interp, attrs, env) -> dict:
        out = {}
        for kv in attrs:
            if isinstance(kv.value, list) and kv.value and \
                    isinstance(kv.value[0], A.AttrKV):
                out[kv.key] = self._attrs(interp, kv.value, env)
            elif isinstance(kv.value, list) and not kv.value:
                out[kv.key] = {}
            else:
                out[kv.key] = interp.eval(kv.value, env)
        return out

    def foedus(self, interp, st: A.Foedus, env):
        self.providers.append((st.name, self._attrs(interp, st.attrs, env)))

    def sedes(self, interp, st: A.Sedes, env):
        if self.backend is not None:
            raise interp.h("nomen_geminum", "a fabrica has one SEDES only",
                           st, major=True)
        self.backend = (st.name, self._attrs(interp, st.attrs, env))

    def exstruatur(self, interp, st: A.Exstruatur, env):
        nomen = interp.eval(st.name_expr, env)
        if not isinstance(nomen, str) or not NAME_RE.match(nomen):
            raise interp.h("argumentum_pravum",
                           f"resource name {scriptum(nomen)!r} must match "
                           f"[a-z_][a-z0-9_]*", st)
        if nomen in self.resources or nomen in self.datas:
            raise interp.h("nomen_geminum",
                           f"resource '{nomen}' raised twice", st, major=True)
        attrs = self._attrs(interp, st.attrs, env)
        genus = attrs.pop("genus", None)
        if not isinstance(genus, str):
            raise interp.h("argumentum_pravum",
                           f"resource '{nomen}' lacks genus:", st)
        self.resources[nomen] = {"genus": genus, "species": st.species,
                                 "attrs": attrs}

    def scrutor(self, interp, st: A.Scrutor, env):
        if st.name in self.datas or st.name in self.resources:
            raise interp.h("nomen_geminum",
                           f"data '{st.name}' examined twice", st, major=True)
        attrs = self._attrs(interp, st.attrs, env)
        genus = attrs.pop("genus", None)
        if not isinstance(genus, str):
            raise interp.h("argumentum_pravum",
                           f"data '{st.name}' lacks genus:", st)
        self.datas[st.name] = {"genus": genus, "attrs": attrs}

    def postulo(self, interp, st: A.Postulo, env):
        name = st.name
        raw = None
        source = None
        if name in self.postulata:
            raw, source = self.postulata[name], "flag"
        elif f"GOTHICA_POSTULATUM_{name.upper()}" in os.environ:
            raw = os.environ[f"GOTHICA_POSTULATUM_{name.upper()}"]
            source = "env"
        value = None
        if raw is not None:
            value = _coerce(interp, raw, st.type, st)
        elif st.default is not None:
            value = interp.eval(st.default, env)
        else:
            raise IraMachinae(
                f"POSTULO {name} is unanswered — supply "
                f"-postulatum {name}=... or GOTHICA_POSTULATUM_{name.upper()}")
        interp.check_type(value, st.type, st, f"demand '{name}'")
        env.declare(name, value, sanctum=True, line=st.line,
                    archivum=interp.cur_file)
        self.variables[name] = {"value": value, "arcanum": st.arcanum,
                                "type": interp._tname(st.type)}

    def profiteor(self, interp, st: A.Profiteor, env):
        if st.name in self.outputs:
            raise interp.h("nomen_geminum",
                           f"output '{st.name}' proclaimed twice", st,
                           major=True)
        v = interp.eval(st.expr, env)
        self.outputs[st.name] = {"value": v, "arcanum": st.arcanum}

    # ---------- emission ----------
    def emit(self) -> dict:
        doc: dict = {}
        tf: dict = {}
        req = {}
        providers_json = {}
        for pname, attrs in self.providers:
            attrs = dict(attrs)
            ver = attrs.pop("versio_foederis", None)
            req[pname] = {"source": f"hashicorp/{pname}"}
            if ver:
                req[pname]["version"] = ver
            providers_json.setdefault(pname, []).append(
                self._emit_attrs(attrs, None))
        if req:
            tf["required_providers"] = req
        if self.backend:
            bname, battrs = self.backend
            tf["backend"] = {bname: self._emit_attrs(battrs, None)}
        if tf:
            doc["terraform"] = tf
        if providers_json:
            doc["provider"] = {k: (v[0] if len(v) == 1 else v)
                               for k, v in providers_json.items()}
        if self.variables:
            doc["variable"] = {}
            for n, spec in self.variables.items():
                var = {"default": self._plain(spec["value"])}
                if spec["arcanum"]:
                    var["sensitive"] = True
                doc["variable"][n] = var
        res: dict = {}
        for nomen, spec in self.resources.items():
            body = self._emit_attrs(spec["attrs"], spec["genus"])
            body["//"] = f"species: {spec['species']}"
            res.setdefault(spec["genus"], {})[nomen] = body
        if res:
            doc["resource"] = res
        dat: dict = {}
        for nomen, spec in self.datas.items():
            dat.setdefault(spec["genus"], {})[nomen] = \
                self._emit_attrs(spec["attrs"], spec["genus"])
        if dat:
            doc["data"] = dat
        if self.outputs:
            doc["output"] = {}
            for n, spec in self.outputs.items():
                out = {"value": self._emit_value(spec["value"], None)}
                if spec["arcanum"]:
                    out["sensitive"] = True
                doc["output"][n] = out
        return doc

    def _emit_attrs(self, attrs: dict, genus: str | None) -> dict:
        out = {}
        for k, v in attrs.items():
            key = ALIASES.get(k, k)
            if k == "imago":
                key = "ami" if (genus in _IMAGO_AMI) else "image"
            out[key] = self._emit_value(v, genus)
        return out

    def _emit_value(self, v, genus):
        if isinstance(v, Relatio):
            return "${" + self._address(v) + "}"
        if isinstance(v, str):
            return self._resolve_markers(v)
        if isinstance(v, dict):
            return {k: self._emit_value(x, genus) for k, x in v.items()}
        if isinstance(v, list):
            return [self._emit_value(x, genus) for x in v]
        if isinstance(v, Instance):
            return {k: self._emit_value(x, genus) for k, x in v.values.items()}
        return v

    def _plain(self, v):
        if isinstance(v, (Relatio, RelatioRoot)):
            raise IraMachinae("a deferred reference cannot be a variable default")
        return v

    def _address(self, r: Relatio) -> str:
        if r.kind == "data":
            spec = self.datas.get(r.res_name)
            if spec is None:
                raise IraMachinae(f"scrutinium.{r.res_name} names no data source")
            base = f"data.{spec['genus']}.{r.res_name}"
        else:
            spec = self.resources.get(r.res_name)
            if spec is None:
                raise IraMachinae(f"reference to unraised resource "
                                  f"'{r.res_name}'")
            base = f"{spec['genus']}.{r.res_name}"
        return base + ("." + ".".join(r.path) if r.path else "")

    def _resolve_markers(self, s: str) -> str:
        def sub(m):
            r = Relatio(m.group(1), m.group(2),
                        tuple(m.group(3).split(".")) if m.group(3) else ())
            return "${" + self._address(r) + "}"
        return _MARKER_RE.sub(sub, s)


def _coerce(interp, raw: str, t, node):
    if isinstance(t, A.TName):
        if t.name == "NUMERUS":
            r = roman_to_int(raw)
            if r is not None:
                return r
            try:
                return int(raw)
            except ValueError:
                raise IraMachinae(f"'{raw}' is not a NUMERUS")
        if t.name == "FRACTIO":
            return float(raw)
        if t.name == "VERITAS":
            return raw in ("VERUM", "verum", "true", "1")
        if t.name == "SCRIPTUM":
            return raw
    raise IraMachinae(f"cannot coerce demand of type {interp._tname(t)}")


# ---------------- terraform driver ----------------
def workdir_for(prog_name: str, base: str = ".") -> str:
    d = os.path.join(base, ".gothica", prog_name)
    os.makedirs(d, exist_ok=True)
    return d


def write_json(state: FabricaState, base: str = ".") -> str:
    d = workdir_for(state.name, base)
    path = os.path.join(d, "main.tf.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state.emit(), f, indent=2, ensure_ascii=False)
    return path


def terraform(cmd: list[str], cwd: str, silens=False) -> int:
    exe = shutil.which("terraform")
    if exe is None:
        raise IraMachinae(
            "the terraform binary is absent from this shrine. Install it, or "
            "run inside the vox-gothica Docker image (gothica/fabrica).")
    if not os.path.isdir(os.path.join(cwd, ".terraform")):
        r = subprocess.run([exe, "init", "-input=false", "-no-color"],
                           cwd=cwd, capture_output=True, text=True)
        if r.returncode != 0:
            raise IraMachinae("terraform init failed", r.stderr or r.stdout)
    r = subprocess.run([exe, *cmd, "-no-color"], cwd=cwd, text=True)
    return r.returncode
