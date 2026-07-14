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
from .litaniae import adfero as lit_adfero
from .litaniae import initium as lit_initium
from .litaniae import expello as lit_expello
from .litaniae import renovo as lit_renovo
from .litaniae import offero as lit_offero
from .litaniae import librarium as lit_librarium
from .litaniae.manifestum import load_manifest, manifest_path
from . import purga as lit_purga
from . import lustro as lit_lustro
from . import censura as lit_censura
from . import codex as lit_codex
from . import speculum as lit_speculum
from .diagnostic_records import lint as lint_record, censura as censura_record
import json


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


def cmd_initium(args) -> int:
    root = os.path.abspath(args.dir or ".")
    try:
        created = lit_initium.scaffold(root, args.via, litania=args.litania)
    except FileExistsError as exc:
        print(f"⚙ initium refused: {exc} already exists", file=sys.stderr)
        return 2
    for name in created:
        _say(f"  ++ inscribed {name}", args)
    kind = "litania" if args.litania else "project"
    _say(f"++ initium complete — {kind} scaffold at {root} ++", args)
    _say("++ Next: gothica proba --dir probationes ++", args)
    return 0


def cmd_adfero(args) -> int:
    root = _find_root(os.path.abspath(args.dir or "."))
    if not os.path.isfile(manifest_path(root)):
        print(f"⚙ no litania.toml under {root}", file=sys.stderr)
        return 2
    if args.via:
        constraint = args.constraint or "^0.1"
        lit_adfero.append_dependency(root, args.via, constraint)
        _say(f"++ dependency recorded: {args.via} {constraint} ++", args)
    load_manifest(manifest_path(root))
    entries = lit_adfero.sync(root)
    if entries:
        for e in entries:
            _say(f"  ++ materialized {e.via}@{e.versio} ++", args)
    else:
        _say("++ no remote dependencies — lockfile cleared ++", args)
    _say(f"++ adfero complete — litania.claustrum updated ++", args)
    return 0


def cmd_expello(args) -> int:
    root = _find_root(os.path.abspath(args.dir or "."))
    lit_expello.expello(root, args.via)
    _say(f"++ expello complete — '{args.via}' cast out ++", args)
    return 0


def cmd_renovo(args) -> int:
    root = _find_root(os.path.abspath(args.dir or "."))
    bumps = lit_renovo.renovo(root, args.via)
    if bumps:
        for dep, old, new in bumps:
            _say(f"  ++ {dep}: {old} → {new} ++", args)
    else:
        _say("++ all constraints already at newest compatible versions ++", args)
    _say("++ renovo complete ++", args)
    return 0


def cmd_offero(args) -> int:
    root = _find_root(os.path.abspath(args.dir or "."))
    result = lit_offero.offero(
        root, push=not args.no_push, fiat=args.fiat,
    )
    _say(f"++ offero sanctus — {result['via']}@{result['versio']} "
         f"({result['tag']}) ++", args)
    if not args.no_push:
        _say(f"++ tag pushed to origin ++", args)
    _say("++ Librarium: open a PR to index this litania ++", args)
    _say(f"   {result['librarium']}", args)
    return 0


def cmd_librarium(args) -> int:
    refresh = args.renova
    if args.librarium_cmd == "quaere":
        hits = lit_librarium.quaere(args.term, refresh=refresh)
        if not hits:
            print(f"⚙ no litaniae match '{args.term}' in the Librarium",
                  file=sys.stderr)
            return 1
        _say(f"++ quaere — {len(hits)} hit(s) for '{args.term}' ++", args)
        for entry in hits:
            _say(lit_librarium.format_quaere_line(entry), args)
        return 0
    if args.librarium_cmd == "inspice":
        data = lit_librarium.inspice(args.via, refresh=refresh)
        _say(lit_librarium.format_inspice(data), args)
        if not data["indexed"] and not data["versiones"]:
            print(f"⚙ '{args.via}' is unknown to the Librarium and has no "
                  f"reachable tags", file=sys.stderr)
            return 4
        return 0
    return 2


def cmd_purga(args) -> int:
    target = args.path or "."
    changed, total = lit_purga.purga(
        target,
        check_only=args.proba,
        latinizat=args.latinizat,
    )
    if total == 0:
        print(f"⚙ no .vg scrolls at '{target}'", file=sys.stderr)
        return 2
    if args.proba:
        if changed:
            _say(f"++ purga would reform {changed} of {total} scroll(s) ++", args)
            return 1
        _say(f"++ {total} scroll(s) already canonical ++", args)
        return 0
    _say(f"++ purga cleansed {changed} of {total} scroll(s) ++", args)
    return 0


def cmd_lustro(args) -> int:
    target = args.path or "."
    hits = lit_lustro.lustro(target, serius=args.serius)
    if not hits:
        _say("++ lustro finds no blemish — the scrolls are worthy ++", args)
        return 0
    if args.profanum:
        for h in hits:
            print(json.dumps(lint_record(h)), flush=True)
        return 1
    for h in hits:
        loc = f"{h.archivum}:{h.line}" if h.archivum else str(h.line)
        _say(f"  ⚠ {h.code}  {loc} — {h.message}", args)
    _say(f"++ lustro: {len(hits)} admonition(s) ++", args)
    return 1


def cmd_censura(args) -> int:
    target = args.path or "."
    root = _find_root(os.path.abspath(target if os.path.isdir(target)
                                      else os.path.dirname(target) or "."))
    hits = lit_censura.censura(target, root_dir=root)
    if not hits:
        _say("++ censura finds no profanation — the scrolls are sound ++", args)
        return 0
    if args.profanum:
        for h in hits:
            print(json.dumps(censura_record(h)), flush=True)
        return 1
    for h in hits:
        loc = f"{h.archivum}:{h.line}" if h.archivum else str(h.line)
        _say(f"  ⚙ {h.code} [{h.genus}]  {loc} — {h.message}", args)
    _say(f"++ censura: {len(hits)} finding(s) ++", args)
    return 1


def cmd_speculum(args) -> int:
    records = lit_speculum.analyze(args.file, root_dir=_find_root(
        os.path.dirname(os.path.abspath(args.file)) or "."))
    if not records:
        _say("++ speculum finds no blemish — the scroll reflects truly ++", args)
        return 0
    for rec in records:
        print(json.dumps(rec), flush=True)
    return 1


def cmd_codex(args) -> int:
    if args.quaesitum:
        hits = lit_codex.quaere(args.quaesitum)
        if not hits:
            print(f"⚙ codex finds no mention of '{args.quaesitum}'",
                  file=sys.stderr)
            _say(f"++ see {lit_codex.CODEX_URL} ++", args)
            return 1
        _say(f"++ codex quaere — {len(hits)} hit(s) for "
             f"'{args.quaesitum}' ++", args)
        for h in hits:
            _say(f"  {h.page}:{h.line}  {h.excerpt}", args)
        return 0
    pages = lit_codex.index_pages()
    if not pages:
        print("⚙ local codex not found — open the hosted sanctum",
              file=sys.stderr)
        _say(f"++ {lit_codex.CODEX_URL} ++", args)
        return 2
    _say("++ codex index ++", args)
    for name, title in pages:
        _say(f"  {name}  — {title}", args)
    _say(f"++ hosted: {lit_codex.CODEX_URL} ++", args)
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

    p = sub.add_parser("initium", help="scaffold a project or litania",
                       parents=[common])
    p.add_argument("--dir", default=".", help="target directory")
    p.add_argument("--via", required=True,
                   help="litania.via (e.g. github.com/you/my-canticle)")
    p.add_argument("--litania", action="store_true",
                   help="scaffold a publishable litania (no principium.vg)")

    p = sub.add_parser("adfero", help="resolve deps into litaniae/",
                       parents=[common])
    p.add_argument("--dir", default=".", help="project root")
    p.add_argument("via", nargs="?", help="add dependency via before resolve")
    p.add_argument("--constraint", default="^0.1",
                   help="version constraint when adding a via")

    p = sub.add_parser("expello", help="remove a dependency",
                       parents=[common])
    p.add_argument("--dir", default=".", help="project root")
    p.add_argument("via", help="dependency to remove")

    p = sub.add_parser("renovo", help="raise constraints to newest compatible",
                       parents=[common])
    p.add_argument("--dir", default=".", help="project root")
    p.add_argument("via", nargs="?", help="single dependency to renew")

    p = sub.add_parser("offero", help="publish litania (tag + Librarium PR)",
                       parents=[common])
    p.add_argument("--dir", default=".", help="litania repository root")
    p.add_argument("--fiat", action="store_true",
                   help="skip FIAT confirmation before git push")
    p.add_argument("--no-push", action="store_true",
                   help="validate and tag locally only")

    lib = sub.add_parser("librarium", help="search and inspect the Librarium",
                         parents=[common])
    lib_sub = lib.add_subparsers(dest="librarium_cmd", required=True)
    p = lib_sub.add_parser("quaere", help="search index by name or topic",
                           parents=[common])
    p.add_argument("term", help="search term")
    p.add_argument("--renova", action="store_true",
                   help="refresh remote index cache before search")
    p = lib_sub.add_parser("inspice", help="show litania metadata and tags",
                           parents=[common])
    p.add_argument("via", help="litania via (github.com/owner/repo)")
    p.add_argument("--renova", action="store_true",
                   help="refresh remote index cache before inspect")

    p = sub.add_parser("purga", help="format .vg to canonical style",
                       parents=[common])
    p.add_argument("path", nargs="?", help="file or directory")
    p.add_argument("--proba", action="store_true",
                   help="check-only — exit I if reform would be needed")
    p.add_argument("--latinizat", action="store_true",
                   help="rewrite Terraform attr names to Latin aliases (FABRICA)")

    p = sub.add_parser("lustro", help="lint .vg scrolls", parents=[common])
    p.add_argument("path", nargs="?", help="file or directory")
    p.add_argument("--serius", action="store_true",
                   help="disable jocular L-VII; enable strict elige (L-X)")

    p = sub.add_parser("censura", help="static-check .vg scrolls (M5)",
                       parents=[common])
    p.add_argument("path", nargs="?", help="file or directory")

    p = sub.add_parser("speculum", help="LSP diagnostics JSONL (lustro+censura)",
                       parents=[common])
    p.add_argument("file", help=".vg scroll to analyze")

    p = sub.add_parser("codex", help="search or list Codex documentation",
                       parents=[common])
    p.add_argument("quaesitum", nargs="?", help="search term")

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
        if args.cmd == "initium":
            return cmd_initium(args)
        if args.cmd == "adfero":
            return cmd_adfero(args)
        if args.cmd == "expello":
            return cmd_expello(args)
        if args.cmd == "renovo":
            return cmd_renovo(args)
        if args.cmd == "offero":
            return cmd_offero(args)
        if args.cmd == "librarium":
            return cmd_librarium(args)
        if args.cmd == "purga":
            return cmd_purga(args)
        if args.cmd == "lustro":
            return cmd_lustro(args)
        if args.cmd == "censura":
            return cmd_censura(args)
        if args.cmd == "speculum":
            return cmd_speculum(args)
        if args.cmd == "codex":
            return cmd_codex(args)
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
