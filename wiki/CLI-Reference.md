# CLI Reference

Binary name: **`gothica`**

Global flags:
- `--silens` — results only, no liturgy
- `--profanum` — plain diagnostics (Arabic line numbers)
- `--profanum=json` — machine-readable JSON for CI/editors
- `-postulatum k=v` — supply POSTULO values (also `GOTHICA_POSTULATUM_<NOMEN>` env vars)

## Execution

| Command | Action |
|---------|--------|
| `gothica invoco file.vg` | Run a CANTICUM |
| `gothica invoco file.vg -- args…` | Pass args to `imperium.argumenta()` |
| `gothica invoco --profunditas N` | Override recursion limit |
| `gothica proba [--dir probationes]` | Run `*_proba.vg` test litanies |

## Infrastructure (Fabrica)

| Command | Action |
|---------|--------|
| `gothica scribe-solum fabrica.vg` | Emit `.tf.json` only |
| `gothica auguro fabrica.vg` | `terraform plan` |
| `gothica auguro --exi-si-mutatio` | Exit non-zero on drift (CI) |
| `gothica consecro fabrica.vg` | Plan + apply (type **FIAT**) |
| `gothica consecro --fiat` | Apply without confirmation |
| `gothica exterminatus fabrica.vg` | Destroy (type **EXTERMINATUS**, no bypass) |

## Packages (planned M5)

| Command | Action |
|---------|--------|
| `gothica initium` | Scaffold project |
| `gothica adfero via[@versio]` | Install litania |
| `gothica expello via` | Remove litania |
| `gothica renovo [via]` | Upgrade dependencies |
| `gothica offero` | Publish to Librarium |

## Hygiene (planned)

| Command | Action |
|---------|--------|
| `gothica purga [file\|dir]` | Formatter |
| `gothica lustro [file\|dir]` | Linter |
| `gothica codex [query]` | Search documentation |
| `gothica versio` | Toolchain version |

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `I` | Uncaught Minor heresy |
| `II` | Uncaught Major heresy |
| `III` | Terraform failure |
| `IV` | Test failure |
| `V` | Profanatio (compile-time rejection) |

Full spec: [Mandata (Ch. XII)](https://adeptusprogus.github.io/vox-gothica/12-cli.html)
