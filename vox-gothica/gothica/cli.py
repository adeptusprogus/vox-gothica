"""The gothica toolchain (docs 12)."""
from __future__ import annotations
import argparse
import glob
import os
import sys
from . import __version__
from .heresiae import Heresis, Profanatio, IraMachinae
from .parser import parse_source
from .interpres import Interpres
from .valores import Rite
from . import fabrica as fab
from .diagnostica import render_profanatio, render_heresis, render_ira


def _say(msg, args):
    if not args.silens:
        print(msg)


def _find_root(start: str) -> str:
    """Project root = nearest ancestor with litania.toml, else start."""
    d = os.path.abspath(start)
    probe = d
    while True:
        if os.path.exists(os.path.join(probe, "litania.toml")):
            return probe
        parent = os.path.dirname(probe)
        if parent == probe:
            return d
        probe = parent


def _load(path: str):
    if not os.path.exists(path):
        print(f"⚙ no scroll at '{path}'", file=sys.stderr)
        sys.exit(2)
    with open(path, encoding="utf-8") as f:
        return parse_source(f.read(), path)


def _postulata(args) -> dict:
    out = {}
    for kv in (args.postulatum or []):
        if "=" not in kv:
            print(f"⚙ -postulatum expects k=v, got '{kv}'", file=sys.stderr)
            sys.exit(2)
        k, v = kv.split("=", 1)
        out[k] = v
    return out


def cmd_invoco(args) -> int:
    prog = _load(args.file)
    if prog.mode != "CANTICUM":
        print(f"⚙ invoco requires a CANTICUM ('{prog.name}' is a {prog.mode}; "
              f"use auguro/consecro for fabricae)", file=sys.stderr)
        return 2
    interp = Interpres(argv=args.args or [],
                       max_depth=args.profunditas,
                       root_dir=_find_root(os.path.dirname(
                           os.path.abspath(args.file))))
    interp.run_program(prog)
    _say("++ The rite concludes. The Machine Spirit is appeased. ++", args)
    return 0


def _consecrate(args, plan_only=False, destroy=False, emit_only=False) -> int:
    prog = _load(args.file)
    if prog.mode != "FABRICA":
        print(f"⚙ this command requires a FABRICA ('{prog.name}' is a "
              f"{prog.mode})", file=sys.stderr)
        return 2
    root = os.path.dirname(os.path.abspath(args.file)) or "."
    interp = Interpres(mode="FABRICA", root_dir=root)
    state = fab.FabricaState(prog.name)
    state.postulata = _postulata(args)
    interp.fabrica = state
    interp.run_program(prog)
    path = fab.write_json(state, root)
    _say(f"++ Manifest transcribed: {path} ++", args)
    n = len(state.resources)
    if emit_only:
        _say(f"++ {_roman(n)} resource(s) await the word. Emit-only rite "
             f"concludes. ++", args)
        return 0
    cwd = os.path.dirname(path)
    if destroy:
        if not args.fiat:
            word = input("Speak the word to unmake all (EXTERMINATUS): ")
            if word.strip() != "EXTERMINATUS":
                _say("++ The word was not spoken. Nothing burns today. ++", args)
                return 0
        code = fab.terraform(["destroy", "-auto-approve"], cwd)
        if code != 0:
            raise IraMachinae("terraform destroy failed")
        _say("++ EXTERMINATUS delivered. The ground is glass. ++", args)
        return 0
    code = fab.terraform(["plan", "-detailed-exitcode"], cwd)
    if code == 1:
        raise IraMachinae("terraform plan failed")
    if plan_only:
        if args.exi_si_mutatio and code == 2:
            _say("++ The augury shows change. ++", args)
            return 1
        _say("++ The augury is complete. ++", args)
        return 0
    if not args.fiat:
        word = input("Speak the word to make it flesh (FIAT): ")
        if word.strip() != "FIAT":
            _say("++ The word was not spoken. The manifest sleeps. ++", args)
            return 0
    code = fab.terraform(["apply", "-auto-approve"], cwd)
    if code != 0:
        raise IraMachinae("terraform apply failed")
    _say(f"++ {_roman(n)} machine(s) raised. The manifest is made flesh. "
         f"Praise the Omnissiah. ++", args)
    return 0


def _roman(n):
    from .lexicon import int_to_roman
    try:
        return int_to_roman(n)
    except ValueError:
        return str(n)


def cmd_proba(args) -> int:
    files = sorted(glob.glob(os.path.join(args.dir, "*_proba.vg")))
    if not files:
        print(f"⚙ no probationes found in {args.dir}", file=sys.stderr)
        return 1
    total = passed = failed = skipped = 0
    for path in files:
        prog = _load(path)
        interp = Interpres(root_dir=_find_root(
            os.path.dirname(os.path.dirname(os.path.abspath(path))) or "."))
        if prog.mode != "LITANIA":
            print(f"⚙ {path}: probationes must be LITANIA", file=sys.stderr)
            return 2
        interp.cur_file = path
        from .valores import Env, Cell
        env = Env()
        interp._hoist(prog.body, env)
        for st in prog.body:
            interp.exec_stmt(st, env)
        for name, cell in env.vars.items():
            if not name.startswith("proba_") or not isinstance(cell.value, Rite):
                continue
            if args.unus and name != args.unus:
                continue
            total += 1
            try:
                interp.call_value(cell.value, [])
                print(f"  SANCTUS        {name}")
                passed += 1
            except Heresis as h:
                if h.genus == "probatio_praetermissa":
                    print(f"  PRAETERMISSUS  {name} — {h.nuntius}")
                    skipped += 1
                else:
                    print(f"  HERETICUS      {name} — [{h.genus}] {h.nuntius}")
                    failed += 1
    print(f"\n++ {passed} sanctus, {failed} hereticus, {skipped} praetermissus "
          f"of {total} ++")
    return 1 if failed else 0


def cmd_versio(args) -> int:
    print(f"gothica {__version__} — Vox Gothica toolchain. "
          f"Praise the Omnissiah.")
    return 0


def main(argv=None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--silens", action="store_true")
    common.add_argument("--profanum", action="store_true",
                        help="plain machine-readable diagnostics")

    ap = argparse.ArgumentParser(
        prog="gothica",
        description="Vox Gothica — the High Gothic language of canticles "
                    "and fabricae.")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("invoco", help="run a CANTICUM", parents=[common])
    p.add_argument("file")
    p.add_argument("--profunditas", type=int, default=4000)
    p.add_argument("args", nargs="*")

    for name, hlp in (("auguro", "plan"), ("consecro", "apply"),
                      ("exterminatus", "destroy"),
                      ("scribe-solum", "emit tf.json only")):
        p = sub.add_parser(name, help=f"FABRICA: {hlp}", parents=[common])
        p.add_argument("file")
        p.add_argument("-postulatum", action="append", dest="postulatum",
                       metavar="k=v")
        p.add_argument("--fiat", action="store_true",
                       help="skip confirmation (not honored by exterminatus)")
        p.add_argument("--exi-si-mutatio", action="store_true",
                       dest="exi_si_mutatio")

    p = sub.add_parser("proba", help="run probationes", parents=[common])
    p.add_argument("--dir", default="probationes")
    p.add_argument("--unus")

    sub.add_parser("versio", help="print version", parents=[common])

    args = ap.parse_args(argv)
    if args.cmd is None:
        ap.print_help()
        return 0
    try:
        if args.cmd == "invoco":
            return cmd_invoco(args)
        if args.cmd == "auguro":
            return _consecrate(args, plan_only=True)
        if args.cmd == "consecro":
            return _consecrate(args)
        if args.cmd == "exterminatus":
            args.fiat = False   # solemnity is non-negotiable
            return _consecrate(args, destroy=True)
        if args.cmd == "scribe-solum":
            return _consecrate(args, emit_only=True)
        if args.cmd == "proba":
            return cmd_proba(args)
        if args.cmd == "versio":
            return cmd_versio(args)
    except Profanatio as p_:
        print(render_profanatio(p_, args.profanum), file=sys.stderr)
        return 2
    except Heresis as h:
        print(render_heresis(h, args.profanum), file=sys.stderr)
        return 1
    except IraMachinae as e:
        print(render_ira(e, args.profanum), file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("\n++ The rite was interrupted by mortal hands. ++",
              file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
