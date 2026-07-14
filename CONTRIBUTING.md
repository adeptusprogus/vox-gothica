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

### 2. Create a branch

Branch from latest `main`:

```bash
git fetch upstream
git checkout -b feat/short-description upstream/main
```

**Branch naming:**

| Prefix | Use for |
|--------|---------|
| `feat/` | New language feature or stdlib module |
| `fix/` | Bug fix |
| `docs/` | Codex, wiki, README only |
| `ci/` | Workflows, tooling |
| `refactor/` | Internal restructuring (no behavior change) |

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

### 4. Commit

Write clear commit messages:

```
fix: guard divisor in litania_numerorum example

Prevents divisio_nihili when divisor is N. Adds *_proba.vg case.
```

Prefixes: `feat`, `fix`, `docs`, `ci`, `refactor`, `test`.

### 5. Open a pull request

```bash
git push origin feat/short-description
```

Open a PR against `adeptusprogus/vox-gothica:main`. Fill in the PR template.

**PR title:** same style as commits (e.g. `feat: add lustro linter stub`).

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
