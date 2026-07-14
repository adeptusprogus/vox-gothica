#!/usr/bin/env python3
"""Normalize SEO/meta tags so every Codex page names Vox Gothica explicitly."""
from __future__ import annotations

import re
from pathlib import Path

BASE = "https://adeptusprogus.github.io/vox-gothica"
KEYWORDS = (
    "Vox Gothica, vox-gothica, vox gothica language, gothica, gothica programming language, "
    "programming language, esolang, esoteric language, Warhammer 40K, Adeptus Mechanicus, "
    "High Gothic, Terraform, infrastructure as code, canticle, fabrica, litania, Adeptus Mechanicus language"
)

PAGES: dict[str, tuple[str, str]] = {
    "index.html": (
        "Vox Gothica — Codex & Librarium Sanctum",
        "Vox Gothica — official specification of the High Gothic programming language for canticles and fabricae.",
    ),
    "prooemium.html": (
        "Vox Gothica — Prooemium (Doctrine)",
        "Vox Gothica — design principles, execution modes, and conformance doctrine.",
    ),
    "01-lexical.html": (
        "Vox Gothica — Lexica Sacra",
        "Vox Gothica — characters, comments, identifiers, keywords, Roman numerals, file seals.",
    ),
    "02-types.html": (
        "Vox Gothica — Typi et Valores",
        "Vox Gothica — type system, SCHEMA records, NIHIL, equality, conversions.",
    ),
    "03-expressions.html": (
        "Vox Gothica — Expressiones",
        "Vox Gothica — operators, precedence, evaluation order, interpolation.",
    ),
    "04-statements.html": (
        "Vox Gothica — Sententiae",
        "Vox Gothica — declarations, FIAT, control flow, scope, entry point.",
    ),
    "05-rites.html": (
        "Vox Gothica — Ritus",
        "Vox Gothica — functions, closures, anonymous rites, recursion.",
    ),
    "06-heresies.html": (
        "Vox Gothica — Codex Hereticus",
        "Vox Gothica — complete normative error taxonomy (heresies and profanatio).",
    ),
    "07-modules.html": (
        "Vox Gothica — Moduli",
        "Vox Gothica — INVOCO imports, visibility, resolution order, project layout.",
    ),
    "08-litaniae.html": (
        "Vox Gothica — Litaniae",
        "Vox Gothica — package manager: litaniae, lockfile, Librarium registry.",
    ),
    "09-stdlib.html": (
        "Vox Gothica — Cultus Machinae",
        "Vox Gothica — standard library, built-in prayers, and test runner.",
    ),
    "10-fabrica.html": (
        "Vox Gothica — Fabrica",
        "Vox Gothica — infrastructure manifests that transpile to Terraform JSON.",
    ),
    "11-grammar.html": (
        "Vox Gothica — Grammatica Formalis",
        "Vox Gothica — complete formal EBNF grammar.",
    ),
    "12-cli.html": (
        "Vox Gothica — Mandata (CLI)",
        "Vox Gothica — gothica toolchain commands, diagnostics, exit codes.",
    ),
    "13-examples.html": (
        "Vox Gothica — Exempla Sancta",
        "Vox Gothica — complete worked canticle and fabrica examples.",
    ),
    "14-implementation.html": (
        "Vox Gothica — Instrumenta",
        "Vox Gothica — reference implementation architecture and milestones.",
    ),
    "15-glossary.html": (
        "Vox Gothica — Glossarium",
        "Vox Gothica — keyword glossary with Latin meanings.",
    ),
}

APP_META = """<meta name="application-name" content="Vox Gothica">
<meta name="apple-mobile-web-app-title" content="Vox Gothica">
<meta name="language" content="English">
"""


def patch_file(path: Path, title: str, desc: str) -> None:
    text = path.read_text(encoding="utf-8")
    url = f"{BASE}/{path.name}" if path.name != "index.html" else f"{BASE}/"
    esc_t, esc_d = title.replace('"', "&quot;"), desc.replace('"', "&quot;")

    text = re.sub(r"<title>[^<]*</title>", f"<title>{title}</title>", text)
    text = re.sub(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{esc_d}"', text)
    text = re.sub(r'<meta name="keywords" content="[^"]*"', f'<meta name="keywords" content="{KEYWORDS}"', text)
    text = re.sub(r'<meta property="og:title" content="[^"]*"', f'<meta property="og:title" content="{esc_t}"', text)
    text = re.sub(r'<meta property="og:description" content="[^"]*"', f'<meta property="og:description" content="{esc_d}"', text)
    text = re.sub(r'<meta property="og:site_name" content="[^"]*"', '<meta property="og:site_name" content="Vox Gothica"', text)
    text = re.sub(r'<meta name="twitter:title" content="[^"]*"', f'<meta name="twitter:title" content="{esc_t}"', text)
    text = re.sub(r'<meta name="twitter:description" content="[^"]*"', f'<meta name="twitter:description" content="{esc_d}"', text)
    text = re.sub(r'<link rel="canonical" href="[^"]*"', f'<link rel="canonical" href="{url}"', text)
    text = re.sub(r'<meta property="og:url" content="[^"]*"', f'<meta property="og:url" content="{url}"', text)

    if 'name="application-name"' not in text:
        text = re.sub(
            r'(<meta name="keywords" content="[^"]*">)',
            r"\1\n" + APP_META,
            text,
            count=1,
        )

    path.write_text(text, encoding="utf-8")


def patch_json_ld_index(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    new_ld = (
        '{"@context":"https://schema.org","@type":"SoftwareSourceCode",'
        '"name":"Vox Gothica","alternateName":["vox-gothica","gothica"],'
        '"description":"High Gothic programming language for canticles and Terraform fabricae",'
        '"codeRepository":"https://github.com/adeptusprogus/vox-gothica",'
        '"image":"https://adeptusprogus.github.io/vox-gothica/heraldry.png",'
        '"programmingLanguage":["Vox Gothica","Python"],'
        '"license":"https://spdx.org/licenses/GPL-3.0-only.html",'
        '"keywords":["Vox Gothica","vox-gothica","gothica","esolang","Warhammer 40K","Terraform","Adeptus Mechanicus"]}'
    )
    text = re.sub(r"<script type=\"application/ld\+json\">.*?</script>", f"<script type=\"application/ld+json\">\n{new_ld}\n</script>", text, flags=re.DOTALL)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    docs = Path(__file__).resolve().parents[2] / "docs"
    for name, (title, desc) in PAGES.items():
        patch_file(docs / name, title, desc)
        print(f"tags: {name}")
    patch_json_ld_index(docs / "index.html")


if __name__ == "__main__":
    main()
