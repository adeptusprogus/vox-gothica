"""gothica librarium — index search and inspection (08-litaniae §7, M4)."""
from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

from ..heresiae import Profanatio
from .adfero import _git_url
from .offero import _LIBRARIUM_DEFAULT

_DEFAULT_MIRROR = "github.com/vox-gothica/librarium-sanctum"
_CACHE_TTL = 86_400  # 24h
_GITHUB_VIA = re.compile(r"^github\.com/([^/]+)/([^/]+)(?:/v(\d+))?$")
_BUNDLED = Path(__file__).resolve().parent / "indicium"


@dataclass
class IndexEntry:
    via: str
    descriptio: str | None = None
    licentia: str | None = None
    alia: list[str] = field(default_factory=list)
    excommunicatae: dict[str, str] = field(default_factory=dict)
    source: str = "bundled"


def _bad(msg: str) -> None:
    raise Profanatio("P-XIV", "librarium_innotum", msg, "librarium", 0)


def _config_path() -> Path:
    return Path.home() / ".gothica" / "configuratio.toml"


def _cache_root() -> Path:
    return Path.home() / ".gothica" / "librarium-cache"


def mirror_vias() -> list[str]:
    """Configured librarium mirrors; first match wins for lookups."""
    mirrors = [_DEFAULT_MIRROR]
    cfg = _config_path()
    if cfg.is_file():
        try:
            with cfg.open("rb") as fh:
                data = tomllib.load(fh)
        except Exception:
            return mirrors
        block = data.get("librarium")
        if isinstance(block, dict):
            raw = block.get("mirrors")
            if isinstance(raw, list) and all(isinstance(m, str) for m in raw):
                mirrors = raw
    return mirrors


def _mirror_git_url(mirror_via: str) -> str:
    m = _GITHUB_VIA.match(mirror_via)
    if not m:
        _bad(f"mirror '{mirror_via}' is not a github.com/owner/repo via")
    return f"https://github.com/{m.group(1)}/{m.group(2)}.git"


def _cache_dir(mirror_via: str) -> Path:
    slug = mirror_via.replace("/", "__")
    return _cache_root() / slug


def sync_mirror(mirror_via: str, *, refresh: bool = False) -> Path | None:
    """Clone or refresh a librarium mirror. Returns cache path or None on failure."""
    cache = _cache_dir(mirror_via)
    url = _mirror_git_url(mirror_via)
    try:
        if cache.exists():
            stamp = cache / ".gothica-sync"
            if not refresh and stamp.is_file():
                age = time.time() - stamp.stat().st_mtime
                if age < _CACHE_TTL:
                    return cache
            proc = subprocess.run(
                ["git", "fetch", "--depth", "1", "origin", "HEAD"],
                cwd=cache, capture_output=True, text=True, timeout=90,
            )
            if proc.returncode != 0:
                return None
            subprocess.run(
                ["git", "reset", "--hard", "FETCH_HEAD"],
                cwd=cache, capture_output=True, text=True, timeout=30, check=False,
            )
        else:
            cache.parent.mkdir(parents=True, exist_ok=True)
            proc = subprocess.run(
                ["git", "clone", "--depth", "1", url, str(cache)],
                capture_output=True, text=True, timeout=120,
            )
            if proc.returncode != 0:
                return None
        (cache / ".gothica-sync").write_text(str(time.time()), encoding="utf-8")
        return cache
    except (OSError, subprocess.TimeoutExpired):
        return None


def _parse_entry(data: dict, source: str) -> IndexEntry | None:
    via = data.get("via")
    if not isinstance(via, str) or not via:
        return None
    alia = data.get("alia") or []
    if not isinstance(alia, list) or not all(isinstance(a, str) for a in alia):
        alia = []
    excom: dict[str, str] = {}
    block = data.get("excommunicatae")
    if isinstance(block, dict):
        for ver, note in block.items():
            if isinstance(ver, str) and isinstance(note, str):
                excom[ver] = note
    return IndexEntry(
        via=via,
        descriptio=data.get("descriptio") if isinstance(data.get("descriptio"), str) else None,
        licentia=data.get("licentia") if isinstance(data.get("licentia"), str) else None,
        alia=list(alia),
        excommunicatae=excom,
        source=source,
    )


def _load_index_dir(index_dir: Path, source: str) -> dict[str, IndexEntry]:
    out: dict[str, IndexEntry] = {}
    if not index_dir.is_dir():
        return out
    for path in sorted(index_dir.glob("*.toml")):
        try:
            with path.open("rb") as fh:
                data = tomllib.load(fh)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        entry = _parse_entry(data, source)
        if entry:
            out[entry.via] = entry
    return out


def load_catalog(*, refresh: bool = False) -> dict[str, IndexEntry]:
    """Merge index entries from mirrors (first wins) then bundled fallback."""
    catalog: dict[str, IndexEntry] = {}
    for mirror in mirror_vias():
        cache = sync_mirror(mirror, refresh=refresh)
        if cache:
            remote = _load_index_dir(cache / "index", mirror)
            for via, entry in remote.items():
                catalog.setdefault(via, entry)
    bundled = _load_index_dir(_BUNDLED, "bundled")
    for via, entry in bundled.items():
        catalog.setdefault(via, entry)
    return catalog


def _haystack(entry: IndexEntry) -> str:
    parts = [entry.via, entry.descriptio or "", *entry.alia]
    return " ".join(parts).lower()


def quaere(term: str, *, refresh: bool = False) -> list[IndexEntry]:
    needle = term.strip().lower()
    if not needle:
        _bad("search term is empty")
    hits = [
        e for e in load_catalog(refresh=refresh).values()
        if needle in _haystack(e)
    ]
    hits.sort(key=lambda e: e.via)
    return hits


def _list_tags(via: str, *, limit: int = 24) -> list[str]:
    if not _GITHUB_VIA.match(via):
        return []
    url = _git_url(via)
    try:
        proc = subprocess.run(
            ["git", "ls-remote", "--tags", url],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if proc.returncode != 0:
        return []
    tags: list[str] = []
    for line in proc.stdout.splitlines():
        if "^{}" in line:
            continue
        if "\trefs/tags/" not in line:
            continue
        tag = line.split("\trefs/tags/")[-1].lstrip("v")
        if tag and tag not in tags:
            tags.append(tag)
    def _key(v: str) -> tuple:
        parts = []
        for p in re.split(r"[.-]", v):
            try:
                parts.append((0, int(p)))
            except ValueError:
                parts.append((1, p))
        return tuple(parts)

    tags.sort(key=_key, reverse=True)
    return tags[:limit]


def inspice(via: str, *, refresh: bool = False) -> dict:
    via = via.strip()
    if not via:
        _bad("via is required")
    catalog = load_catalog(refresh=refresh)
    entry = catalog.get(via)
    tags = _list_tags(via)
    return {
        "via": via,
        "entry": entry,
        "versiones": tags,
        "librarium": _LIBRARIUM_DEFAULT,
        "indexed": entry is not None,
    }


def format_quaere_line(entry: IndexEntry) -> str:
    desc = entry.descriptio or "(no descriptio)"
    return f"  {entry.via:<44} {desc}"


def format_inspice(data: dict) -> str:
    via = data["via"]
    entry: IndexEntry | None = data["entry"]
    lines = [f"++ inspice — {via} ++"]
    if entry is None:
        lines.append("  (not in Librarium index — showing remote tags only)")
    else:
        if entry.descriptio:
            lines.append(f"  descriptio: {entry.descriptio}")
        if entry.licentia:
            lines.append(f"  licentia:   {entry.licentia}")
        if entry.alia:
            lines.append(f"  alia:       {', '.join(entry.alia)}")
        lines.append(f"  index:      {entry.source}")
        if entry.excommunicatae:
            lines.append("  excommunicatae:")
            for ver, note in sorted(entry.excommunicatae.items()):
                lines.append(f"    {ver} — {note}")
    vers = data["versiones"]
    if vers:
        preview = ", ".join(vers[:8])
        extra = f" (+{len(vers) - 8} more)" if len(vers) > 8 else ""
        lines.append(f"  tags:       {preview}{extra}")
    else:
        lines.append("  tags:       (none reachable)")
    lines.append(f"  librarium:  {data['librarium']}")
    return "\n".join(lines)
