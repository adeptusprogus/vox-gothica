# Applicata Sancta

Runnable canticles — grotesque utilities in the sight of the Omnissiah.

| App | Rite | Invocation |
|-----|------|------------|
| **Cogitator Arithmetica** | Sacred ledger / calculator | `gothica invoco applicata/cogitator_arithmetica/principium.vg -- additio VII III` |
| **Auspex Impietatis** | Purity scanner (text or census) | `gothica invoco applicata/auspex_impietatis/principium.vg -- OMNISSIAH` |
| **Census Mortis** | Post-battle casualty ledger | `gothica invoco applicata/census_mortis/principium.vg -- census D X V III` |

Each app is a small project: `principium.vg` (CANTICUM entry), `fons/` (LITANIA logic), `probationes/` (tests).

### Census Mortis operands

`census <effectifs> <%mortis> <%mutilati> <%deserteres>` — percents are plain `NUMERUS` (e.g. `XX` = 20%). Example: 500 troops, 10% dead, 5% maimed, 3% deserters:

```bash
gothica invoco applicata/census_mortis/principium.vg -- census D X V III
```
