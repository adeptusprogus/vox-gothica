"""gothica codex — search the Vox Gothica documentation (docs 12-cli §Hygiene)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CODEX_URL = "https://adeptusprogus.github.io/vox-gothica/"


@dataclass
class CodexHit:
    page: str
    title: str
    line: int
    excerpt: str


def _codex_roots() -> list[Path]:
    here = Path(__file__).resolve()
    roots = [
        here.parent.parent.parent / "docs",
        here.parent.parent / "docs",
        Path.cwd() / "docs",
    ]
    out: list[Path] = []
    seen: set[Path] = set()
    for r in roots:
        rp = r.resolve()
        if rp.is_dir() and rp not in seen:
            seen.add(rp)
            out.append(rp)
    return out


def _page_title(html: str, fallback: str) -> str:
    m = re.search(r"<title>([^<]+)</title>", html, re.I)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    if m:
        text = re.sub(r"<[^>]+>", "", m.group(1))
        return re.sub(r"\s+", " ", text).strip()
    return fallback


def _strip_html(line: str) -> str:
    text = re.sub(r"<[^>]+>", " ", line)
    return re.sub(r"\s+", " ", text).strip()


def quaere(term: str, *, limit: int = 20) -> list[CodexHit]:
    needle = term.casefold()
    hits: list[CodexHit] = []
    for root in _codex_roots():
        for fp in sorted(root.glob("*.html")):
            if fp.name == "heretech.html":
                continue
            text = fp.read_text(encoding="utf-8", errors="replace")
            title = _page_title(text, fp.stem)
            for i, raw in enumerate(text.splitlines(), 1):
                plain = _strip_html(raw)
                if not plain or needle not in plain.casefold():
                    continue
                hits.append(CodexHit(fp.name, title, i, plain[:160]))
                if len(hits) >= limit:
                    return hits
    return hits


def index_pages() -> list[tuple[str, str]]:
    pages: list[tuple[str, str]] = []
    for root in _codex_roots():
        for fp in sorted(root.glob("*.html")):
            if fp.name == "heretech.html":
                continue
            text = fp.read_text(encoding="utf-8", errors="replace")
            pages.append((fp.name, _page_title(text, fp.stem)))
        if pages:
            return pages
    return pages
