"""The Machine-Cult: built-ins and standard modules (docs 09-stdlib)."""
from __future__ import annotations
import copy
import json
import math
import os
import random
import subprocess
import sys
import time
import urllib.request
import urllib.error
from .heresiae import Heresis
from .lexicon import int_to_roman, roman_to_int
from .valores import (NativeRite, Module, Instance, Rite, scriptum,
                      genus_valoris, INT64_MIN, INT64_MAX, Relatio)


def _h(genus, msg, gradus=0):
    return Heresis(genus, msg, gradus=gradus)


def _need(cond, genus, msg):
    if not cond:
        raise _h(genus, msg)


def _int(v, ctx):
    _need(isinstance(v, int) and not isinstance(v, bool),
          "typus_profanus", f"{ctx} requires NUMERUS, got {genus_valoris(v)}")
    return v


def _str(v, ctx):
    _need(isinstance(v, str), "typus_profanus",
          f"{ctx} requires SCRIPTUM, got {genus_valoris(v)}")
    return v


def _list(v, ctx):
    _need(isinstance(v, list), "typus_profanus",
          f"{ctx} requires ORDO, got {genus_valoris(v)}")
    return v


def _dict(v, ctx):
    _need(isinstance(v, dict), "typus_profanus",
          f"{ctx} requires TABULA, got {genus_valoris(v)}")
    return v


# ---------------- built-ins ----------------
def bi_longitudo(x):
    if isinstance(x, (str, list, dict)):
        return len(x)
    raise _h("typus_profanus", "longitudo takes ORDO, TABULA or SCRIPTUM")


def bi_series(a, b):
    return list(range(_int(a, "series"), _int(b, "series")))


def bi_series_gradu(a, b, g):
    a, b, g = _int(a, "series_gradu"), _int(b, "series_gradu"), _int(g, "series_gradu")
    _need(g != 0, "argumentum_pravum", "series_gradu with zero step")
    return list(range(a, b, g))


def bi_adde(o, x):
    _list(o, "adde").append(x)
    return None


def bi_insere(o, i, x):
    o = _list(o, "insere")
    i = _int(i, "insere")
    _need(0 <= i <= len(o), "index_extra_fines", f"insert index {i} of {len(o)}")
    o.insert(i, x)
    return None


def bi_remove(o, i):
    o = _list(o, "remove")
    i = _int(i, "remove")
    _need(0 <= i < len(o), "index_extra_fines", f"index {i} of {len(o)}")
    return o.pop(i)


def bi_pars(x, a, b):
    a, b = _int(a, "pars"), _int(b, "pars")
    if isinstance(x, (list, str)):
        a, b = max(0, a), max(0, b)
        return x[a:b]
    raise _h("typus_profanus", "pars takes ORDO or SCRIPTUM")


def bi_habet(t, k):
    return k in _dict(t, "habet")


def bi_accipe(t, k, d):
    return _dict(t, "accipe").get(k, d)


def bi_dele(t, k):
    _dict(t, "dele").pop(k, None)
    return None


def bi_claves(t):
    return list(_dict(t, "claves").keys())


def bi_valores(t):
    return list(_dict(t, "valores").values())


def bi_exemplar(x):
    if isinstance(x, (Rite, NativeRite)):
        raise _h("conversio_impossibilis", "a rite cannot be copied")
    if isinstance(x, Instance):
        return Instance(x.schema, {k: bi_exemplar(v) for k, v in x.values.items()})
    if isinstance(x, list):
        return [bi_exemplar(v) for v in x]
    if isinstance(x, dict):
        return {k: bi_exemplar(v) for k, v in x.items()}
    return x


def bi_idem(a, b):
    return a is b


def bi_elige(c, a, b):
    _need(isinstance(c, bool), "typus_profanus", "elige requires VERITAS")
    return a if c else b


def bi_numerus(x):
    if isinstance(x, bool):
        return 1 if x else 0
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        return int(x)
    if isinstance(x, str):
        s = x.strip()
        r = roman_to_int(s)
        if r is not None:
            return r
        try:
            return int(s)
        except ValueError:
            raise _h("conversio_impossibilis", f"cannot transmute '{x}' to NUMERUS")
    raise _h("conversio_impossibilis",
             f"cannot transmute {genus_valoris(x)} to NUMERUS")


def bi_fractio(x):
    if isinstance(x, bool):
        raise _h("conversio_impossibilis", "VERITAS does not become FRACTIO")
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x)
        except ValueError:
            raise _h("conversio_impossibilis", f"cannot transmute '{x}' to FRACTIO")
    raise _h("conversio_impossibilis",
             f"cannot transmute {genus_valoris(x)} to FRACTIO")


def bi_scriptum(x):
    return scriptum(x)


def bi_veritas(x):
    if isinstance(x, bool):
        return x
    if x == "VERUM":
        return True
    if x == "FALSUM":
        return False
    raise _h("conversio_impossibilis", "only 'VERUM'/'FALSUM' become VERITAS")


def bi_romanum(n):
    n = _int(n, "romanum")
    if not (0 <= n <= 3999):
        raise _h("excessus_numeri", f"{n} exceeds Roman doctrine (0–3999)")
    return int_to_roman(n)


def bi_genus_valoris(x):
    return genus_valoris(x)


def bi_dormi(ms):
    ms = _int(ms, "dormi")
    _need(ms >= 0, "argumentum_pravum", "dormi requires non-negative ms")
    time.sleep(ms / 1000.0)
    return None


def bi_sigilla(x):
    # v0.2 impl: no-op freeze marker is not enforced deeply; documented gap
    return x


BUILTINS = {
    "longitudo": bi_longitudo, "series": bi_series,
    "series_gradu": bi_series_gradu, "adde": bi_adde, "insere": bi_insere,
    "remove": bi_remove, "pars": bi_pars, "habet": bi_habet,
    "accipe": bi_accipe, "dele": bi_dele, "claves": bi_claves,
    "valores": bi_valores, "exemplar": bi_exemplar, "idem": bi_idem,
    "elige": bi_elige, "numerus": bi_numerus, "fractio": bi_fractio,
    "scriptum": bi_scriptum, "veritas": bi_veritas, "romanum": bi_romanum,
    "genus_valoris": bi_genus_valoris, "dormi": bi_dormi, "sigilla": bi_sigilla,
}


# ---------------- standard modules ----------------
def _mod(name, fns: dict, consts: dict | None = None) -> Module:
    ex = {k: NativeRite(f"{name}.{k}", v) for k, v in fns.items()}
    if consts:
        ex.update(consts)
    return Module(name, ex)


def m_mathematica():
    def radix(x):
        v = x if isinstance(x, (int, float)) and not isinstance(x, bool) else None
        _need(v is not None, "typus_profanus", "radix requires a number")
        _need(v >= 0, "argumentum_pravum", "radix of a negative — the Warp beckons")
        return math.sqrt(v)

    def fractio_integra(f):
        _need(isinstance(f, float), "typus_profanus", "fractio_integra requires FRACTIO")
        if math.isnan(f) or math.isinf(f):
            raise _h("conversio_impossibilis", "NaN/inf cannot become NUMERUS")
        return int(f)

    def minimus(o):
        o = _list(o, "minimus")
        _need(len(o) > 0, "argumentum_pravum", "minimus of an empty ORDO")
        return min(o)

    def maximus(o):
        o = _list(o, "maximus")
        _need(len(o) > 0, "argumentum_pravum", "maximus of an empty ORDO")
        return max(o)

    return _mod("mathematica", {
        "radix": radix, "potentia": lambda b, e: b ** e,
        "modulus": lambda x: abs(x), "minimus": minimus, "maximus": maximus,
        "rotundo": lambda f: float(round(f)), "solum": lambda f: math.floor(f),
        "tectum": lambda f: math.ceil(f), "fractio_integra": fractio_integra,
        "sinus": math.sin, "cosinus": math.cos, "tangens": math.tan,
        "logarithmus": math.log, "exponens": math.exp,
    }, {"PI": math.pi, "E": math.e, "NAN": float("nan"),
        "INFINITUM": float("inf"), "MAXIMUS_NUMERUS": INT64_MAX,
        "MINIMUS_NUMERUS": INT64_MIN})


def m_scriptura():
    return _mod("scriptura", {
        "maiuscula": lambda s: _str(s, "maiuscula").upper(),
        "minuscula": lambda s: _str(s, "minuscula").lower(),
        "divide": lambda s, sep: _str(s, "divide").split(_str(sep, "divide")),
        "coniunge": lambda o, sep: _str(sep, "coniunge").join(
            _str(x, "coniunge element") for x in _list(o, "coniunge")),
        "substitue": lambda s, a, b: _str(s, "substitue").replace(a, b),
        "incipit": lambda s, p: _str(s, "incipit").startswith(p),
        "desinit": lambda s, p: _str(s, "desinit").endswith(p),
        "continet": lambda s, p: p in _str(s, "continet"),
        "purga": lambda s: _str(s, "purga").strip(),
        "imple_sinistra": lambda s, n, c: _str(s, "imple_sinistra").rjust(n, c),
        "inveni": lambda s, sub: _str(s, "inveni").find(sub),
        "mensura_octetorum": lambda s: len(_str(s, "mensura").encode()),
        "ad_octetos": lambda s: list(_str(s, "ad_octetos").encode()),
        "ex_octetis": _ex_octetis,
    })


def _ex_octetis(o):
    try:
        return bytes(_list(o, "ex_octetis")).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as e:
        raise _h("forma_prava", f"profane octets: {e}")


def m_ordo_opera(call):
    def transmuta(o, f):
        return [call(f, [x]) for x in _list(o, "transmuta")]

    def excerne(o, f):
        out = []
        for x in _list(o, "excerne"):
            keep = call(f, [x])
            _need(isinstance(keep, bool), "typus_profanus",
                  "excerne rite must return VERITAS")
            if keep:
                out.append(x)
        return out

    def redige(o, f, init):
        acc = init
        for x in _list(o, "redige"):
            acc = call(f, [acc, x])
        return acc

    def ordina(o):
        o = _list(o, "ordina")
        try:
            return sorted(o)
        except TypeError:
            raise _h("typus_profanus", "ordina over mixed types")

    def ordina_per(o, f):
        return sorted(_list(o, "ordina_per"), key=lambda x: call(f, [x]))

    def summa(o):
        o = _list(o, "summa")
        acc = 0
        for x in o:
            acc = acc + x
        return acc

    def quisque(o, f):
        return all(call(f, [x]) for x in _list(o, "quisque"))

    def ullus(o, f):
        return any(call(f, [x]) for x in _list(o, "ullus"))

    def compone(a, b):
        return [list(t) for t in zip(_list(a, "compone"), _list(b, "compone"))]

    return _mod("ordo_opera", {
        "transmuta": transmuta, "excerne": excerne, "redige": redige,
        "ordina": ordina, "ordina_per": ordina_per,
        "inverte": lambda o: list(reversed(_list(o, "inverte"))),
        "summa": summa, "quisque": quisque, "ullus": ullus, "compone": compone,
    })


def m_tempus():
    return _mod("tempus", {
        "nunc": lambda: int(time.time() * 1000),
        "nunc_monotonicum": lambda: time.monotonic_ns(),
        "data_scriptum": lambda ms, fmt: time.strftime(
            fmt, time.gmtime(_int(ms, "data_scriptum") / 1000)),
    })


def m_archivum():
    def lege(via):
        try:
            with open(_str(via, "lege"), encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise _h("archivum_ignotum", f"no scroll at '{via}'")
        except OSError as e:
            raise _h("archivum_clausum", str(e))

    def scribe(via, textum):
        try:
            with open(_str(via, "scribe"), "w", encoding="utf-8") as f:
                f.write(_str(textum, "scribe"))
            return None
        except OSError as e:
            raise _h("archivum_clausum", str(e))

    def attinge(via, textum):
        try:
            with open(via, "a", encoding="utf-8") as f:
                f.write(textum)
            return None
        except OSError as e:
            raise _h("archivum_clausum", str(e))

    def enumera(via):
        try:
            return sorted(os.listdir(via))
        except FileNotFoundError:
            raise _h("archivum_ignotum", f"no directory at '{via}'")
        except OSError as e:
            raise _h("archivum_clausum", str(e))

    return _mod("archivum", {
        "lege": lege, "scribe": scribe, "attinge": attinge,
        "existit": lambda via: os.path.exists(via),
        "dele": lambda via: (os.remove(via), None)[1],
        "enumera": enumera,
        "crea_directorium": lambda via: (os.makedirs(via, exist_ok=True), None)[1],
    })


def m_imperium(argv: list[str]):
    def ambitus(nomen):
        v = os.environ.get(_str(nomen, "ambitus"))
        if v is None:
            raise _h("clavis_ignota", f"env var '{nomen}' is not set")
        return v

    def impera(mandatum):
        m = [_str(x, "impera") for x in _list(mandatum, "impera")]
        try:
            r = subprocess.run(m, capture_output=True, text=True)
        except FileNotFoundError:
            raise _h("archivum_ignotum", f"no such command: {m[0]}")
        return {"codex": r.returncode, "exitus": r.stdout, "error": r.stderr}

    return _mod("imperium", {
        "argumenta": lambda: list(argv),
        "ambitus": ambitus,
        "ambitus_aut": lambda n, d: os.environ.get(n, d),
        "exi": lambda c: sys.exit(_int(c, "exi")),
        "impera": impera,
    })


def m_machina_cogitans():
    def pete(url):
        try:
            with urllib.request.urlopen(_str(url, "pete"), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            raise _h("responsum_pravum", f"HTTP {e.code} from {url}", gradus=e.code)
        except (urllib.error.URLError, TimeoutError) as e:
            raise _h("retis_fractum", f"the noosphere is silent: {e}")

    def mitte(url, corpus):
        try:
            req = urllib.request.Request(url, data=corpus.encode(), method="POST")
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            raise _h("responsum_pravum", f"HTTP {e.code} from {url}", gradus=e.code)
        except (urllib.error.URLError, TimeoutError) as e:
            raise _h("retis_fractum", f"the noosphere is silent: {e}")

    return _mod("machina_cogitans", {"pete": pete, "mitte": mitte})


def m_codex_json():
    def lege(s):
        try:
            return json.loads(_str(s, "codex_json.lege"))
        except json.JSONDecodeError as e:
            raise _h("forma_prava", f"profane JSON: {e}")

    def _clean(v):
        if isinstance(v, Instance):
            return {k: _clean(x) for k, x in v.values.items()}
        if isinstance(v, (Rite, NativeRite)):
            raise _h("conversio_impossibilis", "a rite cannot become JSON")
        if isinstance(v, list):
            return [_clean(x) for x in v]
        if isinstance(v, dict):
            return {k: _clean(x) for k, x in v.items()}
        return v

    return _mod("codex_json", {
        "lege": lege,
        "scribe": lambda v: json.dumps(_clean(v), ensure_ascii=False),
        "scribe_ornatum": lambda v: json.dumps(_clean(v), ensure_ascii=False,
                                               indent=4),
    })


def m_fortuna():
    def inter(a, b):
        return random.randint(_int(a, "inter"), _int(b, "inter"))

    def elige_sortem(o):
        o = _list(o, "elige_sortem")
        _need(len(o) > 0, "argumentum_pravum", "the lot cannot fall on nothing")
        return random.choice(o)

    return _mod("fortuna", {
        "inter": inter, "fractio_fortunae": random.random,
        "elige_sortem": elige_sortem,
        "misce": lambda o: (random.shuffle(_list(o, "misce")), None)[1],
        "semen": lambda n: (random.seed(n), None)[1],
    })


def m_notarius():
    state = {"gradus": os.environ.get("GOTHICA_NOTARIUS", "info")}
    order = {"debug": 0, "info": 1, "monitum": 2, "error": 3}

    def nota(gradus, nuntius):
        if order.get(gradus, 1) >= order.get(state["gradus"], 1):
            ts = time.strftime("%H:%M:%S", time.gmtime())
            print(f"[{gradus.upper()}] {ts} — {scriptum(nuntius)}",
                  file=sys.stderr)
        return None

    return _mod("notarius", {
        "nota": nota,
        "debug": lambda n: nota("debug", n),
        "info": lambda n: nota("info", n),
        "monitum": lambda n: nota("monitum", n),
        "error": lambda n: nota("error", n),
        "gradus_pone": lambda g: (state.__setitem__("gradus", g), None)[1],
    })


def m_probatio(call):
    def adfirma(cond, nuntius):
        _need(isinstance(cond, bool), "typus_profanus", "adfirma requires VERITAS")
        if not cond:
            raise _h("probatio_fracta", scriptum(nuntius))
        return None

    def adfirma_aequalia(actus, exspectatus, nuntius):
        if actus != exspectatus:
            raise _h("probatio_fracta",
                     f"{scriptum(nuntius)} — got {scriptum(actus)}, "
                     f"awaited {scriptum(exspectatus)}")
        return None

    def adfirma_heresim(genus, ritus):
        try:
            call(ritus, [])
        except Heresis as h:
            if h.major:
                raise
            if h.genus == genus:
                return None
            raise _h("probatio_fracta",
                     f"awaited heresy '{genus}', got '{h.genus}'")
        raise _h("probatio_fracta", f"awaited heresy '{genus}', none arose")

    def praetermitte(nuntius):
        raise _h("probatio_praetermissa", scriptum(nuntius))

    return _mod("probatio", {
        "adfirma": adfirma, "adfirma_aequalia": adfirma_aequalia,
        "adfirma_heresim": adfirma_heresim, "praetermitte": praetermitte,
    })


def m_fenestra(call):
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError as exc:
        raise _h("fenestra_indisponibilis",
                 f"the Machine Spirit lacks a windowing cultus ({exc})")

    _COG = {
        "bg": "#120c08",
        "panel": "#1e1410",
        "brass": "#b8860b",
        "gold": "#d4af37",
        "parchment": "#e8dcc8",
        "rust": "#6b2f1a",
        "phosphor": "#9acd32",
        "ink": "#2b1810",
        "font": ("Menlo", 11),
        "font_bold": ("Menlo", 11, "bold"),
        "font_title": ("Menlo", 13, "bold"),
    }

    _windows: dict[str, dict] = {}
    _seq = 0

    def _new_id() -> str:
        nonlocal _seq
        _seq += 1
        return f"fenestra:{_seq}"

    def _win(wid):
        w = _windows.get(_str(wid, "fenestra"))
        _need(w is not None, "vas_ignotum", f"unknown fenestra '{wid}'")
        return w

    def _style_cogitator(root, frame):
        c = _COG
        root.configure(bg=c["bg"])
        root.geometry("520x560")
        root.minsize(480, 520)
        try:
            root.iconphoto(False, tk.PhotoImage(
                data="R0lGODlhEAAQAIABAAAAAP///yH5BAEAAAAALAAAAAAQABAAAAIxhI+py+0Po5y02ouz3rz7"
                     "D4biSJbmiabqyrbuC8fyTNf2jef6zvf+DwwKh8SiHgAAOw=="))
        except tk.TclError:
            pass
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Cog.TFrame", background=c["panel"])
        style.configure("Cog.TLabel", background=c["panel"], foreground=c["gold"],
                        font=c["font"])
        style.configure("CogTitle.TLabel", background=c["panel"],
                        foreground=c["brass"], font=c["font_title"])
        style.configure("CogSub.TLabel", background=c["panel"],
                        foreground=c["parchment"], font=c["font"])
        style.configure("Cog.TButton", background=c["rust"], foreground=c["parchment"],
                        font=c["font_bold"], padding=(12, 8), borderwidth=2)
        style.map("Cog.TButton",
                  background=[("active", c["brass"]), ("pressed", c["gold"])],
                  foreground=[("active", c["bg"])])
        style.configure("Cog.TCombobox", fieldbackground=c["ink"],
                        background=c["rust"], foreground=c["parchment"],
                        arrowcolor=c["gold"])
        style.configure("Cog.TEntry", fieldbackground=c["ink"],
                        foreground=c["phosphor"], insertcolor=c["phosphor"])
        frame.configure(style="Cog.TFrame", padding=16)
        banner = ttk.Label(
            frame,
            text="⚙ COGITATOR ARITHMETICA ⚙\nAdeptus Administratum — ledger sanctum",
            style="CogTitle.TLabel", justify="center")
        banner.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        sep = tk.Frame(frame, height=2, bg=c["brass"])
        sep.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        return 2  # next row after banner + separator

    def crea(titulus):
        wid = _new_id()
        root = tk.Tk()
        root.title(_str(titulus, "crea"))
        root.configure(bg="#1a1210")
        frame = ttk.Frame(root, padding=12)
        frame.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        _windows[wid] = {
            "root": root, "frame": frame, "row": 0,
            "vars": {}, "output": None, "theme": None,
        }
        return wid

    def crea_cogitator(titulus):
        wid = _new_id()
        root = tk.Tk()
        root.title(_str(titulus, "crea_cogitator"))
        frame = ttk.Frame(root)
        frame.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        start_row = _style_cogitator(root, frame)
        _windows[wid] = {
            "root": root, "frame": frame, "row": start_row,
            "vars": {}, "output": None, "theme": "cogitator",
        }
        return wid

    def _label_style(w):
        return "Cog.TLabel" if w.get("theme") == "cogitator" else "TLabel"

    def rotula(wid, nomen, optiones):
        w = _win(wid)
        nm = _str(nomen, "rotula")
        opts = _list(optiones, "rotula")
        row = w["row"]
        ttk.Label(w["frame"], text=nm, style=_label_style(w)).grid(
            row=row, column=0, sticky="w", pady=4)
        var = tk.StringVar(value=_str(opts[0], "rotula default") if opts else "")
        w["vars"][nm] = var
        box_kw = {"textvariable": var,
                  "values": [_str(x, "rotula opt") for x in opts],
                  "state": "readonly", "width": 28}
        if w.get("theme") == "cogitator":
            box_kw["style"] = "Cog.TCombobox"
        box = ttk.Combobox(w["frame"], **box_kw)
        box.grid(row=row, column=1, sticky="ew", pady=4)
        w["row"] += 1

    def campus(wid, nomen, defectus):
        w = _win(wid)
        nm = _str(nomen, "campus")
        row = w["row"]
        ttk.Label(w["frame"], text=nm, style=_label_style(w)).grid(
            row=row, column=0, sticky="w", pady=4)
        var = tk.StringVar(value=_str(defectus, "campus"))
        w["vars"][nm] = var
        entry_kw = {"textvariable": var, "width": 30}
        if w.get("theme") == "cogitator":
            entry_kw["style"] = "Cog.TEntry"
        ttk.Entry(w["frame"], **entry_kw).grid(
            row=row, column=1, sticky="ew", pady=4)
        w["row"] += 1

    def nuntius(wid, textum):
        w = _win(wid)
        txt = _str(textum, "nuntius")
        c = _COG
        if w["output"] is None:
            row = w["row"]
            if w.get("theme") == "cogitator":
                ttk.Label(w["frame"], text="— SCRIBEUM —",
                          style="CogSub.TLabel").grid(
                    row=row, column=0, columnspan=2, sticky="w", pady=(8, 2))
                row += 1
            out = tk.Text(
                w["frame"], height=7, width=48, wrap="word",
                bg=c["ink"] if w.get("theme") == "cogitator" else "#2b1810",
                fg=c["phosphor"] if w.get("theme") == "cogitator" else "#e8dcc8",
                insertbackground=c["phosphor"],
                relief="sunken", borderwidth=3,
                font=c["font"])
            out.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=8)
            w["frame"].rowconfigure(row, weight=1)
            w["output"] = out
            w["row"] += 1
        w["output"].delete("1.0", "end")
        w["output"].insert("1.0", txt)

    def lege_campo(wid, nomen):
        w = _win(wid)
        nm = _str(nomen, "lege_campo")
        var = w["vars"].get(nm)
        _need(var is not None, "clavis_ignota", f"no field '{nm}' on fenestra")
        return var.get()

    def lege_rotula(wid, nomen):
        return lege_campo(wid, nomen)

    def pulsor(wid, titulus, ritus):
        w = _win(wid)
        row = w["row"]

        def _invoke():
            try:
                call(ritus, [])
            except Heresis as h:
                nuntius(wid, f"⚙ HERESY [{h.genus}] {h.nuntius}")
            except Exception as exc:
                nuntius(wid, f"⚙ {exc}")

        btn_kw = {"text": _str(titulus, "pulsor"), "command": _invoke}
        if w.get("theme") == "cogitator":
            btn_kw["style"] = "Cog.TButton"
        ttk.Button(w["frame"], **btn_kw).grid(
            row=row, column=0, columnspan=2, pady=12, sticky="ew")
        w["row"] += 1

    def circulo(wid):
        w = _win(wid)
        w["root"].mainloop()
        return None

    return _mod("fenestra", {
        "crea": crea, "crea_cogitator": crea_cogitator,
        "rotula": rotula, "campus": campus, "nuntius": nuntius,
        "lege_campo": lege_campo, "lege_rotula": lege_rotula,
        "pulsor": pulsor, "circulo": circulo,
    })


FABRICA_FORBIDDEN = {"fortuna", "fenestra", }


def stdlib_module(name: str, interp) -> Module | None:
    call = interp.call_value
    table = {
        "mathematica": m_mathematica,
        "scriptura": m_scriptura,
        "ordo_opera": lambda: m_ordo_opera(call),
        "tempus": m_tempus,
        "archivum": m_archivum,
        "imperium": lambda: m_imperium(interp.argv),
        "machina_cogitans": m_machina_cogitans,
        "codex_json": m_codex_json,
        "fortuna": m_fortuna,
        "notarius": m_notarius,
        "probatio": lambda: m_probatio(call),
        "fenestra": lambda: m_fenestra(call),
    }
    fn = table.get(name)
    return fn() if fn else None
