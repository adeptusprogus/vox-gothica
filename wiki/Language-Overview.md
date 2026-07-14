# Language Overview

**Vox Gothica** (v0.2.0) is a High Gothic programming language. File extension: `.vg`.

## Three execution modes

| Mode | Header | Purpose |
|------|--------|---------|
| **Canticle** | `CANTICUM "name".` | General-purpose programs |
| **Fabrica** | `FABRICA "name".` | Infrastructure → Terraform JSON |
| **Litania** | `LITANIA "name".` | Library module (declarations only) |

Every file begins with `AVE OMNISSIAH.` — the file seal.

## Core concepts

| Latin term | Meaning |
|------------|---------|
| **Ritus** | Function |
| **SCHEMA** | Record type |
| **HERESIS** | Error (exception) |
| **Litania** | Package |
| **INVOCO** | Import |
| **DECLARO** / **SANCTUM** | Mutable / immutable binding |
| **FIAT** | Assignment |
| **VOCIFERO** | Print to stdout |
| **TEMPTA** | Try/catch |

## Type system

Primitive types: `NUMERUS`, `FRACTIO`, `SCRIPTUM`, `VERITAS`, `NIHIL`, `ORDO[T]`, `TABULA[K,V]`, plus user-defined `SCHEMA`.

- **Strict typing** — no implicit coercions, no truthiness
- **Roman & Arabic numerals** — `XII` and `12` are interchangeable
- **String interpolation** — `"Ave, {nomen}!"`

## Modules

One `.vg` file = one module. Import with:

```vg
INVOCO "mathematica"                       ++ stdlib
INVOCO "fons/logistics"                    ++ project module
INVOCO "adeptus/http_sancta" UT rete       ++ installed litania + alias
```

## Design principles

1. **Pseudo-Latin, fixed forms** — keywords never conjugate
2. **Code is liturgy** — metaphor covers CLI, errors, packages
3. **Serious core** — fully implementable, debuggable language underneath
4. **One AST, two backends** — interpreter + Terraform emitter
5. **No lock-in** — generated `.tf.json` is ordinary Terraform

Full doctrine: [Prooemium](https://adeptusprogus.github.io/vox-gothica/prooemium.html)
