# Vox Gothica

**A High Gothic programming language for canticles and fabricae** — an esolang in the
tradition of the Adeptus Mechanicus, with a real Python toolchain (`gothica`) and
Terraform-backed *fabricae*.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Docs](https://img.shields.io/badge/docs-Codex%20Vox%20Gothica-8B0000)](https://adeptusprogus.github.io/vox-gothica/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)](https://github.com/adeptusprogus/vox-gothica)

> *From the weakness of the flesh — the Machine delivers us.*

---

## Table of contents

- [What is this?](#what-is-this)
- [Requirements](#requirements)
- [Install](#install)
  - [macOS](#macos)
  - [Linux](#linux)
  - [Windows](#windows)
  - [Docker (all platforms)](#docker-all-platforms)
  - [Portable / standalone binary](#portable--standalone-binary)
  - [Run without installing](#run-without-installing)
- [Quick start](#quick-start)
- [CLI reference](#cli-reference)
- [Documentation](#documentation)
- [Development](#development)
- [Repository layout](#repository-layout)
- [Status](#status)
- [Contributing](#contributing)
- [License](#license)

---

## What is this?

**Vox Gothica** (`.vg`) is a programming language whose source reads as pseudo-Latin
liturgy of the Adeptus Mechanicus. One syntax, two purposes:

| Rite | Header | What it does |
|------|--------|--------------|
| **Canticle** | `CANTICUM "name".` | General-purpose programs — functions (*rites*), records (*schemas*), errors (*heresies*), modules |
| **Fabrica** | `FABRICA "name".` | Infrastructure manifests → **Terraform JSON** — chanting genuinely raises cloud machines |

```vg
AVE OMNISSIAH.
CANTICUM "salutatio".

VOCIFERO "Ave, Imperium!"
```

```console
$ gothica invoco salutatio.vg
Ave, Imperium!
++ The rite concludes. The Machine Spirit is appeased. ++
```

The reference toolchain **`gothica`** is pure Python ≥ 3.10 with **zero runtime dependencies**.

---

## Requirements

| | macOS | Linux | Windows |
|---|-------|-------|---------|
| **Python** | 3.10+ ([python.org](https://www.python.org/downloads/) or `brew install python`) | 3.10+ (`apt install python3` / `dnf install python3`) | 3.10+ ([python.org](https://www.python.org/downloads/) or `winget install Python.Python.3.12`) |
| **pip** | included with Python | `python3 -m ensurepip` | included with Python |
| **Terraform** | only for *fabricae* | only for *fabricae* | only for *fabricae* (`winget install Hashicorp.Terraform`) |
| **Disk** | ~5 MB (toolchain) | ~5 MB | ~5 MB |

Optional but recommended: **[pipx](https://pipx.pypa.io/)** — installs `gothica` into an isolated environment on any OS.

---

## Install

Clone once, then follow your platform:

```console
git clone https://github.com/adeptusprogus/vox-gothica.git
cd vox-gothica/vox-gothica
```

All install methods place a `gothica` command on your `PATH`.

---

### macOS

**1. Install Python** (if needed):

```console
brew install python pipx
pipx ensurepath
```

Restart the terminal after `pipx ensurepath`.

**2. Install gothica:**

```console
./install.sh
```

**3. Verify:**

```console
gothica versio
gothica invoco exempla/salutatio.vg
```

<details>
<summary>Alternative: single-file zipapp (no pip)</summary>

```console
./install.sh --pyz
export PATH="$PATH:$HOME/.local/bin"   # add to ~/.zshrc to persist
gothica versio
```

</details>

<details>
<summary>Alternative: manual venv</summary>

```console
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
gothica versio
```

</details>

---

### Linux

**1. Install Python** (Debian/Ubuntu example):

```console
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
pipx install pipx && pipx ensurepath   # optional but recommended
```

Fedora/RHEL: `sudo dnf install python3 python3-pip`  
Arch: `sudo pacman -S python python-pip`

**2. Install gothica:**

```console
chmod +x install.sh
./install.sh
```

**3. Ensure `~/.local/bin` is on PATH** (if the installer says so):

```console
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
gothica versio
```

<details>
<summary>Alternative: single-file zipapp</summary>

```console
./install.sh --pyz
export PATH="$PATH:$HOME/.local/bin"
gothica versio
```

</details>

<details>
<summary>Alternative: manual venv</summary>

```console
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
gothica versio
```

</details>

---

### Windows

**1. Install Python** (if needed):

```powershell
winget install Python.Python.3.12
```

During setup, check **“Add python.exe to PATH”**. Open a **new** PowerShell window afterwards.

**2. Install gothica:**

```powershell
cd vox-gothica\vox-gothica
powershell -ExecutionPolicy Bypass -File install.ps1
```

**3. Verify** (new terminal if `gothica` is not found):

```powershell
gothica versio
gothica invoco exempla\salutatio.vg
```

<details>
<summary>If gothica is not recognized</summary>

The installer prints a `Scripts` folder path. Add it to your user PATH:

```powershell
# Example — use the path printed by install.ps1
[Environment]::SetEnvironmentVariable(
  'PATH',
  $env:PATH + ';C:\Users\YOU\AppData\Roaming\Python\Python312\Scripts',
  'User'
)
```

Open a **new** terminal, then run `gothica versio`.

</details>

<details>
<summary>Alternative: manual venv</summary>

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
gothica versio
```

</details>

<details>
<summary>Git Bash / WSL</summary>

On **WSL** or **Git Bash**, use the [Linux](#linux) / [macOS](#macos) `install.sh` path instead.

</details>

---

### Docker (all platforms)

For *fabricae*, the Docker image bundles **gothica + Terraform** — useful when you
do not want to install Terraform locally.

```console
cd vox-gothica
docker build -t vox-gothica .
```

**Plan** (macOS / Linux):

```console
docker run --rm -v "$PWD:/opus" vox-gothica auguro /opus/exempla/fabrica_interretialis.vg
```

**Plan** (Windows PowerShell):

```powershell
docker run --rm -v "${PWD}:/opus" vox-gothica auguro /opus/exempla/fabrica_interretialis.vg
```

**Apply** (with cloud credentials):

```console
docker run --rm -it -v "$PWD:/opus" \
  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
  vox-gothica consecro /opus/exempla/fabrica_interretialis.vg --fiat
```

---

### Portable / standalone binary

Build on the **target OS** (no cross-compilation):

| Tier | Command | Result |
|------|---------|--------|
| Zipapp | `make pyz` | `dist/gothica.pyz` (~240 KB, needs Python 3.10+ on host) |
| Native-ish | `make binarium` | `dist/gothica` (~15–20 MB, **no Python** on target) |

Works on macOS, Linux, and Windows — run `make` from `vox-gothica/` on each platform you ship to.

---

### Run without installing

For a quick trial or development, no install step:

**macOS / Linux:**

```console
cd vox-gothica
PYTHONPATH=. python3 -m gothica invoco exempla/salutatio.vg
```

**Windows:**

```powershell
cd vox-gothica
$env:PYTHONPATH = "."
python -m gothica invoco exempla\salutatio.vg
```

---

## Quick start

After install, from the `vox-gothica/` directory:

```console
# Hello world
gothica invoco exempla/salutatio.vg

# Roman numerals & lists
gothica invoco exempla/litania_numerorum.vg

# Run the test suite
gothica proba --dir demo/probationes

# Emit Terraform JSON (no cloud credentials needed)
gothica scribe-solum exempla/fabrica_interretialis.vg
```

Create your own canticle — save as `meum.vg` anywhere:

```vg
AVE OMNISSIAH.
CANTICUM "meum".

VOCIFERO "Ave, Omnissiah!"
```

```console
gothica invoco meum.vg
```

---

## CLI reference

| Command | Action |
|---------|--------|
| `gothica invoco file.vg` | Run a CANTICUM |
| `gothica proba --dir probationes` | Run `*_proba.vg` test litanies |
| `gothica scribe-solum fabrica.vg` | Emit `.tf.json` only |
| `gothica auguro fabrica.vg` | `terraform plan` |
| `gothica consecro fabrica.vg` | `terraform apply` — type **FIAT** (`--fiat` to skip) |
| `gothica exterminatus fabrica.vg` | `terraform destroy` — type **EXTERMINATUS** (no bypass) |
| `gothica versio` | Toolchain version |

**Global flags:** `--silens` (no liturgy) · `--profanum` / `--profanum=json` (CI diagnostics) · `-postulatum k=v` (Fabrica variables; also `GOTHICA_POSTULATUM_<NAME>` env vars)

Full spec: [Mandata (Ch. XII)](https://adeptusprogus.github.io/vox-gothica/12-cli.html)

---

## Documentation

The normative language specification is the **[Codex Vox Gothica](https://adeptusprogus.github.io/vox-gothica/)**:

| Chapter | Topic |
|---------|-------|
| [Porta Librarii](https://adeptusprogus.github.io/vox-gothica/) | Index |
| [Prooemium](https://adeptusprogus.github.io/vox-gothica/prooemium.html) | Design principles |
| [Codex Hereticus](https://adeptusprogus.github.io/vox-gothica/06-heresies.html) | Error taxonomy |
| [Fabrica](https://adeptusprogus.github.io/vox-gothica/10-fabrica.html) | Infrastructure → Terraform |
| [Mandata](https://adeptusprogus.github.io/vox-gothica/12-cli.html) | CLI & diagnostics |
| [Glossarium](https://adeptusprogus.github.io/vox-gothica/15-glossary.html) | Keywords |

Source HTML: [`docs/`](docs/) · Wiki quick-ref: [`wiki/`](wiki/)

---

## Development

```console
cd vox-gothica
python3 -m venv .venv
```

**macOS / Linux:** `source .venv/bin/activate`  
**Windows:** `.\.venv\Scripts\Activate.ps1`

```console
pip install -e .
make proba          # run full test suite
make pyz            # build dist/gothica.pyz
make docker         # build Docker image
```

Toolchain internals: [`vox-gothica/README.md`](vox-gothica/README.md) · architecture: [Instrumenta (Ch. XIV)](https://adeptusprogus.github.io/vox-gothica/14-implementation.html)

---

## Repository layout

```
vox-gothica/
├── README.md              ← you are here
├── CONTRIBUTING.md        ← PR workflow & Ordo Branchium
├── docs/                  ← Codex Vox Gothica (GitHub Pages)
├── wiki/                  ← GitHub Wiki markdown sources
└── vox-gothica/           ← gothica toolchain
    ├── gothica/           ← Python package (lexer, parser, interpreter, fabrica)
    ├── exempla/           ← runnable examples
    ├── demo/              ← sample project + probationes/
    ├── install.sh         ← macOS & Linux installer
    ├── install.ps1        ← Windows installer
    ├── Dockerfile         ← gothica + Terraform image
    └── Makefile           ← proba / pyz / binarium / docker
```

---

## Status

**v0.2.0 — Second Canticle**

| ✅ Shipped | 🚧 Planned (M4–M6) |
|-----------|-------------------|
| Lexer, parser, interpreter | Litania package manager (`adfero` / `offero`) |
| Modules, stdlib, test runner | `purga` formatter, `lustro` linter |
| Fabrica → Terraform JSON | Static checker, conformance suite |
| Plan / apply / destroy driver | Go/Rust port |

---

## Collegium Magorum

| | |
|---|---|
| **EduardL** | Archmagos Auctor — Founder of the Rite |
| **Claude Fable** | Magos Errant — Cogitator-Artisan of the First Canticle |

---

## Contributing

Pull requests welcome. Read **[CONTRIBUTING.md](CONTRIBUTING.md)** for:

- **Ordo Branchium** — branch naming (`cantica/`, `purgatio/`, `codex/`, …)
- PR + green CI required on `main`
- Automated inquisitor — wrong branch names get *HERESY DETECTA*

Quick ref: [.github/BRANCH_POLICY.md](.github/BRANCH_POLICY.md)

---

## License

[GNU General Public License v3.0](LICENSE)

*The flesh is weak; the toolchain is versioned.*
