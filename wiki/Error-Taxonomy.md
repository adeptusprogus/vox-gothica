# Error Taxonomy

Vox Gothica has **no undefined behavior**. Anything not defined in the spec is **`PROFANATIO`** (compile-time rejection).

## Three orders of sin

| Order | Latin | When | Caught by TEMPTA? |
|-------|-------|------|-------------------|
| **Profanatio** | compile-time | Parse / resolution / mode violations | N/A (won't compile) |
| **Minor heresy** | `HERESIS MINORIS` | Runtime logic errors | Yes |
| **Major heresy** | `HERESIS MAIORIS` | Stack overflow, recursion limit | No (unwinds stack) |

## Diagnostic format

```
⚙ HERESIS DETECTA — CANTICUM "name", VERSUS XLII
  genus: divisio_nihili
  The cogitator was commanded to divide C by naught.

    XLII │     DECLARO quotiens : NUMERUS = summa / divisor
         │                                        ^^^^^^^^^
  vestigium:
    ritus divide_sancte — VERSUS XLII
  ++ hint: guard the divisor — SI divisor == N TUNC ...
```

Use `--profanum` for plain text or `--profanum=json` for CI.

## Common genera

| Genus | Meaning |
|-------|---------|
| `divisio_nihili` | Division by zero |
| `vas_ignotum` | Use before declaration |
| `typus_profamus` | Type mismatch |
| `conversio_impossibilis` | Invalid type conversion |
| `invocatio_vana` | Module not found |
| `circulus_impius` | Import cycle |
| `fabrica_in_cantico` | EXSTRUATUR in a CANTICUM |
| `relatio_differata_tacta` | Illegal operation on deferred reference |

The complete taxonomy (normative): [Codex Hereticus (Ch. VI)](https://adeptusprogus.github.io/vox-gothica/06-heresies.html)
