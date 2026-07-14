# Applicata Sancta

Runnable canticles — grotesque utilities in the sight of the Omnissiah.

**Run from the `vox-gothica/` package directory** (where `gothica/`, `exempla/`, and `applicata/` live):

```bash
cd path/to/vox-gothica/vox-gothica
```

| App | Invocation |
|-----|------------|
| **Cogitator Arithmetica** | `gothica invoco applicata/cogitator_arithmetica/principium.vg additio VII III` |
| **Auspex Impietatis** | `gothica invoco applicata/auspex_impietatis/principium.vg OMNISSIAH` |
| **Census Mortis** | `gothica invoco applicata/census_mortis/principium.vg census D X V III` |

### GUI window (fenestra)

Pure Vox Gothica — module `fenestra`, no external Python UI:

```bash
gothica invoco applicata/cogitator_arithmetica/principium_fenestra.vg
```

Seal as standalone executable (requires PyInstaller):

```bash
pip install pyinstaller
gothica sigillum applicata/cogitator_arithmetica/principium_fenestra.vg --fenestra --nomine CogitatorArithmetica
# → dist/CogitatorArithmetica
```

Or: `make sigillum-cogitator` from `vox-gothica/`.

Uses `crea_cogitator` — brass panel, phosphor readout, Adeptus Administratum banner.

## Troubleshooting

### `invocatio_vana` — the invocation of `fenestra` went unanswered

Your `gothica` binary predates the `fenestra` module (e.g. PyInstaller release **v0.2.14** from GitHub). Reinstall from source:

```bash
cd vox-gothica/vox-gothica
python3 -m pip install -e .          # or: ./install.sh --from-source
```

Check which binary runs:

```bash
which gothica
file "$(which gothica)"
```

A **Mach-O executable** in `~/.local/bin/gothica` is the old release bundle. Prefer `.venv/bin/gothica` or a fresh pip install:

```bash
export PATH="$(pwd)/.venv/bin:$PATH"
```

### `fenestra_indisponibilis` — No module named `_tkinter`

Homebrew Python 3.14 ships without Tk. Install the Tk binding, then recreate or reuse a venv:

```bash
brew install python-tk@3.14
python3 -c "import tkinter; print('ok')"
```

### `pip: command not found`

Use `python3 -m pip` or `pip3` instead of `pip`.

### Wrong working directory / missing scroll

Run from **`vox-gothica/vox-gothica/`** (where `applicata/` lives), not the repository root:

```bash
cd path/to/vox-gothica/vox-gothica
gothica invoco applicata/cogitator_arithmetica/principium_fenestra.vg
```

### Window opens behind other apps

On macOS the fenestra may launch off-screen or behind the terminal — use Mission Control (F3) or Cmd+Tab to find **Cogitator Arithmetica**.

### Skip censura preflight (debug only)

```bash
GOTHICA_CENSURA=N gothica invoco applicata/cogitator_arithmetica/principium_fenestra.vg
```

From the **repository root** (`vox-gotica/`, one level up), prefix with `vox-gothica/`:

```bash
gothica invoco vox-gothica/applicata/cogitator_arithmetica/principium.vg additio VII III
```

Each app is a small project: `principium.vg` (CANTICUM entry), `fons/` (LITANIA logic), `probationes/` (tests).

### Census Mortis operands

`census <effectifs> <%mortis> <%mutilati> <%deserteres>` — percents are plain `NUMERUS` (e.g. `XX` = 20%). Example: 500 troops, 10% dead, 5% maimed, 3% deserters:

```bash
gothica invoco applicata/census_mortis/principium.vg -- census D X V III
```
