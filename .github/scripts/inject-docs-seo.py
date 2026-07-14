#!/usr/bin/env python3
"""Inject SEO meta tags into Codex HTML pages (idempotent)."""
from __future__ import annotations

import re
from pathlib import Path

BASE = "https://adeptusprogus.github.io/vox-gothica"
SITE_DESC = (
    "Vox Gothica — a High Gothic programming language for canticles (programs) "
    "and fabricae (Terraform infrastructure). Esolang inspired by Warhammer 40,000 "
    "Adeptus Mechanicus. Toolchain: gothica."
)
KEYWORDS = (
    "Vox Gothica, gothica, programming language, esolang, esoteric language, "
    "Warhammer 40K, Adeptus Mechanicus, High Gothic, Terraform, infrastructure as code, "
    "Python, canticle, fabrica, litania"
)

PAGE_DESC = {
    "index.html": "Codex Vox Gothica — official language specification and documentation shrine.",
    "prooemium.html": "Doctrine and design principles of Vox Gothica v0.2.",
    "01-lexical.html": "Lexica Sacra — characters, literals, Roman numerals, file seals.",
    "02-types.html": "Type system, SCHEMA records, NIHIL, equality.",
    "03-expressions.html": "Operators, precedence, interpolation.",
    "04-statements.html": "Declarations, control flow, scope.",
    "05-rites.html": "Functions, closures, anonymous rites.",
    "06-heresies.html": "Codex Hereticus — complete error taxonomy.",
    "07-modules.html": "INVOCO, modules, project layout.",
    "08-litaniae.html": "Package manager — litaniae, lockfile, registry.",
    "09-stdlib.html": "Cultus Machinae — standard library and testing.",
    "10-fabrica.html": "Fabricae — infrastructure manifests to Terraform JSON.",
    "11-grammar.html": "Formal EBNF grammar of Vox Gothica.",
    "12-cli.html": "gothica CLI commands and diagnostics.",
    "13-examples.html": "Worked canticle and fabrica examples.",
    "14-implementation.html": "Reference implementation architecture.",
    "15-glossary.html": "Keyword glossary — Latin meanings.",
}


def seo_block(path: str, title: str, desc: str) -> str:
    url = f"{BASE}/{path}" if path != "index.html" else f"{BASE}/"
    return f"""<meta name="description" content="{desc}">
<meta name="keywords" content="{KEYWORDS}">
<meta name="robots" content="index, follow">
<meta name="author" content="adeptusprogus">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Codex Vox Gothica">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="sitemap" type="application/xml" href="{BASE}/sitemap.xml">"""


def inject(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if 'name="description"' in text:
        return False
    m = re.search(r"<title>([^<]+)</title>", text)
    title = m.group(1).strip() if m else path.stem
    desc = PAGE_DESC.get(path.name, SITE_DESC)
    block = seo_block(path.name, title.replace('"', "&quot;"), desc.replace('"', "&quot;"))
    new = re.sub(
        r"(<meta name='viewport'[^>]*>)",
        r"\1\n" + block,
        text,
        count=1,
    )
    if new == text:
        new = re.sub(
            r'(<meta name="viewport"[^>]*>)',
            r"\1\n" + block,
            text,
            count=1,
        )
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    docs = Path(__file__).resolve().parents[2] / "docs"
    changed = sum(inject(p) for p in sorted(docs.glob("*.html")) if p.name != "heretech.html")
    print(f"SEO injected into {changed} pages")


if __name__ == "__main__":
    main()
