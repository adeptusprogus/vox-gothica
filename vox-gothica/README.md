# gothica — Vox Gothica toolchain

Reference implementation of **Vox Gothica**, the High Gothic programming language for canticles (programs) and fabricae (infrastructure → Terraform). Language docs live in the `vox-gothica/` documentation set; this repo is the working toolchain.

Pure Python ≥ 3.10, **zero dependencies**.

```
AVE OMNISSIAH.
CANTICUM "salutatio".

VOCIFERO "Ave, Imperium!"
```

```console
$ gothica invoco salutatio.vg
Ave, Imperium!
++ The rite concludes. The Machine Spirit is appeased. ++
```

## Install

**macOS / Linux**

```console
$ ./install.sh          # pipx/pip install → `gothica` command
$ ./install.sh --pyz    # or: single-file ~/.local/bin/gothica (zipapp)
```

**Windows**

```console
> powershell -ExecutionPolicy Bypass -File install.ps1
```

**Docker (for fabricae — terraform included)**

```console
$ docker build -t vox-gothica .
$ docker run --rm -v "$PWD:/opus" vox-gothica auguro /opus/fabrica.vg
$ docker run --rm -it -v "$PWD:/opus" \
    -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
    vox-gothica consecro /opus/fabrica.vg --fiat
```

The image is `python:3.12-alpine` + the official terraform binary + gothica; it runs as an unprivileged user with `/opus` as the work directory.

## Single binary ("like Go")

Three tiers, honest about trade-offs:

1. `make pyz` → `dist/gothica.pyz` (~240 KB, one file, needs any Python 3.10+ on the host).
2. `make binarium` → `dist/gothica` via PyInstaller: fully self-contained executable (~15–20 MB), **no Python needed on the target**. Build once per target OS (macOS/Linux/Windows) — like Go's per-GOOS builds, minus the cross-compilation.
3. True static native binary = the planned Go/Rust port. The spec's conformance suite exists precisely so that port is mechanical.

## Commands

| | |
|---|---|
| `gothica invoco file.vg` | run a CANTICUM |
| `gothica proba --dir probationes` | run `*_proba.vg` test litanies |
| `gothica scribe-solum fabrica.vg` | emit Terraform JSON only |
| `gothica auguro fabrica.vg` | plan (`--exi-si-mutatio` for drift CI) |
| `gothica consecro fabrica.vg` | apply — speaks only after you type `FIAT` (`--fiat` to skip) |
| `gothica exterminatus fabrica.vg` | destroy — type `EXTERMINATUS`; no bypass flag exists |
| `gothica versio` | version |

Global flags: `--silens` (no liturgy), `--profanum` (machine-readable JSON diagnostics for CI/editors), `-postulatum k=v` (supply POSTULO values; also `GOTHICA_POSTULATUM_<NOMEN>` env vars).

## Layout

```
gothica/            the package: lexicon, parser, interpres, cultus (stdlib),
                    fabrica (tf.json emitter + terraform driver), cli
exempla/            runnable examples from the language docs
demo/               a project with fons/ modules and probationes/ tests
install.sh          macOS/Linux installer
install.ps1         Windows installer
Dockerfile          fabrica execution image (gothica + terraform)
Makefile            proba / pyz / binarium / docker
```

## Implemented (v0.2.0)

Core language: Roman & Arabic numerals, interpolation, DECLARO/SANCTUM/FIAT, SI/DUM/PRO OMNI, RITUS incl. anonymous rites & closures, SCHEMA records, TEMPTA/heresies per the Codex Hereticus, modules (`INVOCO`, `UT`, `EX`), stdlib (mathematica, scriptura, ordo_opera, tempus, archivum, imperium, machina_cogitans, codex_json, fortuna, notarius, probatio). Fabrica: FOEDUS/SEDES/EXSTRUATUR/SCRUTOR/POSTULO/PROFITEOR/ARCANUM, deferred references, alias table, Terraform JSON emission, plan/apply/destroy driver.

Not yet: `expello`/`renovo`/`offero`, `purga`/`lustro`, static checker. Shipped in v0.2.2: `initium`, `adfero` (GitHub deps). See milestone plan (M4–M6).

*The flesh is weak; the toolchain is versioned.*
