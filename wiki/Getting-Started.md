# Getting Started

## Requirements

- Python **3.10+**
- Zero runtime dependencies (pure Python stdlib)

## Install

```bash
git clone https://github.com/adeptusprogus/vox-gothica.git
cd vox-gothica/vox-gothica
./install.sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

**Single-file binary (zipapp):**
```bash
./install.sh --pyz    # → ~/.local/bin/gothica
```

Verify:
```bash
gothica versio
```

## Your first canticle

Create `salutatio.vg`:

```vg
AVE OMNISSIAH.
CANTICUM "salutatio".

VOCIFERO "Ave, Imperium!"
```

Run it:
```bash
gothica invoco salutatio.vg
```

Expected output:
```
Ave, Imperium!
++ The rite concludes. The Machine Spirit is appeased. ++
```

## Run the examples

```bash
cd vox-gothica
gothica invoco exempla/salutatio.vg
gothica invoco exempla/litania_numerorum.vg
gothica proba --dir demo/probationes
make proba    # full CI suite
```

## Sample applications (Applicata Sancta)

Grotesque WH40K utilities in `applicata/`:

```bash
# Sacred calculator
gothica invoco applicata/cogitator_arithmetica/principium.vg -- additio VII III

# Heresy scanner
gothica invoco applicata/auspex_impietatis/principium.vg -- DCLXVI

# Post-battle casualty ledger (500 troops, 10% dead, 5% maimed, 3% deserters)
gothica invoco applicata/census_mortis/principium.vg -- census D X V III
```

Static check before run (automatic on `invoco`):
```bash
gothica censura applicata/cogitator_arithmetica
```

## Docker (for Fabricae)

```bash
docker build -t vox-gothica .
docker run --rm -v "$PWD:/opus" vox-gothica auguro /opus/exempla/fabrica_interretialis.vg
```

## Next steps

- Read the [Language Overview](Language-Overview)
- Browse [Exempla Sancta](https://adeptusprogus.github.io/vox-gothica/13-examples.html) in the Codex (§7 = applicata)
- See [CLI Reference](CLI-Reference) for `censura`, `speculum`, and all commands
