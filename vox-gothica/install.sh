#!/usr/bin/env bash
# Vox Gothica installer — macOS & Linux.
# Usage:  ./install.sh            (pipx/pip install, real `gothica` command)
#         ./install.sh --pyz     (single-file gothica.pyz into ~/.local/bin)
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"

say()  { printf '⚙ %s\n' "$*"; }
die()  { printf '⚙ HERESIS: %s\n' "$*" >&2; exit 1; }

find_python() {
    for p in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$p" >/dev/null 2>&1; then
            if "$p" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then
                echo "$p"; return
            fi
        fi
    done
    die "Python >= 3.10 was not found. Install it (macOS: brew install python; Debian/Ubuntu: apt install python3)."
}

PY="$(find_python)"
say "Python found: $($PY --version)"

if [[ "${1:-}" == "--pyz" ]]; then
    say "Forging single-file gothica.pyz ..."
    TMP="$(mktemp -d)"
    cp -r "$DIR/gothica" "$TMP/gothica"
    printf 'import sys\nfrom gothica.cli import main\nsys.exit(main())\n' > "$TMP/__main__.py"
    mkdir -p "$BIN_DIR"
    "$PY" -m zipapp "$TMP" -o "$BIN_DIR/gothica" -p "/usr/bin/env $PY"
    chmod +x "$BIN_DIR/gothica"
    rm -rf "$TMP"
    say "Installed: $BIN_DIR/gothica"
else
    if command -v pipx >/dev/null 2>&1; then
        say "Consecrating via pipx ..."
        pipx install --force "$DIR"
    else
        say "Consecrating via pip (--user) ..."
        "$PY" -m pip install --user --quiet --upgrade "$DIR" \
            || "$PY" -m pip install --user --quiet --upgrade --break-system-packages "$DIR"
    fi
fi

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) say "NOTE: add $BIN_DIR to PATH:  export PATH=\"\$PATH:$BIN_DIR\"" ;;
esac

command -v gothica >/dev/null 2>&1 && gothica versio \
    || say 'Done. Open a new shell and run: gothica versio'
say "For fabricae you also need terraform (or use the Docker image)."
say "The Machine Spirit is appeased."
