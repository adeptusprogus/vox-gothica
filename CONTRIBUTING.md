# Contributing to Vox Gothica

Thank you for offering your flesh-hours to the Rite. This document describes how to propose changes.

## Golden rules

1. **`main` is sacred** — no direct pushes. Every change enters through a pull request.
2. **CI must be green** — all three Python versions (3.10, 3.11, 3.12) must pass `make proba`.
3. **One concern per PR** — a bugfix, a feature, or a doc fix; not all three.
4. **Spec is law** — language changes must match the [Codex](https://adeptusprogus.github.io/vox-gothica/). If the Codex and code disagree, fix whichever is wrong and note it in the PR.
5. **No drive-by refactors** — touch only what your change requires.

## Workflow

```
fork → branch → commit → push → pull request → review → merge
```

### 1. Fork and clone

```bash
git clone https://github.com/<you>/vox-gothica.git
cd vox-gothica
git remote add upstream https://github.com/adeptusprogus/vox-gothica.git
```

### 2. Create a branch — *Ordo Branchium*

Every branch bears an **ordo** (order) prefix from the Cult Mechanicus. This is not optional decoration: it tells reviewers what liturgy you are performing.

**Format (normative):**

```
<ordo>/<slug>
```

| Part | Rule |
|------|------|
| `<ordo>` | One of the sacred orders below — lowercase, exactly as written |
| `<slug>` | `kebab-case`, lowercase English or Latin, **3–48 characters**, describes the change |
| Separator | Single `/` between ordo and slug — no nested paths |

**Examples:**

```bash
git checkout -b cantica/lustro-linter upstream/main
git checkout -b purgatio/divisor-nihil-guard upstream/main
git checkout -b codex/chapter-viii-litaniae upstream/main
git checkout -b fabrica/aws-vpc-alias upstream/main
```

#### Sacred ordines

| Ordo | High Gothic | Use for |
|------|-------------|---------|
| `cantica/` | *canticle* | Language features, interpreter, parser, stdlib modules, runtime |
| `fabrica/` | *workshop* | Fabricae, Terraform emission, providers, `EXSTRUATUR`, IaC |
| `litania/` | *litany* | Package manager, `litania.toml`, lockfile, registry, deps |
| `purgatio/` | *purification* | Bug fixes — expunging heresy from the Machine |
| `codex/` | *sacred text* | Documentation: `docs/`, `wiki/`, README, Codex chapters |
| `cogitator/` | *cogitator* | CI, build, install scripts, formatter/linter tooling, refactors |
| `auspex/` | *auspex* | Spikes and prototypes — **not for merge without follow-up PR** |
| `exterminatus/` | *extermination* | Removals, deprecations, dead-code annihilation |
| `crusade/` | *crusade* | Large efforts spanning multiple PRs (link the issue in PR body) |

#### Choosing the right ordo

```
New RITUS syntax?          → cantica/
Terraform alias table?     → fabrica/
adfero/offero commands?    → litania/
divisio_nihili on zero?    → purgatio/
Fix typo in 06-heresies?   → codex/
GitHub Actions matrix?     → cogitator/
Try a Go parser for fun?   → auspex/   (mark PR as draft)
Remove deprecated kw?      → exterminatus/
M4 conformance suite?      → crusade/   (reference issue #N)
```

#### Forbidden names

| Sin | Examples |
|-----|----------|
| No ordo prefix | `my-fix`, `update`, `johns-branch` |
| Wrong case | `Cantica/Foo`, `PURGATIO/bar` |
| Nested paths | `cantica/fabrica/vpc` |
| Sacred branch names | `main`, `master`, `develop`, `release` |
| Joke slugs that obscure intent | `cantica/chaos-wins`, `purgatio/empire-sucks` |
| Personal names as slug | `cantica/eduard-wip` — use topic instead: `cantica/lustro-wip` |

> **Auspex branches** must be opened as **Draft PRs** and either promoted to a proper ordo or closed within 14 days. The Machine tolerates reconnaissance, not permanent camps.

Branch from latest `main`:

```bash
git fetch upstream
git checkout -b <ordo>/<slug> upstream/main
```

### 3. Develop and test

```bash
cd vox-gothica
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
make proba
```

If you change language behavior, add or update:
- an example in `vox-gothica/exempla/`
- a test in `vox-gothica/demo/probationes/` (`*_proba.vg`)
- the relevant Codex chapter in `docs/` (if spec-visible)

### 4. Commit — *Inscriptiones*

Commit messages use the **same ordines** as branch names (Conventional Commits, Mechanicus dialect):

```
purgatio: guard divisor in litania_numerorum example

Prevents divisio_nihili when divisor is N. Adds *_proba.vg case.
```

| Prefix | Ordo | When |
|--------|------|------|
| `cantica:` | `cantica/` | New behavior in language or stdlib |
| `fabrica:` | `fabrica/` | Infrastructure / Terraform |
| `litania:` | `litania/` | Packages and lockfile |
| `purgatio:` | `purgatio/` | Bug fix |
| `codex:` | `codex/` | Documentation only |
| `cogitator:` | `cogitator/` | CI, build, tooling, refactor |
| `exterminatus:` | `exterminatus/` | Removal / deprecation |
| `crusade:` | `crusade/` | Part of a tracked multi-PR effort |

Legacy prefixes (`feat:`, `fix:`, `docs:`) are still understood by maintainers but **discouraged** — inscribe the proper ordo.

### 5. Open a pull request

```bash
git push origin <ordo>/<slug>
```

Open a PR against `adeptusprogus/vox-gothica:main`. Fill in the PR template.

**PR title:** same ordine as the branch (e.g. `cantica: add lustro linter stub`).

**Branch name in PR** must match `<ordo>/<slug>`. Maintainers will request rename if the ordo is wrong.

### 6. Review and merge

| Who | What happens |
|-----|--------------|
| **External contributor** | Wait for maintainer review. Address feedback. |
| **Maintainer** | CI green → squash-merge. Delete the branch. |

Maintainers may bypass review in emergencies (branch protection allows admin bypass), but the PR + CI requirement still applies.

## What we merge

| ✅ Welcome | ❌ Please don't |
|-----------|----------------|
| Bug fixes with tests | Breaking changes without Codex update |
| Codex clarifications | Reformatting unrelated files |
| New stdlib modules (discuss in issue first) | New dependencies in the toolchain |
| Fabrica alias additions | Force-push to `main` |
| CI improvements | Commits with secrets or credentials |

## Large changes

Open an **issue** first for:

- New language keywords or syntax
- Changes to the Codex Hereticus taxonomy
- Package manager (`litaniae`) implementation
- Go/Rust port milestones

## Code style

- Python: match existing code in `gothica/` — no extra abstractions, minimal diff.
- Vox Gothica: follow the Codex lexical rules (Roman numerals, `NUMQUAM FINIS` blocks, file seals).
- Docs: normative chapters are law; mark informative sections as *(informative)*.

## License

By contributing, you agree that your contributions are licensed under the project's [GPL-3.0](LICENSE) license.

*The flesh is weak; the pull request is reviewed.*
