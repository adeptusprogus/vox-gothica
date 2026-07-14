#!/usr/bin/env python3
"""Inject favicon and og:image into Codex HTML pages."""
from __future__ import annotations

import re
from pathlib import Path

BASE = "https://adeptusprogus.github.io/vox-gothica"
MARKER = 'rel="icon"'
HEAD = f"""<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="heraldry.png" type="image/png" sizes="512x512">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:image" content="{BASE}/og-image.png">
<meta name="twitter:image" content="{BASE}/og-image.png">
"""


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    new = re.sub(
        r"(<meta name='viewport'[^>]*>)",
        r"\1\n" + HEAD,
        text,
        count=1,
    )
    if new == text:
        new = re.sub(
            r'(<meta name="viewport"[^>]*>)',
            r"\1\n" + HEAD,
            text,
            count=1,
        )
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    docs = Path(__file__).resolve().parents[2] / "docs"
    n = sum(patch(p) for p in sorted(docs.glob("*.html")) if p.name != "heretech.html")
    print(f"favicon injected into {n} pages")


if __name__ == "__main__":
    main()
