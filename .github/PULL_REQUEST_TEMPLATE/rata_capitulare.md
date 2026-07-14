name: Rata Capitulare
about: Standard offering to the Rite — feature, fix, or codex amendment
title: "ordo: "
assignees: []
---

## Summarium

<!-- Quae facit haec rata, et cur? One paragraph in plain language. -->

## Ordo Branchium

<!-- Branch **must** be `<ordo>/<slug>` — see [CONTRIBUTING.md](../CONTRIBUTING.md#2-create-a-branch--ordo-branchium) -->

- [ ] `cantica/` — language, interpreter, stdlib
- [ ] `fabrica/` — infrastructure, Terraform, Fabricae
- [ ] `litania/` — packages, lockfile, registry
- [ ] `purgatio/` — bug fix (heresy expunged)
- [ ] `codex/` — documentation, wiki, README
- [ ] `cogitator/` — CI, build, install scripts, tooling
- [ ] `exterminatus/` — removal / deprecation
- [ ] `crusade/` — part of a larger effort (issue: #<!-- N -->)

**Branch:** `<!-- ordo/kebab-case-slug -->`

**Commits:** ordine prefix on every commit (`cantica:`, `purgatio:`, …)

## Codex alignment

The spec is law. If behavior changes, the Codex must agree.

- [ ] No language-spec changes
- [ ] Codex chapter updated: <!-- e.g. docs/06-heresies.html -->
- [ ] N/A — tooling / CI only

## Probationes (testing)

- [ ] `make proba` passes locally
- [ ] New/updated `*_proba.vg` in `demo/probationes/`
- [ ] New/updated exemplum in `exempla/`
- [ ] N/A — docs only

## Checklist

- [ ] Branch name follows **Ordo Branchium** (`<ordo>/<slug>`)
- [ ] PR title uses the same ordine as the branch
- [ ] Single concern per PR (no unrelated changes)
- [ ] No secrets, tokens, or credentials committed
- [ ] Linked issue (if any): #<!-- N -->

---

*The flesh offers the diff; the Collegium judges.*
