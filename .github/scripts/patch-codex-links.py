#!/usr/bin/env python3
"""Add repository/install links to all Codex HTML pages."""
from __future__ import annotations

from pathlib import Path

BANNER_NAV = """<nav class='banner-ancora'>
<a href='https://github.com/adeptusprogus/vox-gothica' rel='noopener noreferrer'>Repositorium</a>
<a href='https://github.com/adeptusprogus/vox-gothica/releases' rel='noopener noreferrer'>Releases</a>
<a href='index.html#installatio'>Installatio</a>
</nav>
"""

NAV_INSTALL = """<a class='' href='index.html#installatio'><span class='num'>⚙</span> Installatio</a>
"""

MARKER = "<span class='machina-spiritus'>"
PORTA = """<a class=' activa' href='index.html'><span class='num'>✠</span> Porta Librarii</a>"""
PORTA_INACTIVE = """<a class='' href='index.html'><span class='num'>✠</span> Porta Librarii</a>"""


def patch_banner(text: str) -> str:
    if "banner-ancora" in text:
        return text
    return text.replace(MARKER, BANNER_NAV + MARKER)


def patch_nav(text: str) -> str:
    if "transectus-installatio" in text:
        return text
    install = NAV_INSTALL.replace(
        "href='index.html#installatio'",
        "href='index.html#installatio' class='transectus-installatio'",
        1,
    )
    for porta in (PORTA, PORTA_INACTIVE):
        if porta in text:
            return text.replace(porta, porta + "\n" + install, 1)
    return text


def main() -> None:
    docs = Path(__file__).resolve().parents[2] / "docs"
    for path in sorted(docs.glob("*.html")):
        if path.name == "heretech.html":
            continue
        text = path.read_text(encoding="utf-8")
        new = patch_nav(patch_banner(text))
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"patched {path.name}")


if __name__ == "__main__":
    main()
