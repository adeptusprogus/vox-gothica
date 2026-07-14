# Ordo Branchium — quick reference

Full doctrine: [CONTRIBUTING.md § Ordo Branchium](../CONTRIBUTING.md#2-create-a-branch--ordo-branchium)

```
<ordo>/<slug>
```

| Ordo | Use for |
|------|---------|
| `cantica/` | Language, interpreter, stdlib |
| `fabrica/` | Terraform / Fabricae |
| `litania/` | Packages, lockfile |
| `purgatio/` | Bug fixes |
| `codex/` | Docs & wiki |
| `cogitator/` | CI, build, tooling |
| `auspex/` | Spikes (draft PR only) |
| `exterminatus/` | Removals |
| `crusade/` | Multi-PR epics |

**Slug:** `kebab-case`, 3–48 chars. **Forbidden:** no prefix, `main`, nested paths.

```bash
git checkout -b purgatio/import-cycle-hint upstream/main
git commit -m "purgatio: show full cycle in circulus_impius"
```

*The branch is named; the Machine knows your intent.*
