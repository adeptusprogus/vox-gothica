# CLI Reference

Binary name: **`gothica`**

Global flags:
- `--silens` — results only, no liturgy
- `--profanum` — plain diagnostics (Arabic line numbers); censura/lustro emit JSON records
- `--profanum=json` — machine-readable JSON for CI/editors (documented; boolean `--profanum` ships today)
- `-postulatum k=v` — supply POSTULO values (also `GOTHICA_POSTULATUM_<NOMEN>` env vars)

## Execution

| Command | Action |
|---------|--------|
| `gothica invoco file.vg` | Run a CANTICUM (preflight `censura` unless `GOTHICA_CENSURA=N`) |
| `gothica invoco file.vg -- args…` | Pass args to `imperium.argumenta()` |
| `gothica invoco --profunditas N` | Override recursion limit |
| `gothica proba [--dir probationes]` | Run `*_proba.vg` test litanies |

## Infrastructure (Fabrica)

| Command | Action |
|---------|--------|
| `gothica scribe-solum fabrica.vg` | Emit `.tf.json` only |
| `gothica auguro fabrica.vg` | `terraform plan` (preflight censura) |
| `gothica auguro --exi-si-mutatio` | Exit non-zero on drift (CI) |
| `gothica consecro fabrica.vg` | Plan + apply (type **FIAT**) |
| `gothica consecro --fiat` | Apply without confirmation |
| `gothica exterminatus fabrica.vg` | Destroy (type **EXTERMINATUS**, no bypass) |

## Packages

| Command | Action |
|---------|--------|
| `gothica initium --via name` | Scaffold project (`principium.vg` + `fons/` + tests) |
| `gothica initium --via name --litania` | Scaffold publishable litania |
| `gothica adfero via[@versio]` | Install litania |
| `gothica expello via` | Remove litania |
| `gothica renovo [via]` | Upgrade dependencies |
| `gothica offero` | Publish to Librarium |
| `gothica librarium quaere term` | Search package index |
| `gothica librarium inspice via` | Inspect a package |

## Hygiene & static analysis (M5)

| Command | Action |
|---------|--------|
| `gothica purga [file\|dir]` | Formatter (`--proba` = check only) |
| `gothica lustro [file\|dir]` | Linter (L-I–L-X; `--serius` disables L-VII) |
| `gothica censura [file\|dir]` | Static checker (C-I–C-V, imports); exit `1` on findings |
| `gothica speculum file.vg` | lustro + censura as JSONL |
| `gothica speculum --stdio` | NDJSON RPC (`analyze`, `shutdown`) |
| `gothica codex [query]` | Search Codex documentation |
| `gothica codex lustro` | Validate doc examples |
| `gothica versio` | Toolchain version |

## Sample applications

See `vox-gothica/applicata/`:

```bash
gothica invoco applicata/cogitator_arithmetica/principium.vg -- additio VII III
gothica invoco applicata/auspex_impietatis/principium.vg -- the WARP hungers
gothica invoco applicata/census_mortis/principium.vg -- census D X V III
```

## Environment

| Variable | Effect |
|----------|--------|
| `GOTHICA_CENSURA=N` | Skip censura preflight on `invoco` / `auguro` / `consecro` |
| `GOTHICA_SILENS=I` | Same as `--silens` |
| `GOTHICA_PROFANUM=I` | Same as `--profanum` |
| `GOTHICA_NOTARIUS` | `notarius` log level |

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Tests failed, censura/lustro findings, plan drift (`--exi-si-mutatio`), or censura preflight halt |
| `2` | Profanatio (parse/load) |
| `3` | Ira Machinae (Terraform failure) |
| `4` | Excommunicatio (package operations) |

Full spec: [Mandata (Ch. XII)](https://adeptusprogus.github.io/vox-gothica/12-cli.html)
