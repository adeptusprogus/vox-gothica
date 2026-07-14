#!/usr/bin/env bash
# Vox Gothica installer — macOS & Linux.
#
# Default: download pre-built binary from GitHub Releases (no Python).
#
#   curl -fsSL https://raw.githubusercontent.com/adeptusprogus/vox-gothica/main/vox-gothica/install.sh | bash
#
# Options:
#   --version v0.2.0   specific release (default: latest)
#   --from-source      build via pip/pipx (needs Python 3.10+)
#   --pyz              zipapp into ~/.local/bin (needs Python 3.10+)
set -euo pipefail

REPO="adeptusprogus/vox-gothica"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
VERSION=""
FROM_SOURCE=0
PYZ=0

say()  { printf '⚙ %s\n' "$*"; }
die()  { printf '⚙ HERESIS: %s\n' "$*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --version) VERSION="$2"; shift 2 ;;
        --from-source) FROM_SOURCE=1; shift ;;
        --pyz) PYZ=1; shift ;;
        -h|--help)
            sed -n '2,12p' "$0"
            exit 0
            ;;
        *) die "Unknown option: $1 (try --help)" ;;
    esac
done

find_python() {
    for p in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$p" >/dev/null 2>&1; then
            if "$p" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then
                echo "$p"; return
            fi
        fi
    done
    die "Python >= 3.10 was not found."
}

detect_asset() {
    local os arch
    os="$(uname -s)"
    arch="$(uname -m)"
    case "$os" in
        Darwin)
            case "$arch" in
                arm64)  echo "gothica-darwin-arm64" ;;
                x86_64) echo "gothica-darwin-amd64" ;;
                *) die "Unsupported macOS architecture: $arch" ;;
            esac ;;
        Linux)
            case "$arch" in
                x86_64|amd64) echo "gothica-linux-amd64" ;;
                *) die "Unsupported Linux architecture: $arch (build from source with --from-source)" ;;
            esac ;;
        *)
            die "Unsupported OS: $os — use install.ps1 on Windows"
            ;;
    esac
}

resolve_version() {
    if [[ -n "$VERSION" ]]; then
        echo "$VERSION"
        return
    fi
    local tag
    tag="$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
        | sed -n 's/.*"tag_name": *"\([^"]*\)".*/\1/p' | head -1)"
    [[ -n "$tag" ]] || die "Could not resolve latest release from GitHub."
    echo "$tag"
}

install_binary() {
    local tag asset url tmp
    tag="$(resolve_version)"
    asset="$(detect_asset)"
    url="https://github.com/${REPO}/releases/download/${tag}/${asset}"
    say "Fetching ${tag} → ${asset} ..."
    mkdir -p "$BIN_DIR"
    tmp="$(mktemp)"
    curl -fsSL "$url" -o "$tmp"
    chmod +x "$tmp"
    mv "$tmp" "$BIN_DIR/gothica"
    say "Installed: $BIN_DIR/gothica (${tag})"
}

install_from_source() {
    local PY
    PY="$(find_python)"
    say "Python found: $($PY --version)"
    if command -v pipx >/dev/null 2>&1; then
        say "Consecrating via pipx ..."
        pipx install --force "$DIR"
    else
        say "Consecrating via pip (--user) ..."
        "$PY" -m pip install --user --quiet --upgrade "$DIR" \
            || "$PY" -m pip install --user --quiet --upgrade --break-system-packages "$DIR"
    fi
}

install_pyz() {
    local PY
    PY="$(find_python)"
    say "Python found: $($PY --version)"
    say "Forging single-file gothica.pyz ..."
    local TMP
    TMP="$(mktemp -d)"
    cp -r "$DIR/gothica" "$TMP/gothica"
    printf 'import sys\nfrom gothica.cli import main\nsys.exit(main())\n' > "$TMP/__main__.py"
    mkdir -p "$BIN_DIR"
    "$PY" -m zipapp "$TMP" -o "$BIN_DIR/gothica" -p "/usr/bin/env $PY"
    chmod +x "$BIN_DIR/gothica"
    rm -rf "$TMP"
    say "Installed: $BIN_DIR/gothica (zipapp)"
}

# --- main rite ---
if [[ "$FROM_SOURCE" -eq 1 ]]; then
    install_from_source
elif [[ "$PYZ" -eq 1 ]]; then
    install_pyz
else
    if ! command -v curl >/dev/null 2>&1; then
        die "curl is required for binary install. Install curl or use --from-source."
    fi
    install_binary
fi

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) say "NOTE: add $BIN_DIR to PATH:  export PATH=\"\$PATH:$BIN_DIR\"" ;;
esac

if command -v gothica >/dev/null 2>&1; then
    gothica versio
else
    say "Done. Open a new shell and run: gothica versio"
fi

say "For fabricae you also need terraform (or use the Docker image)."
say "The Machine Spirit is appeased."
