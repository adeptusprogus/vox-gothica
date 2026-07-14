# Project Layout

## Repository structure

```
vox-gothica/
├── README.md              # This landing page
├── LICENSE                # GPL-3.0
├── docs/                  # Codex Vox Gothica (GitHub Pages)
│   ├── index.html
│   ├── 01-lexical.html … 15-glossary.html
│   ├── fontes/            # Self-hosted Gothic fonts
│   └── stylus.css
├── vox-gothica/           # Reference toolchain
│   ├── gothica/           # Python package
│   ├── exempla/           # Runnable doc examples
│   ├── demo/              # Sample project with tests
│   ├── install.sh         # macOS/Linux installer
│   ├── Dockerfile         # gothica + terraform image
│   └── pyproject.toml
└── .github/workflows/     # CI
```

## Vox Gothica project layout

A typical user project:

```
meum_opus/
  litania.toml          # manifest
  litania.claustrum     # lockfile
  principium.vg         # CANTICUM entry
  fabrica.vg            # FABRICA manifest
  fons/                 # project LITANIA modules
    logistics.vg
    cogitator/
      auspex.vg
  litaniae/             # installed packages
  probationes/          # tests: *_proba.vg
```

## File headers

Every `.vg` file must begin with:

```vg
AVE OMNISSIAH.
CANTICUM "name".     # or FABRICA / LITANIA
```

## Naming conventions

- Module files: `snake_case.vg`
- Private bindings: prefix `_`
- Test files: `*_proba.vg`
- Package names: hyphens allowed; module file names: underscores only

See [Moduli (Ch. VII)](https://adeptusprogus.github.io/vox-gothica/07-modules.html) and [Litaniae (Ch. VIII)](https://adeptusprogus.github.io/vox-gothica/08-litaniae.html).
