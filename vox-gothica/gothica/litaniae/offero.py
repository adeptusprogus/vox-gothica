"""gothica offero — publish a litania (08-litaniae §8)."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from .. import __version__
from ..heresiae import Profanatio
from ..parser import parse_source
from .manifestum import Manifest, load_manifest, manifest_path

_LIBRARIUM_DEFAULT = "https://github.com/vox-gothica/librarium-sanctum"
_ORIGIN_RE = re.compile(
    r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$"
)


def _bad(msg: str, path: str) -> None:
    raise Profanatio("P-XIV", "manifestum_pravum", msg, path, 0)


def _run(cmd: list[str], root: Path, *, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=root, capture_output=True, text=True,
        timeout=120, check=check,
    )


def _git_root(root: Path) -> Path:
    proc = _run(["git", "rev-parse", "--show-toplevel"], root, check=False)
    if proc.returncode != 0:
        _bad("offero requires a git repository", str(root))
    return Path(proc.stdout.strip())


def _origin_via(root: Path) -> str:
    proc = _run(["git", "remote", "get-url", "origin"], root, check=False)
    if proc.returncode != 0:
        _bad("git remote 'origin' is required for offero", str(root))
    url = proc.stdout.strip()
    m = _ORIGIN_RE.search(url.replace("git@", ""))
    if not m:
        _bad(f"cannot parse GitHub origin from '{url}'", str(root))
    return f"github.com/{m.group('owner')}/{m.group('repo')}"


def _dirty(root: Path) -> bool:
    proc = _run(["git", "status", "--porcelain"], root, check=False)
    return bool(proc.stdout.strip())


def _head_tag(root: Path) -> str | None:
    proc = _run(
        ["git", "describe", "--tags", "--exact-match", "HEAD"],
        root, check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip().lstrip("v")


def _has_substitutio(mpath: Path) -> bool:
    return "[substitutio]" in mpath.read_text(encoding="utf-8")


def _prerelease_constraint(constraint: str) -> bool:
    ver = constraint.lstrip("^~>= ")
    return "-" in ver


def _path_constraint(constraint: str) -> bool:
    c = constraint.strip()
    return c.startswith((".", "/")) or c.startswith("file:")


def _validate_deps(manifest: Manifest, path: str) -> None:
    for dep, c in {**manifest.requirit, **manifest.requirit_probationis}.items():
        if _path_constraint(c):
            _bad(f"path dependency forbidden in published litaniae: {dep}", path)
        if _prerelease_constraint(c):
            _bad(f"pre-release dependency forbidden: {dep} ({c})", path)


def _validate_fons(root: Path) -> None:
    fons = root / "fons"
    if not fons.is_dir():
        _bad("publishable litaniae require fons/", str(manifest_path(root)))
    vg_files = list(fons.rglob("*.vg"))
    if not vg_files:
        _bad("fons/ contains no .vg scrolls", str(manifest_path(root)))
    for fp in vg_files:
        prog = parse_source(fp.read_text(encoding="utf-8"), str(fp))
        if prog.mode != "LITANIA":
            _bad(
                f"published litaniae may only ship LITANIA scrolls "
                f"({fp.name} is {prog.mode})",
                str(fp),
            )


def _run_proba(root: Path) -> None:
    prob_dir = root / "probationes"
    if not prob_dir.is_dir():
        _bad("probationes/ is required for offero", str(manifest_path(root)))
    proc = subprocess.run(
        [sys.executable, "-m", "gothica", "proba", "--dir", str(prob_dir), "--silens"],
        cwd=root, capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        _bad(
            "probationes failed — offero refused\n"
            + (proc.stdout or "") + (proc.stderr or ""),
            str(prob_dir),
        )


def _ensure_tag(root: Path, versio: str) -> str:
    tag = f"v{versio}"
    head = _head_tag(root)
    if head == versio:
        return tag
    proc = _run(["git", "tag", "-l", tag], root, check=False)
    if tag in proc.stdout.split():
        _bad(
            f"tag '{tag}' exists but HEAD is not tagged — "
            f"checkout the release commit or move the tag",
            str(root),
        )
    _run(["git", "tag", tag], root)
    return tag


def _push_tag(root: Path, tag: str) -> None:
    proc = _run(["git", "push", "origin", tag], root, check=False)
    if proc.returncode != 0:
        _bad(
            f"git push origin {tag} failed: {proc.stderr.strip()}",
            str(root),
        )


def librarium_pr_hint(via: str, versio: str) -> str:
    slug = via.replace("/", "-")
    return (
        f"{_LIBRARIUM_DEFAULT}/compare/main...main"
        f"?quick_pull=1&title=offero%3A+{slug}%40{versio}"
    )


def offero(
    root: str | Path,
    *,
    push: bool = True,
    fiat: bool = False,
) -> dict[str, str]:
    root = Path(root).resolve()
    mpath = manifest_path(root)
    manifest = load_manifest(mpath)

    if not manifest.versio:
        _bad("litania.versio is required for offero", str(mpath))
    if manifest.principium:
        _bad("projects with [canticum] cannot be offered — use a litania package",
             str(mpath))
    if _has_substitutio(mpath):
        _bad("[substitutio] must not appear in published manifests", str(mpath))

    git_root = _git_root(root)
    if git_root != root.resolve():
        _bad("offero must run from the repository root", str(mpath))

    origin = _origin_via(git_root)
    if origin != manifest.via:
        _bad(
            f"litania.via '{manifest.via}' does not match origin '{origin}'",
            str(mpath),
        )

    _validate_deps(manifest, str(mpath))
    _validate_fons(git_root)

    if _dirty(git_root):
        _bad("git working tree is dirty — commit or stash before offero", str(mpath))

    _run_proba(git_root)

    tag = _ensure_tag(git_root, manifest.versio)

    if push:
        if not fiat:
            word = input(f"Speak the word to publish {tag} (FIAT): ")
            if word.strip() != "FIAT":
                _bad("the word was not spoken — offero aborted", str(mpath))
        _push_tag(git_root, tag)

    return {
        "via": manifest.via,
        "versio": manifest.versio,
        "tag": tag,
        "librarium": librarium_pr_hint(manifest.via, manifest.versio),
        "toolchain": __version__,
    }
