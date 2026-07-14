"""gothica adfero — resolve manifest and sync lockfile (08-litaniae §6, M4)."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ..heresiae import Profanatio
from .claustrum import LockEntry, claustrum_path, load_claustrum, tree_signum, write_claustrum
from .manifestum import Manifest, load_manifest, manifest_path

_GITHUB_VIA = re.compile(r"^github\.com/([^/]+)/([^/]+)(?:/v(\d+))?$")


def _git_url(via: str) -> str:
    m = _GITHUB_VIA.match(via)
    if not m:
        raise Profanatio(
            "P-XIV", "via_innota",
            f"remote resolution for '{via}' is not supported yet "
            f"(github.com/owner/repo only).",
            str(manifest_path(".")), 0,
        )
    owner, repo, _major = m.group(1), m.group(2), m.group(3)
    return f"https://github.com/{owner}/{repo}.git"


def _parse_min_version(constraint: str) -> str:
    c = constraint.strip()
    if c.startswith("^"):
        return c[1:]
    if c.startswith("~"):
        return c[1:]
    if c.startswith(">="):
        return c[2:]
    if c.startswith("="):
        return c[1:]
    return c


def _resolve_version(via: str, constraint: str) -> str:
    url = _git_url(via)
    target = _parse_min_version(constraint)
    ref = target if re.match(r"^v?\d", target) else f"v{target}"
    proc = subprocess.run(
        ["git", "ls-remote", "--tags", url, ref],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        raise Profanatio(
            "P-XIV", "fons_inaccessibilis",
            f"cannot reach '{via}': {proc.stderr.strip() or proc.stdout.strip()}",
            via, 0,
        )
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if not lines:
        raise Profanatio(
            "P-XIV", "versio_innota",
            f"no tag matching '{ref}' for '{via}'",
            via, 0,
        )
    # tags: <hash>\trefs/tags/v1.2.3
    tag = lines[-1].split("\t")[-1].replace("refs/tags/", "")
    return tag.lstrip("v")


def _fetch_litania(root: Path, via: str, versio: str) -> LockEntry:
    dest = root / "litaniae" / via
    if dest.exists():
        import shutil
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = _git_url(via)
    tag = versio if versio.startswith("v") else f"v{versio}"
    proc = subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", tag, url, str(dest)],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0:
        raise Profanatio(
            "P-XIV", "fons_inaccessibilis",
            f"clone of '{via}@{versio}' failed: {proc.stderr.strip()}",
            str(dest), 0,
        )
    fons = dest / "fons"
    if not fons.is_dir():
        raise Profanatio(
            "P-XIV", "litania_incompleta",
            f"'{via}' has no fons/ directory",
            str(dest), 0,
        )
    signum = tree_signum(fons)
    return LockEntry(
        via=via,
        versio=versio.lstrip("v"),
        fons=f"git+{url}@{tag}",
        signum=signum,
    )


def sync(root: str | Path) -> list[LockEntry]:
    root = Path(root).resolve()
    manifest = load_manifest(manifest_path(root))

    entries: list[LockEntry] = []
    all_deps = {**manifest.requirit, **manifest.requirit_probationis}
    for via, constraint in sorted(all_deps.items()):
        versio = _resolve_version(via, constraint)
        entries.append(_fetch_litania(root, via, versio))

    write_claustrum(claustrum_path(root), entries)
    return entries


def append_dependency(root: str | Path, via: str, constraint: str) -> None:
    path = manifest_path(root)
    text = path.read_text(encoding="utf-8")
    line = f'"{via}" = "{constraint}"'
    if via in text:
        return
    if "[requirit]" not in text:
        text = text.rstrip() + f'\n\n[requirit]\n{line}\n'
    else:
        parts = text.split("[requirit]", 1)
        head, tail = parts[0], parts[1]
        section, _, rest = tail.partition("\n\n")
        section = section.rstrip() + f"\n{line}\n"
        text = head + "[requirit]" + section + ("\n\n" + rest if rest else "")
    path.write_text(text, encoding="utf-8")
